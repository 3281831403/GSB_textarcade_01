"""Hangman.

Guess the hidden word one letter at a time. Six wrong guesses and the drawing
is finished.
"""

from __future__ import annotations

import random

from arcade import art
from arcade.input_utils import ask_letter

NAME = "Hangman"
DESCRIPTION = "Guess the word before the drawing is finished"

MAX_WRONG = 6

WORDS = [
    "python",
    "commit",
    "branch",
    "merge",
    "repository",
    "terminal",
    "variable",
    "function",
    "keyboard",
    "compile",
    "debug",
    "syntax",
    "pointer",
    "recursion",
    "boolean",
    "iterate",
    "package",
    "version",
]


def mask_word(word: str, guessed: set[str]) -> str:
    """Show the word with unguessed letters hidden.

    Args:
        word: The secret word.
        guessed: Letters the player has already guessed.

    Returns:
        The word with underscores for letters not yet found, spaced out so it
        is readable, e.g. "p _ t h _ n".
    """
    return " ".join(letter if letter in guessed else "_" for letter in word)


def is_solved(word: str, guessed: set[str]) -> bool:
    """Return True if every letter in the word has been guessed."""
    return all(letter in guessed for letter in word)


def apply_guess(word: str, guessed: set[str], letter: str) -> tuple[set[str], str]:
    """Apply one guessed letter to the game state.

    Matching ignores capital letters, so "A" and "a" are the same guess.
    Guessing a letter that was already tried is a "repeat" and costs no
    life; only a brand-new wrong letter is a "miss".

    Args:
        word: The secret word, letters only.
        guessed: Letters the player has already tried. Never mutated —
            the updated set is returned instead, so a rejected guess
            leaves the caller's state exactly as it was.
        letter: The letter the player just typed.

    Returns:
        An (updated_guessed, outcome) pair, where outcome is one of
        "hit", "miss", or "repeat". On "repeat" the updated set holds
        the same letters as `guessed`.

    Raises:
        ValueError: If `word` is not a non-empty string of letters, or
            `letter` is not exactly one alphabetic character.
    """
    if not isinstance(word, str) or not word or not word.isalpha():
        raise ValueError(f"word must be a non-empty string of letters, got {word!r}")
    if not isinstance(letter, str) or len(letter) != 1 or not letter.isalpha():
        raise ValueError(f"letter must be exactly one alphabetic character, got {letter!r}")

    normalized = letter.lower()
    if normalized in guessed:
        return set(guessed), "repeat"

    updated = set(guessed)
    updated.add(normalized)
    return updated, "hit" if normalized in word else "miss"


def score_for(word: str, wrong: int) -> int:
    """Score a completed game.

    Longer words and fewer mistakes score higher.

    Args:
        word: The word that was being guessed.
        wrong: How many wrong guesses the player made.

    Returns:
        Points, never below zero.
    """
    return max(0, len(word) * 10 - wrong * 10)


def play(rng: random.Random | None = None) -> int:
    """Run one round of Hangman.

    Args:
        rng: Optional random source for picking the word. Pass
            random.Random(seed) for a deterministic pick; by default the
            module-level randomness is used so real games vary.

    Returns:
        The player's score for this round.
    """
    print(art.HANGMAN_BANNER)

    word = (rng if rng is not None else random).choice(WORDS)
    guessed: set[str] = set()
    wrong = 0

    while wrong < MAX_WRONG and not is_solved(word, guessed):
        print(art.GALLOWS[wrong])
        print(f"\n  Word:  {art.bold(mask_word(word, guessed))}")
        print(f"  Wrong guesses left: {MAX_WRONG - wrong}")
        if guessed:
            print(f"  Already tried: {' '.join(sorted(guessed))}")
        print()

        letter = ask_letter("  Guess a letter:")

        guessed, outcome = apply_guess(word, guessed, letter)

        if outcome == "repeat":
            print(art.yellow(f"  You already tried '{letter}' — that one is free."))
        elif outcome == "hit":
            print(art.green(f"  Yes — '{letter}' is in the word."))
        else:
            wrong += 1
            print(art.red(f"  No — '{letter}' is not in the word."))

    print(art.GALLOWS[min(wrong, MAX_WRONG)])

    if is_solved(word, guessed):
        points = score_for(word, wrong)
        print(art.green(f"\n  You got it. The word was '{word}'."))
        print(f"  {points} points.\n")
        return points

    print(art.red(f"\n  Out of guesses. The word was '{word}'.\n"))
    return 0
