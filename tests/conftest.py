"""Shared test setup.

`fake_input` lets a test pretend the player typed a list of answers, so we can
test functions that ask questions without anyone sitting at a keyboard.
"""

from __future__ import annotations

import builtins

import pytest


@pytest.fixture
def fake_input(monkeypatch):
    """Return a function that queues up answers for input().

    Example:
        def test_something(fake_input):
            fake_input(["7", "y"])
            assert ask_int("Pick a number:") == 7
    """

    def _feed(answers: list[str]) -> None:
        queue = list(answers)

        def _fake(prompt: str = "") -> str:
            if not queue:
                raise AssertionError(
                    f"The code asked for more input than the test provided. Prompt was: {prompt!r}"
                )
            return queue.pop(0)

        monkeypatch.setattr(builtins, "input", _fake)

    return _feed


@pytest.fixture
def no_colour(monkeypatch):
    """Turn off ANSI colour codes so assertions can compare plain strings."""
    monkeypatch.setenv("NO_COLOR", "1")
