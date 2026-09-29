"""Tests for Tic Tac Toe."""

import copy

import pytest

from arcade.games import tictactoe as ttt


DRAW_BOARD = ["X", "X", "O", "O", "O", "X", "X", "O", "X"]

PLAYER_WIN_BOARD = ["X", "X", "X", "O", "O", " ", " ", " ", " "]

COMPUTER_WIN_BOARD = ["O", "O", "O", "X", "X", " ", " ", " ", " "]

# Full boards where the player has a line and the computer does not.
PLAYER_WIN_FULL_BOARDS = [
    ["X", "X", "X", "O", "O", "X", "X", "O", "O"],
    ["X", "O", "O", "O", "X", "O", "O", "X", "X"],
]

# Full boards where the computer has a line and the player does not.
COMPUTER_WIN_FULL_BOARDS = [
    ["O", "O", "O", "X", "X", "O", "O", "X", "X"],
    ["O", "X", "X", "X", "O", "X", "X", "O", "O"],
]

# Every winning line filled with X, everything else empty: always a player win.
PLAYER_WIN_BOARDS = [
    [ttt.PLAYER if i in line else ttt.EMPTY for i in range(9)]
    for line in ttt.WINNING_LINES
]

# Every winning line filled with O, everything else empty: always a computer win.
COMPUTER_WIN_BOARDS = [
    [ttt.COMPUTER if i in line else ttt.EMPTY for i in range(9)]
    for line in ttt.WINNING_LINES
]

# Full boards with no three in a row: always a draw.
DRAW_BOARDS = [
    DRAW_BOARD,
    ["X", "O", "X", "X", "O", "O", "O", "X", "X"],
    ["O", "X", "O", "O", "X", "X", "X", "O", "O"],
]


def test_a_new_board_is_empty():
    assert ttt.new_board() == [ttt.EMPTY] * 9


def test_detects_a_winning_row():
    board = ["X", "X", "X", " ", " ", " ", " ", " ", " "]
    assert ttt.winner(board) == "X"


def test_detects_a_winning_column():
    board = ["O", " ", " ", "O", " ", " ", "O", " ", " "]
    assert ttt.winner(board) == "O"


def test_detects_a_winning_diagonal():
    board = ["X", " ", " ", " ", "X", " ", " ", " ", "X"]
    assert ttt.winner(board) == "X"


def test_no_winner_on_an_empty_board():
    assert ttt.winner(ttt.new_board()) is None


def test_three_empty_squares_in_a_line_do_not_count_as_a_win():
    assert ttt.winner([" "] * 9) is None


def test_free_squares_lists_only_empty_ones():
    board = ["X", " ", "O", " ", " ", " ", " ", " ", " "]
    assert ttt.free_squares(board) == [1, 3, 4, 5, 6, 7, 8]


def test_is_full_is_false_with_a_gap():
    assert ttt.is_full(["X"] * 8 + [" "]) is False


def test_is_full_is_true_with_no_gaps():
    assert ttt.is_full(["X", "O"] * 4 + ["X"]) is True


def test_the_computer_only_plays_free_squares():
    board = ["X", "O", "X", "O", " ", "O", "X", "O", "X"]
    assert ttt.computer_move(board) == 4


def test_render_shows_numbers_for_empty_squares():
    output = ttt.render(ttt.new_board())
    for number in range(1, 10):
        assert str(number) in output


# --- outcome_message ---------------------------------------------------------


def test_draw_fixture_boards_are_full_with_no_winner():
    for board in DRAW_BOARDS:
        assert ttt.is_full(board)
        assert ttt.winner(board) is None


@pytest.mark.parametrize("board", PLAYER_WIN_BOARDS + PLAYER_WIN_FULL_BOARDS)
def test_outcome_message_player_win(board):
    assert ttt.outcome_message(board) == "You win!"


@pytest.mark.parametrize("board", COMPUTER_WIN_BOARDS + COMPUTER_WIN_FULL_BOARDS)
def test_outcome_message_computer_win(board):
    assert ttt.outcome_message(board) == "The computer wins!"


@pytest.mark.parametrize("board", DRAW_BOARDS)
def test_outcome_message_draw(board):
    assert ttt.outcome_message(board) == "It's a draw!"


@pytest.mark.parametrize(
    "board",
    [
        ttt.new_board(),
        [ttt.PLAYER] + [ttt.EMPTY] * 8,
        [ttt.PLAYER, ttt.COMPUTER] + [ttt.EMPTY] * 7,
    ],
)
def test_outcome_message_game_still_on(board):
    assert ttt.outcome_message(board) == "The game is still on."


@pytest.mark.parametrize(
    "board",
    DRAW_BOARDS + PLAYER_WIN_FULL_BOARDS + COMPUTER_WIN_FULL_BOARDS + [ttt.new_board()],
)
def test_outcome_message_never_mentions_none(board):
    assert "None" not in ttt.outcome_message(board)


