"""An experiment in Python parsers."""

import string
from typing import Callable, Generic, Protocol, TypeVar

import attrs


A = TypeVar("A")
B = TypeVar("B")
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


@attrs.define
class Pure(Generic[T]):
    """Inject a value into the parsed result."""

    # TODO: Maybe "inject" might be clearer?
    value: T

    def parse(self, text: str) -> list[tuple[T, str]]:
        return [(self.value, text)]


@attrs.define
class AndThen(Generic[A, B]):
    """Run another parser that's constructed with the output of the previous one."""

    previous: Parser[A]
    callback: Callable[[A], Parser[B]]

    def parse(self, text: str) -> list[tuple[B, str]]:
        results = []
        for (value, remaining) in self.previous.parse(text):
            results.extend(self.callback(value).parse(remaining))
        return results
