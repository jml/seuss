"""Tests for seuss."""

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
    q = AndThen(p, lambda x: Pure(x))
    assert list(q.parse("420")) == list(p.parse("420"))


def test_map() -> None:
    p = Map(int, Digit())
    assert list(p.parse("420")) == [(4, "20")]
