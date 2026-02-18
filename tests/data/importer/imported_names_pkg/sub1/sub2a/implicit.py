# No explicit control of absolute_import.
#
# | Python    | import foo | from foo import bar | from . import baz |
# |-----------|------------|---------------------|-------------------|
# | 2.4       |    Relative, absolute fallback   | SyntaxError       |
# | 2.5 - 2.7 |    Relative, absolute fallback   | Relative          |
# | 3.0+      | Absolute   | Absolute            | Relative          |

import mod
import sys
from sys import path
