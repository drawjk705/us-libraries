"""
This type stub file was generated by pyright.
"""

from callee.base import BaseMatcher

"""
This type stub file was generated by pyright.
"""

class StringTypeMatcher(BaseMatcher):
    """Matches some string type.
    This class shouldn't be used directly.
    """

    CLASS = ...
    def __init__(self) -> None: ...
    def match(self, value): ...
    def __repr__(self): ...

class String(StringTypeMatcher):
    """Matches any string.

    | On Python 2, this means either :class:`str` or :class:`unicode` objects.
    | On Python 3, this means :class:`str` objects exclusively.
    """

    CLASS = ...

class Unicode(StringTypeMatcher):
    """Matches a Unicode string.

    | On Python 2, this means :class:`unicode` objects exclusively.
    | On Python 3, this means :class:`str` objects exclusively.
    """

    CLASS = ...

class StartsWith(BaseMatcher):
    """Matches a string starting with given prefix."""

    def __init__(self, prefix) -> None: ...
    def match(self, value): ...
    def __repr__(self): ...

class EndsWith(BaseMatcher):
    """Matches a string ending with given suffix."""

    def __init__(self, suffix) -> None: ...
    def match(self, value): ...
    def __repr__(self): ...

class Glob(BaseMatcher):
    """Matches a string against a Unix shell wildcard pattern.

    See the :mod:`fnmatch` module for more details about those patterns.
    """

    DEFAULT_CASE = ...
    FNMATCH_FUNCTIONS = ...
    def __init__(self, pattern, case=...) -> None:
        """
        :param pattern: Pattern to match against
        :param case:

            Case sensitivity setting. Possible options:

                * ``'system'`` or ``None``: case sensitvity is system-dependent
                  (this is the default)
                * ``True``: matching is case-sensitive
                * ``False``: matching is case-insensitive
        """
        ...
    def match(self, value): ...
    def __repr__(self): ...

class Regex(BaseMatcher):
    """Matches a string against a regular expression."""

    REGEX_TYPE = ...
    def __init__(self, pattern, flags=...) -> None:
        """
        :param pattern: Regular expression to match against.
                        It can be given as string,
                        or as a compiled regular expression object
        :param flags: Flags to use with a regular expression passed as string
        """
        ...
    def match(self, value): ...
    def __repr__(self): ...
