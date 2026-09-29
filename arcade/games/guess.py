"""Guess the Number.

The computer picks a secret number and you try to find it. After each guess it
tells you whether to go higher or lower.
"""

from __future__ import annotations

import random

from arcade import art
from arcade.input_utils import ask_int

NAME = "Guess the Number"
DESCRIPTION = "Find the secret number in as few guesses as you can"

LOWEST = 1
HIGHEST = 100
MAX_GUESSES = 7


def score_for(guesses_used: int) -> int:
    """Work out a score from how many guesses the player needed.

    Fewer guesses is better, so the first guess is worth the most.

    Args:
        guesses_used: How many guesses the player took.

    Returns:
        Points, never below zero.
    """
    return max(0, (MAX_GUESSES - guesses_used + 1) * 10)


def evaluate(guess: int, secret: int) -> str:
    """Compare a guess with the secret number.

    Args:
        guess: What the player guessed.
        secret: The number they are trying to find.

    Returns:
        One of "correct", "too low", or "too high".
    """
    if guess == secret:
        return "correct"
    if guess < secret:
        return "too low"
    return "too high"


def play() -> int:
    """Run one round of Guess the Number.

    Returns:
        The player's score for this round.
    """
    print(art.GUESS_BANNER)
    print(f"  I am thinking of a number between {LOWEST} and {HIGHEST}.")
    print(f"  You have {MAX_GUESSES} guesses.\n")

    secret = random.randint(LOWEST, HIGHEST)

    for attempt in range(1, MAX_GUESSES + 1):
        remaining = MAX_GUESSES - attempt + 1
        guess = ask_int(
            f"  Guess {attempt}/{MAX_GUESSES} ({remaining} left):",
            minimum=LOWEST,
            maximum=HIGHEST,
        )

        result = evaluate(guess, secret)
        if result == "correct":
            points = score_for(attempt)
            print(art.green(f"\n  Got it. The number was {secret}."))
            print(f"  You found it in {attempt} guess(es) — {points} points.\n")
            return points

        if result == "too low":
            print(art.yellow("  Too low. Aim higher."))
        else:
            print(art.yellow("  Too high. Aim lower."))

    print(art.red(f"\n  Out of guesses. The number was {secret}.\n"))
    return 0
