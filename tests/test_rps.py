"""Tests for Rock Paper Scissors."""

import pytest

from arcade.games import rps


@pytest.mark.parametrize(
    "player,computer",
    [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")],
)
def test_player_wins_the_expected_matchups(player, computer):
    assert rps.decide(player, computer) == "player"


@pytest.mark.parametrize(
    "player,computer",
    [("scissors", "rock"), ("rock", "paper"), ("paper", "scissors")],
)
def test_computer_wins_the_expected_matchups(player, computer):
    assert rps.decide(player, computer) == "computer"


@pytest.mark.parametrize("move", rps.MOVES)
def test_the_same_move_is_always_a_draw(move):
    assert rps.decide(move, move) == "draw"


def test_every_move_beats_exactly_one_other_move():
    for move in rps.MOVES:
        losers = [other for other in rps.MOVES if rps.decide(move, other) == "player"]
        assert len(losers) == 1
