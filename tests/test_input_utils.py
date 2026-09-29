"""Tests for the input helpers."""

from arcade import input_utils


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
