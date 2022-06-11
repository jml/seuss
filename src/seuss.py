"""An experiment in Python parsers."""

import string
from typing import Callable, Generic, Iterable, Iterator, Protocol, TypeVar

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

    def passthrough(self, next_parser: "Parser[A]") -> "Parser[T]":
        # TODO: Better name
        return AndThen(self, lambda a: next_parser.map(lambda _: a))

    def __or__(self, other: "Parser[T]") -> "Parser[T]":
        return OneOf([self, other])

    @classmethod
    def Zero(cls) -> "Parser[T]":
        """A parser that rejects all input."""

        def reject(text: str) -> Iterator[tuple[T, str]]:
            yield from ()

        return cls(reject)


def String(match: str) -> Parser[str]:
    """Parse out a constant string."""

    def parse(text: str) -> Iterator[tuple[str, str]]:
        if text.startswith(match):
            yield (match, text[len(match) :])

    return Parser(parse)


def IsCharacter(predicate: Callable[[str], bool]) -> Parser[str]:
    """Parse out a character that matches the predicate."""

    def parse(text: str) -> Iterator[tuple[str, str]]:
        if text and predicate(text[0]):
            yield (text[0], text[1:])

    return Parser(parse)


def Characters(characters: str) -> Parser[str]:
    """Parse something that must be one of the supplied characters.

    Equivalent to OneOf(map(String, characters)) or IsCharacter(lambda x: x in characters).
    """

    def parse(text: str) -> Iterator[tuple[str, str]]:
        if text and text[0] in characters:
            yield (text[0], text[1:])

    return Parser(parse)


Digit = Characters(string.digits)
"""Parse a single digit.

Return it as a character to give us more flexibility in how we use it.
"""


Whitespace = Characters(string.whitespace)
"""Parse a single whitespace character."""


def _parse_end_of_input(text: str) -> Iterator[tuple[None, str]]:
    if not text:
        yield (None, "")


EndOfInput = Parser(_parse_end_of_input)
"""Parse the end of the string."""


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


def Lift(f: Callable[[A, B], T], a: Parser[A], b: Parser[B]) -> Parser[T]:
    """Run one parser after the other and combine the results."""

    def parse(text: str) -> Iterator[tuple[T, str]]:
        for (x, remaining) in a.parse(text):
            for (y, remaining) in b.parse(remaining):
                yield (f(x, y), remaining)

    return Parser(parse)


def OneOf(parsers: Iterable[Parser[T]]) -> Parser[T]:
    """Make a parser that matches any of the given parsers."""

    def parse(text: str) -> Iterator[tuple[T, str]]:
        for parser in parsers:
            yield from parser.parse(text)

    return Parser(parse)


def replicate(n: int, parser: Parser[T]) -> Parser[list[T]]:
    """Run parser n times and yield a list of the results."""

    stack: list[Parser[list[T]]] = [Pure([])]
    for i in range(n):
        stack.append(Lift(cons, parser, stack[-1]))
    return stack[-1]


def many(parser: Parser[T]) -> Parser[list[T]]:
    """Execute a parser zero or more times."""

    # TODO: Is there a way to implement this without having to delve into the parser layer?
    # I haven't yet figured out how to do an Alternative-layer implementation without laziness.
    #
    # Here's the Haskell implementation for reference.
    #
    # many :: f a -> f [a]
    # many v = many_v
    #   where
    #     many_v = some_v <|> pure []
    #     some_v = liftA2 (:) v many_v

    def parse(text: str) -> Iterator[tuple[list[T], str]]:
        bottom = False
        for (value, remainder) in parser.parse(text):
            bottom = True
            for items in parse(remainder):
                (values, rump) = items
                yield [value] + values, rump
        if not bottom:
            yield [], text

    return Parser(parse)


# TODO: Ongoing MyPy issue with Pure & AndThen interaction
# TODO: sequence
# TODO: yield expression syntax?
# TODO: Can't figure out how to do `many` or `sepBy` at the monad layer
# TODO: Nested parentheses?
# TODO: Come up with an example where we get multiple parses, i.e. where `list of things and strings` matters.


def cons(x: T, ys: list[T]) -> list[T]:
    return [x] + ys
