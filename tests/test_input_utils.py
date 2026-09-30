"""Tests for the input helpers."""

import builtins
import inspect

import pytest

from arcade import input_utils


def _scripted(monkeypatch, script):
    """Feed a script to input().

    Each item is either the string the player "types", or an exception
    instance that input() should raise (EOFError / KeyboardInterrupt).
    """
    queue = list(script)

    def _fake(prompt: str = "") -> str:
        if not queue:
            raise AssertionError(f"The code asked for more input than scripted: {prompt!r}")
        item = queue.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    monkeypatch.setattr(builtins, "input", _fake)
    return _fake


INTERRUPTIONS = [
    pytest.param(EOFError(), id="eof"),
    pytest.param(KeyboardInterrupt(), id="keyboard-interrupt"),
]

# Every public entry point, as a zero-arg call. Ctrl+C and Ctrl+D must behave
# the same at each one.
ENTRIES = [
    ("ask", lambda: input_utils.ask("Question:")),
    ("ask_int", lambda: input_utils.ask_int("Question:")),
    ("ask_choice", lambda: input_utils.ask_choice("Question:", ["a", "b"])),
    ("ask_letter", lambda: input_utils.ask_letter("Question:")),
    ("confirm", lambda: input_utils.confirm("Question:")),
    ("pause", lambda: input_utils.pause()),
]


@pytest.mark.parametrize("failure", INTERRUPTIONS)
@pytest.mark.parametrize("entry_name,entry", ENTRIES)
def test_every_entry_propagates_both_interruptions(monkeypatch, entry_name, entry, failure):
    _scripted(monkeypatch, [failure])
    with pytest.raises(type(failure)):
        entry()


@pytest.mark.parametrize("failure", INTERRUPTIONS)
def test_a_successful_call_right_after_an_interruption_is_unaffected(monkeypatch, failure):
    calls = 0

    def _fake(prompt: str = "") -> str:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise failure
        return str(calls)

    monkeypatch.setattr(builtins, "input", _fake)

    with pytest.raises(type(failure)):
        input_utils.ask("Question:")
    assert input_utils.ask("Question:") == "2"
    assert input_utils.ask_int("Pick:") == 3


@pytest.mark.parametrize("failure", INTERRUPTIONS)
def test_partial_progress_then_interruption_does_not_loop_forever(
    monkeypatch, capsys, failure
):
    _scripted(monkeypatch, ["banana", "0", failure])
    with pytest.raises(type(failure)):
        input_utils.ask_int("Pick:", minimum=1, maximum=9)
    output = capsys.readouterr().out
    assert "not a whole number" in output
    assert "Too low" in output


@pytest.mark.parametrize("failure", INTERRUPTIONS)
def test_several_rounds_can_finish_before_an_interruption(monkeypatch, failure):
    moves = ["rock", "paper", "scissors", "rock", "paper"]
    _scripted(monkeypatch, [*moves, failure])

    answers = [
        input_utils.ask_choice("Move?", ["rock", "paper", "scissors"]) for _ in range(5)
    ]
    assert answers == moves
    with pytest.raises(type(failure)):
        input_utils.ask_choice("Move?", ["rock", "paper", "scissors"])


def test_the_same_input_sequence_replays_identically(monkeypatch, capsys):
    def one_run():
        _scripted(monkeypatch, ["banana", "0", "99", "4"])
        value = input_utils.ask_int("Pick:", minimum=1, maximum=9)
        return value, capsys.readouterr().out

    first = one_run()
    second = one_run()
    assert first == second
    assert first[0] == 4


def test_repeated_calls_each_consume_one_answer(monkeypatch):
    _scripted(monkeypatch, ["a", "b", "c"])
    assert [input_utils.ask_letter("Letter:") for _ in range(3)] == ["a", "b", "c"]


def test_ask_choice_accepts_the_only_option(monkeypatch):
    _scripted(monkeypatch, ["yes"])
    assert input_utils.ask_choice("OK?", ["yes"]) == "yes"


@pytest.mark.parametrize("failure", INTERRUPTIONS)
def test_ask_choice_with_an_empty_list_still_interrupts_cleanly(monkeypatch, failure):
    _scripted(monkeypatch, [failure])
    with pytest.raises(type(failure)):
        input_utils.ask_choice("Pick?", [])


@pytest.mark.parametrize("failure", INTERRUPTIONS)
def test_interruptions_leave_no_module_state_behind(monkeypatch, failure):
    def _state():
        # Only plain data counts as state; modules, classes and functions are
        # part of the code, not something an input call could mutate.
        return {
            key: value
            for key, value in vars(input_utils).items()
            if not (
                inspect.ismodule(value)
                or inspect.isclass(value)
                or inspect.isfunction(value)
                or key.startswith("__")
            )
        }

    before = _state()
    for _, entry in ENTRIES:
        _scripted(monkeypatch, [failure])
        with pytest.raises(type(failure)):
            entry()
    assert _state() == before


def test_ask_returns_what_the_player_typed(fake_input):
    fake_input(["hello"])
    assert input_utils.ask("Say something:") == "hello"


def test_ask_int_accepts_a_number(fake_input):
    fake_input(["7"])
    assert input_utils.ask_int("Pick:") == 7


def test_ask_int_asks_again_after_nonsense(fake_input, capsys):
    fake_input(["banana", "3"])
    assert input_utils.ask_int("Pick:") == 3
    assert "not a whole number" in capsys.readouterr().out


def test_ask_int_rejects_a_value_below_the_minimum(fake_input):
    fake_input(["0", "5"])
    assert input_utils.ask_int("Pick:", minimum=1) == 5


def test_ask_int_rejects_a_value_above_the_maximum(fake_input):
    fake_input(["99", "4"])
    assert input_utils.ask_int("Pick:", maximum=9) == 4


def test_ask_choice_ignores_capital_letters(fake_input):
    fake_input(["ROCK"])
    assert input_utils.ask_choice("Move?", ["rock", "paper"]) == "rock"


def test_ask_choice_asks_again_for_something_not_on_the_list(fake_input):
    fake_input(["banana", "paper"])
    assert input_utils.ask_choice("Move?", ["rock", "paper"]) == "paper"


def test_ask_letter_accepts_one_letter(fake_input):
    fake_input(["k"])
    assert input_utils.ask_letter("Letter:") == "k"


def test_ask_letter_rejects_a_whole_word(fake_input):
    fake_input(["word", "w"])
    assert input_utils.ask_letter("Letter:") == "w"


def test_ask_letter_rejects_a_digit(fake_input):
    fake_input(["4", "d"])
    assert input_utils.ask_letter("Letter:") == "d"


def test_confirm_returns_true_for_yes(fake_input):
    fake_input(["y"])
    assert input_utils.confirm("Sure?") is True


def test_confirm_returns_false_for_no(fake_input):
    fake_input(["n"])
    assert input_utils.confirm("Sure?") is False
