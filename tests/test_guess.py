"""Tests for the Guess the Number game."""

from arcade.games import guess


def test_evaluate_detects_correct_guess():
    assert guess.evaluate(42, 42) == "correct"


def test_evaluate_detects_too_low():
    assert guess.evaluate(10, 50) == "too low"


def test_evaluate_detects_too_high():
    assert guess.evaluate(90, 50) == "too high"


def test_first_guess_scores_the_most():
    assert guess.score_for(1) > guess.score_for(2)


def test_score_is_never_negative():
    assert guess.score_for(guess.MAX_GUESSES * 10) == 0
