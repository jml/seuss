"""Tests for seuss."""

from datetime import date

from seuss import AndThen, Digit, Map, Pure, String


def test_string() -> None:
    assert list(String("fnord").parse("fnord hello")) == [("fnord", " hello")]
    assert list(String("fnord").parse("hello world")) == []


def test_digit() -> None:
    assert list(Digit().parse("1989")) == [("1", "989")]
    assert list(Digit().parse("foo 1989")) == []


def test_pure() -> None:
    p = Pure(42)
    assert list(p.parse("foo")) == [(42, "foo")]


def test_pure_and_then() -> None:
    p = Pure("42")
    q = AndThen(p, String)
    assert list(q.parse("420")) == list(String("42").parse("420"))


def test_and_then_pure() -> None:
    p = Digit()
    q = AndThen(p, Pure)  # type: ignore
    assert list(q.parse("420")) == list(p.parse("420"))


def test_map() -> None:
    p = Map(int, Digit())
    assert list(p.parse("420")) == [(4, "20")]


def test_map_helper() -> None:
    assert list(Digit().map(int).parse("420")) == [(4, "20")]


def test_and_then_helper() -> None:
    assert list(Digit().and_then(Pure).parse("420")) == list(Digit().parse("420"))  # type: ignore


def test_and_then_results() -> None:
    """We can chain together parsers to parse more complex strings."""
    two_digit_number = (
        Digit().and_then(lambda a: Digit().and_then(lambda b: Pure(a + b))).map(int)
    )
    assert list(two_digit_number.parse("42")) == [(42, "")]


def test_parse_iso_date() -> None:
    two_digits = Digit().and_then(lambda a: Digit().and_then(lambda b: Pure(a + b)))
    four_digits = two_digits.and_then(
        lambda a: two_digits.and_then(lambda b: Pure(a + b))
    )
    sep = String("-")
    iso_date = four_digits.map(int).and_then(
        lambda year: sep.and_then(lambda _: two_digits.map(int)).and_then(
            lambda month: sep.and_then(lambda _: two_digits.map(int)).and_then(
                lambda day: Pure(date(year, month, day))
            )
        )
    )
    assert list(iso_date.parse("2022-06-09")) == [(date(2022, 6, 9), "")]
