"""Tests for the Hangman game."""

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
