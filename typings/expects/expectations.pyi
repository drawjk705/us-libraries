"""
This type stub file was generated by pyright.
"""

class Expectation(object):
    def __init__(self, subject) -> None: ...
    @property
    def not_to(self): ...
    @property
    def to_not(self): ...
    def to(self, matcher): ...
