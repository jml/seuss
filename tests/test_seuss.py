"""Tests for seuss."""

from datetime import date

import pytest

from seuss import AndThen, Digit, EndOfInput, Lift, Map, OneOf, Pure, String, many, replicate


def parse(parser, text):
    return list(parser.parse(text))


def parse_strict(parser, text):
    """Parse 'text' and fail if the whole string isn't parsed or if there's more than one way to parse it."""
    # Might add this to the main class.
    result = list(parser.passthrough(EndOfInput).parse(text))
    [(value, remainder)] = result
    assert remainder == ""
    return value


def test_string() -> None:
    assert list(String("fnord").parse("fnord hello")) == [("fnord", " hello")]
    assert list(String("fnord").parse("hello world")) == []


def test_digit() -> None:
    assert list(Digit.parse("1989")) == [("1", "989")]
    assert list(Digit.parse("foo 1989")) == []


def test_pure() -> None:
    p = Pure(42)
    assert list(p.parse("foo")) == [(42, "foo")]


def test_pure_and_then() -> None:
    p = Pure("42")
    q = AndThen(p, String)
    assert list(q.parse("420")) == list(String("42").parse("420"))


def test_pure_list() -> None:
    parse_strict(Pure([]).then(Digit), "9") == 9


def test_and_then_pure() -> None:
    p = Digit
    q = AndThen(p, Pure)  # type: ignore
    assert list(q.parse("420")) == list(p.parse("420"))


def test_map() -> None:
    p = Map(int, Digit)
    assert list(p.parse("420")) == [(4, "20")]


def test_map_helper() -> None:
    assert list(Digit.map(int).parse("420")) == [(4, "20")]


def test_and_then_helper() -> None:
    assert list(Digit.and_then(Pure).parse("420")) == list(Digit.parse("420"))  # type: ignore


def test_and_then_results() -> None:
    """We can chain together parsers to parse more complex strings."""
    two_digit_number = Digit.and_then(lambda a: Digit.and_then(lambda b: Pure(a + b))).map(int)
    assert parse_strict(two_digit_number, "42") == 42


def test_parse_iso_date() -> None:
    two_digits = Digit.and_then(lambda a: Digit.and_then(lambda b: Pure(a + b)))
    four_digits = two_digits.and_then(lambda a: two_digits.and_then(lambda b: Pure(a + b)))
    sep = String("-")
    iso_date = four_digits.map(int).and_then(
        lambda year: sep.and_then(lambda _: two_digits.map(int)).and_then(
            lambda month: sep.and_then(lambda _: two_digits.map(int)).and_then(lambda day: Pure(date(year, month, day)))
        )
    )
    assert parse_strict(iso_date, "2022-06-09") == date(2022, 6, 9)


def test_parse_iso_date_then() -> None:
    two_digits = Digit.and_then(lambda a: Digit.and_then(lambda b: Pure(a + b)))
    four_digits = two_digits.and_then(lambda a: two_digits.and_then(lambda b: Pure(a + b)))
    sep = String("-")
    iso_date = four_digits.map(int).and_then(
        lambda year: sep.then(two_digits.map(int)).and_then(
            lambda month: sep.then(two_digits.map(int)).and_then(lambda day: Pure(date(year, month, day)))
        )
    )
    assert parse_strict(iso_date, "2022-06-09") == date(2022, 6, 9)


def test_replicate() -> None:
    digit = Digit
    assert parse(replicate(0, digit), "1989") == [([], "1989")]
    assert parse(replicate(1, digit), "1989") == [(["1"], "989")]
    assert parse(replicate(2, digit), "1989") == [(["1", "9"], "89")]
    assert parse(replicate(3, digit), "1989") == [(["1", "9", "8"], "9")]
    assert parse(replicate(4, digit), "1989") == [(["1", "9", "8", "9"], "")]


def test_parse_iso_date_replicate() -> None:
    year = replicate(4, Digit).map("".join).map(int)
    month_or_day = replicate(2, Digit).map("".join).map(int)
    sep = String("-")
    iso_date = year.and_then(
        lambda y: sep.then(
            month_or_day.and_then(lambda m: sep.then(month_or_day.and_then(lambda d: Pure(date(y, m, d)))))
        )
    )
    assert parse_strict(iso_date, "2022-06-09") == date(2022, 6, 9)


def test_parse_end_of_input() -> None:
    assert list(replicate(2, Digit).passthrough(EndOfInput).parse("420")) == []


def test_any() -> None:
    foo = String("foo")
    bar = String("bar")
    foobar = OneOf([foo, bar])
    combined = Lift(lambda x, y: (x, y), foobar, foobar)
    assert parse_strict(combined, "foofoo") == ("foo", "foo")
    assert parse_strict(combined, "foobar") == ("foo", "bar")
    assert parse_strict(combined, "barfoo") == ("bar", "foo")
    assert parse_strict(combined, "barbar") == ("bar", "bar")


def test_monoid() -> None:
    foo = String("foo")
    bar = String("bar")
    assert parse_strict(foo | bar, "foo") == "foo"
    # TODO: foo.Zero to make the typing work. There must be a better way.
    assert parse_strict(foo | bar | foo.Zero(), "foo") == "foo"


def test_many() -> None:
    assert parse(many(Digit), "a") == [([], "a")]
    assert parse(many(Digit), "1") == [(["1"], "")]
    assert parse_strict(many(Digit), "1989") == ["1", "9", "8", "9"]
