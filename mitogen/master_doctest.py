import os
import string
import sys


SPECIAL_FILE_PATHS = {
    "__synthetic__",
    "<ansible_synthetic_collection_package>"
}


def _looks_like_script(path):
    """
    Return :data:`True` if the (possibly extensionless) file at `path`
    resembles a Python script. For now we simply verify the file contains
    ASCII text.
    """
    try:
        fp = open(path, 'rb')
    except IOError:
        e = sys.exc_info()[1]
        if e.args[0] == errno.EISDIR:
            return False
        raise

    try:
        sample = fp.read(512).decode('latin-1')
        return not set(sample).difference(string.printable)
    finally:
        fp.close()


def _py_filename(path):
    r"""
    >>> _py_filename(None), _py_filename(''), _py_filename('doesnotexist')
    (None, None, None)

    >>> _py_filename('x.py'), _py_filename('y.pyc'), _py_filename('z.pyo')
    ('x.py', 'y.py', 'z.py')

    >>> with open('/tmp/foo', 'w') as f: f.write('import foo\nfoo.bar()\n')
    >>> _py_filename('/tmp/foo')
    '/tmp/foo'

    >>> with open('/tmp/quux', 'wb') as f: f.write(b'\xff'*100)
    >>> with open('/tmp/empty', 'w') as f: pass
    >>> _py_filename('/tmp/quux'), _py_filename('/tmp/empty')
    (None, '/tmp/empty')

    """
    if not path:
        return None

    if path[-4:] in ('.pyc', '.pyo'):
        path = path.rstrip('co')

    if path.endswith('.py'):
        return path

    if os.path.exists(path) and _looks_like_script(path):
        return path


def _py_filename2(path):
    r"""
    Returns a tuple of a Python path (if the file looks Pythonic) and whether or not
    the Python path is special. Special file paths/modules might only exist in memory

    >>> _py_filename2(None), _py_filename2(''), _py_filename2('doesnotexist')
    ((None, False), (None, False), (None, False))

    >>> _py_filename2('x.py'), _py_filename2('y.pyc'), _py_filename2('z.pyo')
    (('x.py', False), ('y.py', False), ('z.py', False))

    >>> with open('/tmp/foo', 'w') as f: f.write('import foo\foo.bar()\n')
    >>> _py_filename2('/tmp/foo')
    ('/tmp/foo', False)

    >>> with open('/tmp/quux', 'wb') as f: f.write(b'\xff'*100)
    >>> with open('/tmp/empty', 'w') as f: pass
    >>> _py_filename2('/tmp/quux'), _py_filename2('/tmp/empty')
    ((None, False), ('/tmp/empty', False))

    >>> _py_filename2('__synthetic__')
    ('__synthetic__', True)
    """
    if not path:
        return None, False

    if path[-4:] in ('.pyc', '.pyo'):
        path = path.rstrip('co')

    if path.endswith('.py'):
        return path, False

    if os.path.exists(path) and _looks_like_script(path):
        return path, False

    basepath = os.path.basename(path)
    if basepath in SPECIAL_FILE_PATHS:
        return path, True

    return None, False


if __name__ == '__main__':
    import doctest
    print(doctest.testmod())
