"""An experiment in Python parsers."""

import string
from typing import Callable, Generic, Iterator, Protocol, TypeVar

import attrs

A = TypeVar("A")
B = TypeVar("B")
T = TypeVar("T")


@attrs.define
class Parser(Generic[T]):
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

    parse: Callable[[str], Iterator[tuple[T, str]]]
    """Parse T out of text, and return what's left of text.

    If we cannot parse the text, return an empty iterator.
    If there are multiple possible ways to parse the text,
    return an iterator that yields multiple results.
    """

    def map(self, function: Callable[[T], B]) -> "Parser[B]":
        """Run 'function' over the result of this parser."""
        return Map(function, self)

    def and_then(self, function: Callable[[T], "Parser[B]"]) -> "Parser[B]":
        """Construct another parser with the output of this one."""
        return AndThen(self, function)

    def then(self, next_parser: "Parser[B]") -> "Parser[B]":
        """Run another parser after this one, discarding this one's result."""
        return AndThen(self, lambda _: next_parser)


def String(match: str) -> Parser[str]:
    """Parse out a constant string."""

    def parse(text: str) -> Iterator[tuple[str, str]]:
        if text.startswith(match):
            yield (match, text[len(match) :])

    return Parser(parse)


def Digit() -> Parser[str]:
    """Parse a single digit.

    Return it as a character to give us more flexibility in how we use it.
    """

    def parse(text: str) -> Iterator[tuple[str, str]]:
        if text and text[0] in string.digits:
            yield (text[0], text[1:])

    return Parser(parse)


def Map(function: Callable[[A], B], parser: Parser[A]) -> Parser[B]:
    def parse(text: str) -> Iterator[tuple[B, str]]:
        for (value, remaining) in parser.parse(text):
            yield (function(value), remaining)

    return Parser(parse)


def Pure(value: T) -> Parser[T]:
    """Inject a value into the parsed result."""

    def parse(text: str) -> Iterator[tuple[T, str]]:
        yield (value, text)

    return Parser(parse)


def AndThen(previous: Parser[A], callback: Callable[[A], Parser[B]]) -> Parser[B]:
    """Run another parser that's constructed with the output of the previous one."""

    def parse(text: str) -> Iterator[tuple[B, str]]:
        for (value, remaining) in previous.parse(text):
            yield from callback(value).parse(remaining)

    return Parser(parse)


def replicate(n: int, parser: Parser[T]) -> Parser[list[T]]:
    """Run parser n times and yield a list of the results."""
    # TODO: There must be a less awful way of writing this.
    result = []

    def callback(value: T) -> Parser[T]:
        # TODO: I bet I could make this lazy with coroutines or something.
        result.append(value)
        return parser

    if n < 1:
        # TODO: Probably need a "Null" or "Fail" parser that just raises StopIteration.
        raise NotImplementedError("jml doesn't know what he's doing")

    p = parser
    for i in range(1, n):
        p = p.and_then(lambda x: callback(x))

    def wrap_up(value: T) -> Parser[list[T]]:
        result.append(value)
        final = Pure(list(result))
        result[:] = []
        return final

    return p.and_then(wrap_up)


# TODO: Ongoing MyPy issue with Pure & AndThen interaction
# TODO: Some way of handling applicative
# TODO: sequence
# TODO: yield expression syntax?
