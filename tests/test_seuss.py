"""Tests for seuss."""

from seuss import Digit, String

def test_string() -> None:
    assert String("fnord").parse("fnord hello") == [("fnord", " hello")]
    assert String("fnord").parse("hello world") == []


def test_digit() -> None:
    assert Digit().parse("1989") == [("1", "989")]
    assert Digit().parse("foo 1989") == []
