"""Tests for the Hangman game."""

import copy
import random

import pytest

from arcade import art
from arcade.games import hangman


def test_mask_hides_unguessed_letters():
    assert hangman.mask_word("python", set()) == "_ _ _ _ _ _"


def test_mask_reveals_guessed_letters():
    assert hangman.mask_word("python", {"p", "n"}) == "p _ _ _ _ n"


def test_mask_reveals_every_occurrence_of_a_letter():
    # Both 'o's should appear, not just the first.
    assert hangman.mask_word("moon", {"o"}) == "_ o o _"


def test_is_solved_is_false_when_letters_remain():
    assert hangman.is_solved("python", {"p", "y"}) is False


def test_is_solved_is_true_when_all_letters_found():
    assert hangman.is_solved("python", set("python")) is True


def test_longer_words_score_more():
    assert hangman.score_for("recursion", 0) > hangman.score_for("debug", 0)


def test_mistakes_reduce_the_score():
    assert hangman.score_for("python", 3) < hangman.score_for("python", 0)


def test_every_word_in_the_list_is_lowercase_letters_only():
    # A word with a capital or a hyphen would be impossible to guess,
    # because ask_letter() only accepts single lowercase letters.
    for word in hangman.WORDS:
        assert word.isalpha(), f"{word!r} has a non-letter character"
        assert word.islower(), f"{word!r} is not lowercase"


def test_there_is_a_gallows_drawing_for_every_wrong_guess():
    # One drawing for the empty gallows plus one per wrong guess.
    assert len(art.GALLOWS) == hangman.MAX_WRONG + 1


# --- apply_guess: the pure guess-handling entry point -----------------------


def test_apply_guess_hit_adds_the_letter():
    updated, outcome = hangman.apply_guess("python", set(), "p")
    assert outcome == "hit"
    assert updated == {"p"}


def test_apply_guess_miss_adds_the_letter():
    updated, outcome = hangman.apply_guess("python", set(), "x")
    assert outcome == "miss"
    assert updated == {"x"}


def test_apply_guess_repeat_reports_repeat_and_changes_nothing():
    guessed = {"x"}
    snapshot = copy.deepcopy(guessed)
    updated, outcome = hangman.apply_guess("python", guessed, "x")
    assert outcome == "repeat"
    assert updated == snapshot
    assert guessed == snapshot


@pytest.mark.parametrize("first,second", [("x", "X"), ("X", "x"), ("p", "P"), ("P", "p")])
def test_apply_guess_repeat_ignores_case(first, second):
    guessed, _ = hangman.apply_guess("python", set(), first)
    updated, outcome = hangman.apply_guess("python", guessed, second)
    assert outcome == "repeat"
    assert updated == guessed


@pytest.mark.parametrize("bad", ["", "ab", "1", " ", "!", None, 5, ["a"]])
def test_apply_guess_rejects_invalid_letters_without_touching_state(bad):
    guessed = {"a", "b"}
    snapshot = copy.deepcopy(guessed)
    with pytest.raises(ValueError):
        hangman.apply_guess("python", guessed, bad)
    assert guessed == snapshot


@pytest.mark.parametrize("bad_word", ["", None, 42, "abc1", "a b", "hi!"])
def test_apply_guess_rejects_invalid_words(bad_word):
    with pytest.raises(ValueError):
        hangman.apply_guess(bad_word, set(), "a")


def test_apply_guess_never_mutates_the_caller_set():
    guessed = {"a"}
    snapshot = copy.deepcopy(guessed)
    updated, outcome = hangman.apply_guess("python", guessed, "p")
    assert outcome == "hit"
    assert guessed == snapshot
    assert updated == {"a", "p"}
    assert updated is not guessed


def test_apply_guess_failure_then_success_still_works():
    guessed = {"p"}
    snapshot = copy.deepcopy(guessed)
    with pytest.raises(ValueError):
        hangman.apply_guess("python", guessed, "!!")
    assert guessed == snapshot
    updated, outcome = hangman.apply_guess("python", guessed, "y")
    assert outcome == "hit"
    assert updated == {"p", "y"}


@pytest.mark.parametrize(
    "sequence",
    [
        ["p", "x", "a"],
        ["a", "x", "p"],
        ["x", "p", "a"],
    ],
)
def test_apply_guess_final_state_does_not_depend_on_order(sequence):
    guessed = set()
    for letter in sequence:
        guessed, _ = hangman.apply_guess("python", guessed, letter)
    assert guessed == {"p", "x", "a"}


