"""An experiment in Python parsers."""

import string
from typing import Protocol, TypeVar

import attrs


T = TypeVar("T")

class Parser(Protocol[T]):
    """
    A parser for things
    Is a function from strings
    To lists of pairs
    Of things and strings.
    """

    def parse(self, text: str) -> list[tuple[T, str]]:
        ...


@attrs.define
class String:
    """Parse out a constant string."""
    match: str

    def parse(self, text: str) -> list[tuple[str, str]]:
        if text.startswith(self.match):
            return [(self.match, text[len(self.match):])]
        return []


@attrs.define
class Digit:
    """Parse a single digit.

    Return it as a character to give us more flexibility in how we use it.
    """
    def parse(self, text: str) -> list[tuple[str, str]]:
        if not text:
            return []
        if text[0] in string.digits:
            return [(text[0], text[1:])]
        return []
