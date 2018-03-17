Object serialization
====================

Mitogen supports calling arbitrary Python code on slaves, and returning the
results to the caller on the master. To do this the results must be

1. serialized to a byte stream
2. sent over a channel
3. deserialized back to Python objects

Currently this is implemented with `cPickle`, restricted to a whitelist of
types/classes. However a replacement is sought.

The following principals/requirements must be met

1. data from slaves is considered untrusted by the master, deserializing it
   must not enable code execution on the master
2. native types (e.g. ``list``, ``tuple``, ``set``, ``bytes``) are preserved
3. data structures that reference themself are preserved
4. data serialized on a newer version of Python must be deserialisable on an
   earlier version
5. data serialized on a particular architecture (e.g. x86_64) must be
   deserializable on another architecture (e.g. ARM)
6. compatible with Python 2.4+
7. pure Python implementation

The following features are desirable

1. minimal code footprint, or inclusion in Python 2.4+ stdlib
2. implementation in a single file, or ability to minify into one
3. support for custom types/classes, on an opt-in or whitelisted basis
4. serialization rate comparable to `cPickle`
5. deserialization rate comparable to `cPickle`
6. serialized size comparable to `pickle`/`cPickle`
7. API compatiblity with `pickle`, to allow pluggable backends

The following are _not_ requirements

1. compatibility with languages or runtimes other than Python;
   Mitogen spawns every child, so we can rely on Python being available
2. forward or backward compatibility between versions of Mitogen;
   serialized objects only live as long as the Mitogen master process

Survey
------

Possible replacements were searched for on PyPI and the Web. Candidates were
assessed based on the requirements, and a shortlist chosen for further
investigation

- Cerealizer
- Chopsticks pencode
- Gnosis_utils XML Pickler
- Safepickle

Benchmarks were run to compare serialization/deserialisation performance

::

    $ python benchmark_pickles.py
    .....................
    pickle/2 dumps: Mean +- std dev: 12.2 ms +- 0.4 ms
    .....................
    pickle/2 loads: Mean +- std dev: 8.37 ms +- 0.27 ms
    .....................
    cerealizer dumps: Mean +- std dev: 115 ms +- 1 ms
    .....................
    cerealizer loads: Mean +- std dev: 99.7 ms +- 2.4 ms
    .....................
    chopsticks.pencode dumps: Mean +- std dev: 46.7 ms +- 1.9 ms
    .....................
    chopsticks.pencode loads: Mean +- std dev: 134 ms +- 5 ms
    .....................
    safepickle dumps: Mean +- std dev: 83.9 ms +- 2.5 ms
    .....................
    safepickle loads: Mean +- std dev: 40.2 ms +- 1.5 ms

Gnosis XML Pickler did not successfully complete the benchmark.
