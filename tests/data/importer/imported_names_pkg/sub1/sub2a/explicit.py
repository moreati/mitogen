from __future__ import absolute_import

# | Python    | import foo     | from foo import bar  | from . import baz  |
# |-----------|----------------|----------------------|--------------------|
# | 2.4       | SyntaxError: future feature absolute_import is not defined |
# | 2.5+      |                Absolute               | Relative           |

import mod
import sys
from sys import path

from . import sys
from .sys import path

from . import mod
from .. import mod
from ... import mod
from .... import mod

from . import sub3
from .. import sub2a
from ... import sub1
from .... import imported_names_pkg

from ..sub2b.sub3 import mod
from ..sub2b import sub3
