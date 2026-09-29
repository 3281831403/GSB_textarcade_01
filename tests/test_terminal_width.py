"""Tests for fitting banners, rules, and the scoreboard to the terminal width."""

from __future__ import annotations

import copy
import shutil
from pathlib import Path

import pytest

from arcade import art, scoreboard

ARTWORK = "\n".join(
    [
        "",
        "  AAA   BBB ",
        " A   A  B  B",
        " AAAAA  BBB ",
        "",
    ]
)
ART_WIDTH = 12  # longest line in ARTWORK


@pytest.fixture
def width(monkeypatch):
    """Pretend the terminal is a fixed number of columns wide."""

    def _set(columns: int) -> None:
        monkeypatch.setattr(art, "terminal_width", lambda default=art.DEFAULT_WIDTH: columns)

    return _set


# --- terminal_width ----------------------------------------------------------


def test_terminal_width_uses_the_columns_environment_variable(monkeypatch):
    monkeypatch.setenv("COLUMNS", "123")
    assert art.terminal_width() == 123


def test_terminal_width_falls_back_when_there_is_no_terminal(monkeypatch):
    monkeypatch.delenv("COLUMNS", raising=False)

    def _no_terminal(fd: int):
        raise OSError("not a terminal")

    monkeypatch.setattr(shutil.os, "get_terminal_size", _no_terminal)
    assert art.terminal_width() == art.DEFAULT_WIDTH
    assert art.terminal_width(default=42) == 42


def test_terminal_width_ignores_a_garbage_columns_value(monkeypatch):
    monkeypatch.setenv("COLUMNS", "banana")
    monkeypatch.setattr(
        shutil.os,
        "get_terminal_size",
        lambda fd: (_ for _ in ()).throw(OSError("not a terminal")),
    )
    assert art.terminal_width() == art.DEFAULT_WIDTH


@pytest.mark.parametrize("columns", ["0", "-5"])
def test_terminal_width_is_never_less_than_one(monkeypatch, columns):
    monkeypatch.setenv("COLUMNS", columns)
    assert art.terminal_width() >= 1


def test_terminal_width_survives_an_os_level_failure(monkeypatch):
    def _boom(fallback=(80, 24)):
        raise RuntimeError("the OS refused to say")

    monkeypatch.setattr(shutil, "get_terminal_size", _boom)
    assert art.terminal_width() == art.DEFAULT_WIDTH


# --- fit_banner --------------------------------------------------------------


def test_wide_terminal_centres_the_banner(width):
    width(60)
    output = art.fit_banner(ARTWORK, "TITLE")
    lines = output.splitlines()
    assert "AAA" in output
    assert all(len(line) <= 60 for line in lines)
    # Centred: the art block is pushed right by (60 - 12) // 2 = 24 columns.
    assert lines[0].startswith(" " * 24)


