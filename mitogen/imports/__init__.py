# SPDX-FileCopyrightText: 2025 Mitogen authors <https://github.com/mitogen-hq>
# SPDX-License-Identifier: BSD-3-Clause
# !mitogen: minify_safe

import os
import sys
import types
import typing

if sys.version_info >= (3, 14):
    from mitogen.imports._py314 import _code_imports
elif sys.version_info >= (3, 6):
    from mitogen.imports._py36 import _code_imports
elif sys.version_info >= (2, 5):
    from mitogen.imports._py2 import _code_imports_py25 as _code_imports
else:
    from mitogen.imports._py2 import _code_imports_py24 as _code_imports


def codeobj_imports(co):
    # type: (types.CodeType) -> typing.Generator[tuple[int, str, tuple[int, ...]], None, None]
    """
    Yield (level, modname, names) tuples by scanning the code object `co`.

    Top level `import mod` & `from mod import foo` statements are matched.
    Those inside a `class ...` or `def ...` block are currently skipped.

    >>> co = compile('import a, b; from c import d, e as f', '<str>', 'exec')
    >>> list(codeobj_imports(co))  # doctest: +ELLIPSIS
    [(..., 'a', ()), (..., 'b', ()), (..., 'c', ('d', 'e'))]

    :return:
        Generator producing `(level, modname, names)` tuples, where:

        * `level`:
            -1 implicit relative (Python 2.x default)
            0  absolute (Python 3.x, `from __future__ import absolute_import`)
            >0 explicit relative (`from . import a`, `from ..b, import c`)
        * `modname`: Name of module to import, or to import `names` from.
        * `names`: tuple of names in `from mod import ..`.
    """
    return _code_imports(co.co_code, co.co_consts, co.co_names)


def fullname_prefix(fullname, strip):
    '''
    Return fullname with n levels of sub-module removed.

    >>> fullname_prefix('foo.bar.baz', 1)
    'foo.bar'
    >>> fullname_prefix('foo.bar.baz', 3)
    ''
    '''
    pos = None
    for i in range(strip):
        pos = fullname.rfind('.', 0, pos)
        if pos == -1:
            if i == strip - 1:
                return ''
            raise ValueError
    return fullname[:pos]

def fullname_join(prefix, *parts):
    if prefix: return '.'.join((prefix, '.'.join(parts)))
    return '.'.join(parts)

def imported_names(fullname: str, co: types.CodeType):
    co_dirname = os.path.dirname(co.co_filename)
    for level, imported_name, from_names in codeobj_imports(co):
        if level == -1:
            # Python 2.x, implicit relative.
            # Check relative import first, if no match then it's absolute.
            imported_toplevel, _, _ = imported_name.partition('.')
            if (os.path.exists(os.path.join(co_dirname, '%s.py' % imported_toplevel))
                or os.path.exists(os.path.join(co_dirname, '%s/__init__.py' % imported_toplevel))
            ):
                imported_fullname = '%s.%s' % (fullname, imported_name)
            else:
                imported_fullname = imported_name
        elif level == 0:
            # Absolute
            imported_fullname = imported_name
        else:
            # Explicit relative
            base_prefix = fullname_prefix(fullname, level)
            if base_prefix:
                imported_fullname = base_prefix
                if imported_name:
                    imported_fullname = '%s.%s' % (imported_fullname, imported_name)
            else:
                imported_fullname = imported_name

        if from_names:
            for from_name in from_names:
                yield fullname_join(imported_fullname, from_name)
        else:
            yield  imported_fullname

