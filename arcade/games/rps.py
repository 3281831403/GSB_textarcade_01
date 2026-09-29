"""Rock Paper Scissors.

Best of five against the computer.
"""

from __future__ import annotations

import random

from arcade import art
from arcade.input_utils import ask_choice

NAME = "Rock Paper Scissors"
DESCRIPTION = "Best of five against the computer"

MOVES = ["rock", "paper", "scissors"]
ROUNDS = 5

# What each move defeats.
BEATS = {
    "rock": "scissors",
    "paper": "rock",
    "scissors": "paper",
}

EMOJI = {
    "rock": "(rock)",
    "paper": "(paper)",
    "scissors": "(scissors)",
}


def decide(player: str, computer: str) -> str:
    """Work out who won a single round.

    Args:
        player: The player's move.
        computer: The computer's move.

    Returns:
        "player", "computer", or "draw".
    """
    if player == computer:
        return "draw"
    if BEATS[player] == computer:
        return "player"
    return "computer"


def play() -> int:
    """Run one best-of-five match.

    Returns:
        The player's score: 20 points per round won.
    """
    print(art.RPS_BANNER)
    print(f"  First to win the most of {ROUNDS} rounds.\n")

    player_wins = 0
    computer_wins = 0

    for round_number in range(1, ROUNDS + 1):
        print(art.rule())
        print(
            f"  Round {round_number} of {ROUNDS}   (you {player_wins} — {computer_wins} computer)\n"
        )

        player_move = ask_choice("  Your move?", MOVES)
        computer_move = random.choice(MOVES)

        print(f"\n  You:      {EMOJI[player_move]} {player_move}")
        print(f"  Computer: {EMOJI[computer_move]} {computer_move}\n")

        outcome = decide(player_move, computer_move)
        if outcome == "player":
            player_wins += 1
            print(art.green(f"  You win the round — {player_move} beats {computer_move}."))
        elif outcome == "computer":
            computer_wins += 1
            print(art.red(f"  Computer wins — {computer_move} beats {player_move}."))
        else:
            print(art.yellow("  A draw. Nobody scores."))
        print()

    print(art.rule("="))
    print(f"  Final score — you {player_wins}, computer {computer_wins}\n")

    if player_wins > computer_wins:
        print(art.green("  You win the match.\n"))
    elif computer_wins > player_wins:
        print(art.red("  The computer wins the match.\n"))
    else:
        print(art.yellow("  The match is a draw.\n"))

    return player_wins * 20
