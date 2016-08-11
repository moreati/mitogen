
import commands
import getpass
import inspect
import logging
import os
import pkgutil
import re
import socket
import sys
import textwrap
import zlib

import econtext.core


LOG = logging.getLogger('econtext')
IOLOG = logging.getLogger('econtext.io')
RLOG = logging.getLogger('econtext.ctx')

DOCSTRING_RE = re.compile(r'""".+?"""', re.M | re.S)
COMMENT_RE = re.compile(r'^\s*#.*$', re.M)


def minimize_source(source):
    """Remove comments and docstrings from Python `source`, preserving line
    numbers and syntax of empty blocks."""
    subber = lambda match: '""' + ('\n' * match.group(0).count('\n'))
    source = DOCSTRING_RE.sub(subber, source)
    source = COMMENT_RE.sub('\n', source)
    return source.replace('    ', '\t')


def get_child_modules(module, prefix):
    """Return the canonical names of all submodules of a package `module`."""
    it = pkgutil.iter_modules(module.__path__, prefix)
    return [name for _, name, _ in it]


def create_child(*args):
    """Create a child process whose stdin/stdout is connected to a socket,
    returning `(pid, socket_obj)`."""
    parentfp, childfp = socket.socketpair()
    pid = os.fork()
    if not pid:
        os.dup2(childfp.fileno(), 0)
        os.dup2(childfp.fileno(), 1)
        childfp.close()
        parentfp.close()
        os.execvp(args[0], args)
        raise SystemExit

    childfp.close()
    LOG.debug('create_child() child %d fd %d, parent %d, args %r',
              pid, parentfp.fileno(), os.getpid(), args)
    return pid, parentfp


class Listener(econtext.core.BasicStream):
    def __init__(self, broker, address=None, backlog=30):
        self._broker = broker
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind(address or ('0.0.0.0', 0))
        self._sock.listen(backlog)
        econtext.core.set_cloexec(self._sock.fileno())
        self._listen_addr = self._sock.getsockname()
        self.read_side = econtext.core.Side(self, self._sock.fileno())
        broker.update_stream(self)

    def on_receive(self):
        sock, addr = self._sock.accept()
        context = Context(self._broker, name=addr)
        stream = econtext.core.Stream(context)
        stream.accept(sock.fileno(), sock.fileno())


class LogForwarder(object):
    def __init__(self, context):
        self._context = context
        self._context.add_handle_cb(self.forward_log,
                                    handle=econtext.core.FORWARD_LOG)
        self._log = RLOG.getChild(self._context.name)

    def forward_log(self, data):
        if data == econtext.core._DEAD:
            return

        name, level, s = data
        self._log.log(level, '%s: %s', name, s)


class ModuleResponder(object):
    def __init__(self, context):
        self._context = context
        self._context.add_handle_cb(self.get_module,
                                    handle=econtext.core.GET_MODULE)

    def get_module(self, data):
        if data == econtext.core._DEAD:
            return

        reply_to, fullname = data
        LOG.debug('get_module(%r, %r)', reply_to, fullname)
        try:
            module = __import__(fullname, fromlist=[''])
            is_pkg = getattr(module, '__path__', None) is not None
            path = inspect.getsourcefile(module)
            try:
                source = inspect.getsource(module)
            except IOError:
                if not is_pkg:
                    raise
                source = '\n'

            if is_pkg:
                prefix = module.__name__ + '.'
                present = get_child_modules(module, prefix)
            else:
                present = None

            compressed = zlib.compress(minimize_source(source))
            reply = (is_pkg, present, path, compressed)
            self._context.enqueue(reply_to, reply)
        except Exception:
            LOG.debug('While importing %r', fullname, exc_info=True)
            self._context.enqueue(reply_to, None)