@pytest.mark.parametrize("columns", [ART_WIDTH - 1, ART_WIDTH // 2, 5, 1])
def test_narrow_terminal_falls_back_to_a_plain_title(width, columns):
    width(columns)
    output = art.fit_banner(ARTWORK, "TITLE")
    assert "AAA" not in output
    assert "TITLE" in output


def test_banner_fits_exactly_at_its_own_width(width):
    width(ART_WIDTH)
    assert "AAA" in art.fit_banner(ARTWORK, "TITLE")


def test_banner_uses_the_fallback_width_when_the_terminal_is_unknown(monkeypatch):
    monkeypatch.delenv("COLUMNS", raising=False)
    monkeypatch.setattr(
        shutil.os,
        "get_terminal_size",
        lambda fd: (_ for _ in ()).throw(OSError("not a terminal")),
    )
    output = art.fit_banner(art.ARCADE_BANNER, "TERMINAL ARCADE")
    assert "|_   _|" in output  # 80 columns is plenty for the art


def test_a_title_longer_than_the_width_is_returned_unchanged(width):
    width(3)
    assert art.fit_banner(ARTWORK, "A VERY LONG TITLE") == "A VERY LONG TITLE"


def test_fit_banner_is_deterministic_for_the_same_input(width):
    width(37)
    assert art.fit_banner(ARTWORK, "TITLE") == art.fit_banner(ARTWORK, "TITLE")


def test_fit_banner_tracks_a_terminal_resize(width):
    width(60)
    wide = art.fit_banner(ARTWORK, "TITLE")
    width(4)
    narrow = art.fit_banner(ARTWORK, "TITLE")
    assert "AAA" in wide
    assert "AAA" not in narrow


# --- rule --------------------------------------------------------------------


@pytest.mark.parametrize("columns", [20, 80, 137])
def test_rule_follows_the_terminal_width_by_default(width, columns):
    width(columns)
    assert len(art.rule()) == columns
    assert len(art.rule("=")) == columns


def test_rule_still_honours_an_explicit_width(width):
    width(120)
    assert art.rule(width=7) == "-" * 7


@pytest.mark.parametrize("columns", [0, -10])
def test_rule_with_a_nonpositive_width_is_empty(columns):
    assert art.rule(width=columns) == ""


# --- format_scoreboard -------------------------------------------------------

ENTRIES = [
    {"player": "asha", "game": "hangman", "score": 70, "date": "2026-10-05 15:30"},
    {"player": "ravi", "game": "guess", "score": 50, "date": "2026-10-04 09:12"},
]


def test_wide_scoreboard_shows_every_column(width):
    width(100)
    table = scoreboard.format_scoreboard(ENTRIES)
    assert "Date" in table
    assert "2026-10-05 15:30" in table
    assert "hangman" in table


def test_medium_scoreboard_drops_the_date_column(width):
    width(50)
    table = scoreboard.format_scoreboard(ENTRIES)
    assert "Date" not in table
    assert "2026-10-05" not in table
    assert "hangman" in table


@pytest.mark.parametrize("columns", [16, 24, 30, 43])
def test_narrow_scoreboard_drops_columns_without_wrapping(width, columns):
    width(columns)
    table = scoreboard.format_scoreboard(ENTRIES)
    assert "Game" not in table
    assert "Date" not in table
    assert "asha" in table
    assert "70" in table
    for line in table.splitlines():
        assert len(line) <= columns


def test_narrow_scoreboard_truncates_long_player_names(width):
    width(20)
    entries = [{"player": "a-very-long-player-name", "game": "g", "score": 5, "date": "d"}]
    for line in scoreboard.format_scoreboard(entries).splitlines():
        assert len(line) <= 20


def test_empty_scoreboard_message_does_not_depend_on_width(width):
    width(10)
    assert "No scores yet" in scoreboard.format_scoreboard([])


def test_format_scoreboard_does_not_mutate_the_entries(width):
    width(30)
    snapshot = copy.deepcopy(ENTRIES)
    scoreboard.format_scoreboard(ENTRIES)
    assert ENTRIES == snapshot


def test_format_scoreboard_is_deterministic_for_the_same_input(width):
    width(55)
    assert scoreboard.format_scoreboard(ENTRIES) == scoreboard.format_scoreboard(ENTRIES)


# --- save_score rollback -----------------------------------------------------


def test_a_failed_save_leaves_the_scoreboard_untouched(tmp_path, monkeypatch):
    path = tmp_path / "scores.json"
    scoreboard.save_score("guess", "asha", 50, path=path)
    snapshot = copy.deepcopy(scoreboard.load_scores(path))
    before = path.read_bytes()

    def _boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(Path, "write_text", _boom)
    with pytest.raises(OSError):
        scoreboard.save_score("guess", "ravi", 60, path=path)

    assert scoreboard.load_scores(path) == snapshot
    assert path.read_bytes() == before
    assert not (tmp_path / "scores.json.tmp").exists()


def test_a_successful_save_works_right_after_a_failed_one(tmp_path, monkeypatch):
    path = tmp_path / "scores.json"
    scoreboard.save_score("guess", "asha", 50, path=path)

    monkeypatch.setattr(
        Path,
        "write_text",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("disk full")),
    )
    with pytest.raises(OSError):
        scoreboard.save_score("guess", "ravi", 60, path=path)
    monkeypatch.undo()

    scoreboard.save_score("guess", "ravi", 60, path=path)
    saved = scoreboard.load_scores(path)
    assert [e["player"] for e in saved] == ["asha", "ravi"]


def test_consecutive_saves_accumulate_in_order(tmp_path):
    path = tmp_path / "scores.json"
    for round_number in range(5):
        scoreboard.save_score("guess", f"p{round_number}", round_number * 10, path=path)
    saved = scoreboard.load_scores(path)
    assert [e["player"] for e in saved] == [f"p{i}" for i in range(5)]


def test_the_same_save_sequence_replays_identically(tmp_path):
    first = tmp_path / "a.json"
    second = tmp_path / "b.json"
    for target in (first, second):
        for player, score in [("asha", 50), ("ravi", 60), ("meena", 40)]:
            scoreboard.save_score("guess", player, score, path=target)
    replay_a = [{k: v for k, v in e.items() if k != "date"} for e in scoreboard.load_scores(first)]
    replay_b = [{k: v for k, v in e.items() if k != "date"} for e in scoreboard.load_scores(second)]
    assert replay_a == replay_b
