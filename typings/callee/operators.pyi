"""
This type stub file was generated by pyright.
"""

from callee.base import BaseMatcher

"""
This type stub file was generated by pyright.
"""
class OperatorMatcher(BaseMatcher):
    """Matches values based on comparison operator and a reference object.
    This class shouldn't be used directly.
    """
    OP = ...
    TRANSFORM = ...
    def __init__(self, *args, **kwargs) -> None:
        """Accepts a single argument: the reference object to compare against.

        It can be passed either as a single positional parameter,
        or as a single keyword argument -- preferably with a readable name,
        for example::

            some_mock.assert_called_with(Number() & LessOrEqual(to=42))
        """
        ...
    
    def match(self, value):
        ...
    
    def __repr__(self):
        """Provide an universal representation of the matcher."""
        ...
    


class Less(OperatorMatcher):
    """Matches values that are smaller (as per ``<`` operator)
    than given object.
    """
    OP = ...


LessThan = Less
Lt = Less
class LessOrEqual(OperatorMatcher):
    """Matches values that are smaller than,
    or equal to (as per ``<=`` operator), given object.
    """
    OP = ...


LessOrEqualTo = LessOrEqual
Le = LessOrEqual
class Greater(OperatorMatcher):
    """Matches values that are greater (as per ``>`` operator)
    than given object.
    """
    OP = ...


GreaterThan = Greater
Gt = Greater
class GreaterOrEqual(OperatorMatcher):
    """Matches values that are greater than,
    or equal to (as per ``>=`` operator), given object.
    """
    OP = ...


GreaterOrEqualTo = GreaterOrEqual
Ge = GreaterOrEqual
class LengthMatcher(OperatorMatcher):
    """Matches values based on their length, as compared to a reference.
    This class shouldn't be used directly.
    """
    TRANSFORM = ...
    def __init__(self, *args, **kwargs) -> None:
        ...
    


class Shorter(LengthMatcher):
    """Matches values that are shorter (as per ``<`` comparison on ``len``)
    than given value.
    """
    OP = ...


ShorterThan = Shorter
class ShorterOrEqual(LengthMatcher):
    """Matches values that are shorter than,
    or equal in ``len``\ gth to (as per ``<=`` operator), given object.
    """
    OP = ...


ShorterOrEqualTo = ShorterOrEqual
class Longer(LengthMatcher):
    """Matches values that are longer (as per ``>`` comparison on ``len``)
    than given value.
    """
    OP = ...


LongerThan = Longer
class LongerOrEqual(LengthMatcher):
    """Matches values that are longer than,
    or equal in ``len``\ gth to (as per ``>=`` operator), given object.
    """
    OP = ...


LongerOrEqualTo = LongerOrEqual
class Contains(OperatorMatcher):
    """Matches values that contain (as per the ``in`` operator)
    given reference object.
    """
    OP = ...
    def __repr__(self):
        ...
    


class In(OperatorMatcher):
    """Matches values that are within the reference object
    (as per the ``in`` operator).
    """
    OP = ...
    def __repr__(self):
        ...
    