class LocalStream(econtext.core.Stream):
    """
    Base for streams capable of starting new slaves.
    """
    #: The path to the remote Python interpreter.
    python_path = 'python'

    def __init__(self, context):
        super(LocalStream, self).__init__(context)
        self._permitted_classes = set([('econtext.core', 'CallError')])

    def shutdown(self):
        """Requesting the slave gracefully shut itself down."""
        LOG.debug('%r enqueuing SHUTDOWN', self)
        self.enqueue(econtext.core.SHUTDOWN, None)

    def _find_global(self, module_name, class_name):
        """Return the class implementing `module_name.class_name` or raise
        `StreamError` if the module is not whitelisted."""
        if (module_name, class_name) not in self._permitted_classes:
            raise econtext.core.StreamError(
                '%r attempted to unpickle %r in module %r',
                self._context, class_name, module_name)
        return getattr(sys.modules[module_name], class_name)

    def allow_class(self, module_name, class_name):
        """Add `module_name` to the list of permitted modules."""
        self._permitted_modules.add((module_name, class_name))

    # base64'd and passed to 'python -c'. It forks, dups 0->100, creates a
    # pipe, then execs a new interpreter with a custom argv. CONTEXT_NAME is
    # replaced with the context name. Optimized for size.
    def _first_stage():
        import os,sys,zlib
        R,W=os.pipe()
        if os.fork():
            os.dup2(0,100)
            os.dup2(R,0)
            os.close(R)
            os.close(W)
            os.execv(sys.executable,('econtext:'+CONTEXT_NAME,))
        else:
            os.fdopen(W,'wb',0).write(zlib.decompress(sys.stdin.read(input())))
            print 'OK'
            sys.exit(0)

    def get_boot_command(self):
        name = self._context.remote_name
        if name is None:
            name = '%s@%s:%d'
            name %= (getpass.getuser(), socket.gethostname(), os.getpid())

        source = inspect.getsource(self._first_stage)
        source = textwrap.dedent('\n'.join(source.strip().split('\n')[1:]))
        source = source.replace('    ', '\t')
        source = source.replace('CONTEXT_NAME', repr(name))
        encoded = source.encode('base64').replace('\n', '')
        return [self.python_path, '-c',
                'exec "%s".decode("base64")' % (encoded,)]

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self._context)

    def get_preamble(self):
        source = inspect.getsource(econtext.core)
        source += '\nExternalContext().main%r\n' % ((
            self._context.key,
            LOG.level or logging.getLogger().level or logging.INFO,
        ),)

        compressed = zlib.compress(minimize_source(source))
        return str(len(compressed)) + '\n' + compressed

    def connect(self):
        LOG.debug('%r.connect()', self)
        pid, sock = create_child(*self.get_boot_command())
        self.read_side = econtext.core.Side(self, os.dup(sock.fileno()))
        self.write_side = econtext.core.Side(self, os.dup(sock.fileno()))
        sock.close()
        LOG.debug('%r.connect(): child process stdin/stdout=%r',
                  self, self.read_side.fd)

        econtext.core.write_all(self.write_side.fd, self.get_preamble())
        s = os.read(self.read_side.fd, 4096)
        if s != 'OK\n':
            raise econtext.core.StreamError('Bootstrap failed; stdout: %r', s)


class SSHStream(LocalStream):
    #: The path to the SSH binary.
    ssh_path = 'ssh'

    def get_boot_command(self):
        bits = [self.ssh_path]
        if self._context.username:
            bits += ['-l', self._context.username]
        bits.append(self._context.hostname)
        base = super(SSHStream, self).get_boot_command()
        return bits + map(commands.mkarg, base)


class Broker(econtext.core.Broker):
    #: Always allow time for slaves to drain.
    graceful_count = 1

    def create_listener(self, address=None, backlog=30):
        """Listen on `address `for connections from newly spawned contexts."""
        self._listener = Listener(self, address, backlog)

    def get_local(self, name='default', python_path=None):
        """Get the named context running on the local machine, creating it if
        it does not exist."""
        context = Context(self, name)
        context.stream = LocalStream(context)
        if python_path:
            context.stream.python_path = python_path
        context.stream.connect()
        return self.register(context)

    def get_remote(self, hostname, username, name=None, python_path=None):
        """Get the named remote context, creating it if it does not exist."""
        if name is None:
            name = hostname

        context = Context(self, name, hostname, username)
        context.stream = SSHStream(context)
        if python_path:
            context.stream.python_path = python_path
        context.stream.connect()
        return self.register(context)


class Context(econtext.core.Context):
    def __init__(self, *args, **kwargs):
        super(Context, self).__init__(*args, **kwargs)
        self.responder = ModuleResponder(self)
        self.log_forwarder = LogForwarder(self)

    def on_disconnect(self):
        self.stream = None