@pytest.mark.parametrize("length", [0, 1, 8, 10, 27])
def test_outcome_message_rejects_wrong_length(length):
    board = [ttt.EMPTY] * length
    with pytest.raises(ValueError):
        ttt.outcome_message(board)


@pytest.mark.parametrize("bad_mark", ["x", "o", "", "1", "XO"])
def test_outcome_message_rejects_invalid_marks(bad_mark):
    board = [ttt.EMPTY] * 8 + [bad_mark]
    with pytest.raises(ValueError):
        ttt.outcome_message(board)


def test_outcome_message_failure_leaves_board_untouched_and_next_call_works():
    bad_board = [ttt.EMPTY] * 8
    snapshot = copy.deepcopy(bad_board)
    with pytest.raises(ValueError):
        ttt.outcome_message(bad_board)
    assert bad_board == snapshot
    assert ttt.outcome_message(DRAW_BOARD) == "It's a draw!"


def test_outcome_message_does_not_mutate_the_board():
    for board in DRAW_BOARDS + PLAYER_WIN_FULL_BOARDS + COMPUTER_WIN_FULL_BOARDS:
        snapshot = copy.deepcopy(board)
        ttt.outcome_message(board)
        assert board == snapshot


def test_outcome_message_is_deterministic_across_repeated_calls():
    first = ttt.outcome_message(DRAW_BOARD)
    for _ in range(5):
        assert ttt.outcome_message(list(DRAW_BOARD)) == first


# --- full games --------------------------------------------------------------


def _run_scripted_game(fake_input, monkeypatch, player_moves, computer_moves):
    """Play one full game with scripted moves for both sides."""
    fake_input([str(move) for move in player_moves])
    replies = iter(computer_moves)
    monkeypatch.setattr(ttt, "computer_move", lambda board: next(replies))
    return ttt.play()


# Player 1-9 keypad moves, computer 0-based indexes, leading to a full board
# with no three in a row.
DRAW_SCRIPT = ([1, 9, 7, 6, 2], [4, 2, 3, 7])
PLAYER_WIN_SCRIPT = ([1, 2, 3], [3, 4])
COMPUTER_WIN_SCRIPT = ([4, 5, 7], [0, 1, 2])


def test_play_draw_announces_a_draw(fake_input, monkeypatch, capsys):
    score = _run_scripted_game(fake_input, monkeypatch, *DRAW_SCRIPT)
    output = capsys.readouterr().out
    assert score == 0
    assert "draw" in output.lower()
    assert "None" not in output


def test_play_player_win_announces_you_win(fake_input, monkeypatch, capsys):
    score = _run_scripted_game(fake_input, monkeypatch, *PLAYER_WIN_SCRIPT)
    output = capsys.readouterr().out
    assert score == 100
    assert "You win!" in output
    assert "None" not in output


def test_play_computer_win_announces_computer_win(fake_input, monkeypatch, capsys):
    score = _run_scripted_game(fake_input, monkeypatch, *COMPUTER_WIN_SCRIPT)
    output = capsys.readouterr().out
    assert score == 0
    assert "computer wins" in output.lower()
    assert "None" not in output


def test_play_same_script_replays_identically(fake_input, monkeypatch, capsys):
    first_score = _run_scripted_game(fake_input, monkeypatch, *DRAW_SCRIPT)
    first_output = capsys.readouterr().out
    second_score = _run_scripted_game(fake_input, monkeypatch, *DRAW_SCRIPT)
    second_output = capsys.readouterr().out
    assert first_score == second_score
    assert first_output == second_output


def test_play_consecutive_rounds_are_independent(fake_input, monkeypatch, capsys):
    scores = [
        _run_scripted_game(fake_input, monkeypatch, *PLAYER_WIN_SCRIPT),
        _run_scripted_game(fake_input, monkeypatch, *DRAW_SCRIPT),
        _run_scripted_game(fake_input, monkeypatch, *COMPUTER_WIN_SCRIPT),
    ]
    output = capsys.readouterr().out
    assert scores == [100, 0, 0]
    assert "None" not in output


def test_play_reprompts_on_taken_square_then_recovers(fake_input, monkeypatch, capsys):
    # Square 4 is taken by the computer's first move; the player retries.
    score = _run_scripted_game(fake_input, monkeypatch, [1, 4, 2, 3], [3, 4])
    output = capsys.readouterr().out
    assert score == 100
    assert "That square is taken" in output
    assert "You win!" in output


def test_play_reprompts_on_out_of_range_input_then_recovers(fake_input, monkeypatch, capsys):
    score = _run_scripted_game(fake_input, monkeypatch, [0, 10, 1, 2, 3], [3, 4])
    output = capsys.readouterr().out
    assert score == 100
    assert "You win!" in output
