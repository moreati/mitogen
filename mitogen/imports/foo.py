from __future__ import print_function
import io
import sys

import mitogen.imports

def str_find_nth(s:str, sub:str, n:int, start=None, end=None):
    if n < 0: raise ValueError('n must be a non-negative integer')
    for _ in range(n): start = s.find(sub, start, end)
    return start

def str_index_nth(s:str, sub:str, n:int, start=None, end=None):
    if n < 0: raise ValueError('n must be a non-negative integer')
    for _ in range(n): start = s.index(sub, start, end)
    return start

def str_rfind_iter(s:str, sub:str, start=None, end=None):
    while True:
        pos = s.rfind(sub, start, end)
        if pos < 0: break
        yield pos
        end = pos

def str_rfind_nth(s:str, sub:str, n:int, start=None, end=None):
    if n < 0: raise ValueError('n must be a non-negative integer')
    for _ in range(n): end = s.rfind(sub, start, end)
    return end

def str_rindex_nth(s:str, sub:str, n:int, start=None, end=None):
    if n < 0: raise ValueError('n must be a non-negative integer')
    for _ in range(n): end = s.rindex(sub, start, end)
    return end

def fullname_prefix_whileloop(fullname:str, strip:int):
    pos = None
    while strip > 0:
        pos = fullname.rfind('.', None, pos)
        if pos == -1: break
        strip -= 1
    else:
        return fullname[:pos]
    if strip == 1:
        return ''
    raise ValueError

def test_fullname_prefix_whileloop():
    import pytest
    assert fullname_prefix_whileloop('foo', 0) == 'foo'
    assert fullname_prefix_whileloop('foo.bar', 0) == 'foo.bar'
    assert fullname_prefix_whileloop('foo.bar.baz', 0) == 'foo.bar.baz'

    assert fullname_prefix_whileloop('foo', 1) == ''
    assert fullname_prefix_whileloop('foo.bar', 1) == 'foo'
    assert fullname_prefix_whileloop('foo.bar.baz', 1) == 'foo.bar'

    assert fullname_prefix_whileloop('foo.bar', 2) == ''
    assert fullname_prefix_whileloop('foo.bar.baz', 2) == 'foo'

    assert fullname_prefix_whileloop('foo.bar.baz', 3) == ''

    assert pytest.raises(ValueError, fullname_prefix_whileloop, 'foo', 2)
    assert pytest.raises(ValueError, fullname_prefix_whileloop, 'foo', 3)
    assert pytest.raises(ValueError, fullname_prefix_whileloop, 'foo.bar', 3)
    assert pytest.raises(ValueError, fullname_prefix_whileloop, 'foo.bar', 4)
    assert pytest.raises(ValueError, fullname_prefix_whileloop, 'foo.bar.baz', 4)

def test_fullname_prefix():
    import pytest
    assert mitogen.imports.fullname_prefix('foo', 0) == 'foo'
    assert mitogen.imports.fullname_prefix('foo.bar', 0) == 'foo.bar'
    assert mitogen.imports.fullname_prefix('foo.bar.baz', 0) == 'foo.bar.baz'

    assert mitogen.imports.fullname_prefix('foo', 1) == ''
    assert mitogen.imports.fullname_prefix('foo.bar', 1) == 'foo'
    assert mitogen.imports.fullname_prefix('foo.bar.baz', 1) == 'foo.bar'

    assert mitogen.imports.fullname_prefix('foo.bar', 2) == ''
    assert mitogen.imports.fullname_prefix('foo.bar.baz', 2) == 'foo'

    assert mitogen.imports.fullname_prefix('foo.bar.baz', 3) == ''

    assert pytest.raises(ValueError, mitogen.imports.fullname_prefix, 'foo', 2)
    assert pytest.raises(ValueError, mitogen.imports.fullname_prefix, 'foo', 3)
    assert pytest.raises(ValueError, mitogen.imports.fullname_prefix, 'foo.bar', 3)
    assert pytest.raises(ValueError, mitogen.imports.fullname_prefix, 'foo.bar', 4)
    assert pytest.raises(ValueError, mitogen.imports.fullname_prefix, 'foo.bar.baz', 4)

def test_imported_names():
    sys.path.append('tests/data/importer')

    with io.open('tests/data/importer/imported_names_pkg/sub1/sub2a/implicit.py') as f:
        co = compile(f.read(), f.name, 'exec')

    assert list(mitogen.imports.imported_names('imported_names_pkg.sub1.sub2a.implicit', co)) == [
        'mod', 'sys', 'sys.path',
    ]

    with io.open('tests/data/importer/imported_names_pkg/sub1/sub2a/implicit_pkg/__init__.py') as f:
        co = compile(f.read(), f.name, 'exec')

    assert list(mitogen.imports.imported_names('imported_names_pkg.sub1.sub2a.implicit_pkg', co)) == [
        'mod', 'sys', 'sys.path',
    ]

    with io.open('tests/data/importer/imported_names_pkg/sub1/sub2a/explicit.py') as f:
        co = compile(f.read(), f.name, 'exec')

    assert list(mitogen.imports.imported_names('imported_names_pkg.sub1.sub2a.explicit', co)) == [
        '__future__.absolute_import',
        'mod',
        'sys',
        'sys.path',

        'imported_names_pkg.sub1.sub2a.sys',
        'imported_names_pkg.sub1.sub2a.sys.path',

        'imported_names_pkg.sub1.sub2a.mod',
        'imported_names_pkg.sub1.mod',
        'imported_names_pkg.mod',
        'mod',

        'imported_names_pkg.sub1.sub2a.sub3',
        'imported_names_pkg.sub1.sub2a',
        'imported_names_pkg.sub1',
        'imported_names_pkg',

        'imported_names_pkg.sub1.sub2b.sub3.mod',
        'imported_names_pkg.sub1.sub2b.sub3',
    ]

    with io.open('tests/data/importer/imported_names_pkg/sub1/sub2a/explicit_pkg/__init__.py') as f:
        co = compile(f.read(), f.name, 'exec')

    assert list(mitogen.imports.imported_names('imported_names_pkg.sub1.sub2a.explicit_pkg', co)) == [
        '__future__.absolute_import',
        'mod',
        'sys',
        'sys.path',

        'imported_names_pkg.sub1.sub2a.sys',
        'imported_names_pkg.sub1.sub2a.sys.path',

        'imported_names_pkg.sub1.sub2a.mod',
        'imported_names_pkg.sub1.mod',
        'imported_names_pkg.mod',
        'mod',

        'imported_names_pkg.sub1.sub2a.sub3',
        'imported_names_pkg.sub1.sub2a',
        'imported_names_pkg.sub1',
        'imported_names_pkg',

        'imported_names_pkg.sub1.sub2b.sub3.mod',
        'imported_names_pkg.sub1.sub2b.sub3',
    ]


if __name__ == '__main__':
    filename = sys.argv[1]

    with io.open(filename, 'rb') as f:
        src = f.read()
        co = compile(src, filename, 'exec')

    print(co)
    for level, name, namelist in mitogen.imports.codeobj_imports(co):
        print('{level:>2} {name} {namelist}'.format(**locals()))

    for fullname in mitogen.imports.imported_names('foo.bar.baz', co):
        print(fullname)
