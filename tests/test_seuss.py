"""Tests for seuss."""

from seuss import AndThen, Digit, Pure, String

def test_string() -> None:
    assert String("fnord").parse("fnord hello") == [("fnord", " hello")]
    assert String("fnord").parse("hello world") == []


def test_digit() -> None:
    assert Digit().parse("1989") == [("1", "989")]
    assert Digit().parse("foo 1989") == []


def test_pure() -> None:
    p = Pure(42)
    assert p.parse("foo") == [(42, "foo")]


def test_pure_and_then() -> None:
    p = Pure("42")
    q = AndThen(p, String)
    assert q.parse("420") == String("42").parse("420")


def test_and_then_pure() -> None:
    p = Digit()
    q = AndThen(p, Pure)
    assert q.parse("420") == p.parse("420")