def test_apply_guess_same_sequence_replays_identically():
    sequence = ["p", "X", "x", "q", "P", "y"]

    def run():
        guessed = set()
        outcomes = []
        for letter in sequence:
            guessed, outcome = hangman.apply_guess("python", guessed, letter)
            outcomes.append(outcome)
        return guessed, outcomes

    assert run() == run()


def test_apply_guess_consecutive_rounds_track_each_step():
    guessed = set()
    wrong = 0
    for letter, expected in [("p", "hit"), ("x", "miss"), ("x", "repeat"), ("y", "hit"), ("z", "miss")]:
        guessed, outcome = hangman.apply_guess("python", guessed, letter)
        assert outcome == expected
        if outcome == "miss":
            wrong += 1
    assert wrong == 2
    assert guessed == {"p", "x", "y", "z"}


def test_apply_guess_state_stays_bounded_by_the_alphabet():
    guessed = set()
    for round_trip in range(3):
        for code in range(ord("a"), ord("z") + 1):
            guessed, outcome = hangman.apply_guess("python", guessed, chr(code))
            if round_trip > 0:
                assert outcome == "repeat"
    assert len(guessed) == 26


def test_apply_guess_single_letter_word_boundary():
    updated, outcome = hangman.apply_guess("a", set(), "a")
    assert outcome == "hit"
    assert hangman.is_solved("a", updated) is True


# --- play: full rounds with scripted input ----------------------------------


def _play_with_word(monkeypatch, fake_input, word, answers, seed=0):
    monkeypatch.setattr(hangman, "WORDS", [word])
    fake_input(answers)
    return hangman.play(rng=random.Random(seed))


def test_play_repeated_wrong_letter_costs_no_extra_life(monkeypatch, fake_input, capsys):
    score = _play_with_word(
        monkeypatch, fake_input, "python", ["x", "x", "x", "p", "y", "t", "h", "o", "n"]
    )
    assert score == hangman.score_for("python", 1)
    out = capsys.readouterr().out
    assert "already tried" in out
    assert "Wrong guesses left: 5" in out
    assert "Wrong guesses left: 4" not in out


def test_play_repeated_correct_letter_costs_no_life(monkeypatch, fake_input):
    score = _play_with_word(monkeypatch, fake_input, "python", ["p", "p", "y", "t", "h", "o", "n"])
    assert score == hangman.score_for("python", 0)


@pytest.mark.parametrize("wrong_letters", [["x"], ["x", "z"], ["x", "z", "q"]])
def test_play_each_new_wrong_letter_costs_exactly_one_life(
    monkeypatch, fake_input, wrong_letters
):
    answers = wrong_letters + ["p", "y", "t", "h", "o", "n"]
    score = _play_with_word(monkeypatch, fake_input, "python", answers)
    assert score == hangman.score_for("python", len(wrong_letters))


def test_play_same_letter_in_different_case_is_a_repeat(monkeypatch, fake_input, capsys):
    score = _play_with_word(
        monkeypatch, fake_input, "python", ["X", "x", "p", "y", "t", "h", "o", "n"]
    )
    assert score == hangman.score_for("python", 1)
    assert "already tried" in capsys.readouterr().out


def test_play_six_distinct_wrong_letters_loses_the_game(monkeypatch, fake_input, capsys):
    score = _play_with_word(monkeypatch, fake_input, "python", ["a", "b", "c", "d", "e", "f"])
    assert score == 0
    assert "Out of guesses" in capsys.readouterr().out


def test_play_repeats_do_not_count_towards_the_six(monkeypatch, fake_input):
    # Five real misses plus many repeats, then solve: the game must not end early.
    answers = ["a", "a", "b", "b", "c", "c", "d", "d", "e", "e", "p", "y", "t", "h", "o", "n"]
    score = _play_with_word(monkeypatch, fake_input, "python", answers)
    assert score == hangman.score_for("python", 5)


def test_play_same_seed_and_inputs_replay_identically(monkeypatch, fake_input):
    answers = ["x", "p", "x", "y", "t", "h", "o", "n"]
    first = _play_with_word(monkeypatch, fake_input, "python", list(answers), seed=7)
    second = _play_with_word(monkeypatch, fake_input, "python", list(answers), seed=7)
    assert first == second
