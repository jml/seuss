"""An experiment in Python parsers."""

import string
from typing import Callable, Generic, Iterator, Protocol, TypeVar

import attrs


A = TypeVar("A")
B = TypeVar("B")
T = TypeVar("T")

class Parser(Protocol[T]):
    """A monadic parser.

    > A parser for things
    > Is a function from strings
    > To lists of pairs
    > Of things and strings.

    Note that here, a parser goes from strings to _iterators_ of pairs of
    things and strings. This is because lists are lazy in Haskell but not in
    Python, and we only want to go into other parsing options if we really
    have to.
    """

    def parse(self, text: str) -> Iterator[tuple[T, str]]:
        """Parse T out of text, and return what's left of text.

        If we cannot parse the text, return an empty iterator.
        If there are multiple possible ways to parse the text,
        return an iterator that yields multiple results.
        """
        ...


@attrs.define
class String:
    """Parse out a constant string."""
    match: str

    def parse(self, text: str) -> Iterator[tuple[str, str]]:
        if text.startswith(self.match):
            yield (self.match, text[len(self.match):])


@attrs.define
class Digit:
    """Parse a single digit.

    Return it as a character to give us more flexibility in how we use it.
    """
    def parse(self, text: str) -> Iterator[tuple[str, str]]:
        if text and text[0] in string.digits:
            yield (text[0], text[1:])


@attrs.define
class Map(Generic[A, B]):
    function: Callable[[A], B]
    parser: Parser[A]

    def parse(self, text: str) -> Iterator[tuple[B, str]]:
        for (value, remaining) in self.parser.parse(text):
            yield (self.function(value), remaining)


@attrs.define
class Pure(Generic[T]):
    """Inject a value into the parsed result."""

    # TODO: Maybe "inject" might be clearer?
    value: T

    def parse(self, text: str) -> Iterator[tuple[T, str]]:
        yield (self.value, text)


@attrs.define
class AndThen(Generic[A, B]):
    """Run another parser that's constructed with the output of the previous one."""

    previous: Parser[A]
    callback: Callable[[A], Parser[B]]

    def parse(self, text: str) -> Iterator[tuple[B, str]]:
        for (value, remaining) in self.previous.parse(text):
            yield from self.callback(value).parse(remaining)

# TODO: Some way of handling applicative
# TODO: Parse a YYYY-MM-DD date
# TODO: sequence
# TODO: replicate
# TODO: yield expression syntax?
