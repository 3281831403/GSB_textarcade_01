"""Tests for the scoreboard."""

import copy
import json
import os
from datetime import datetime

from arcade import scoreboard



def test_loading_a_missing_file_gives_an_empty_list(tmp_path):
    assert scoreboard.load_scores(tmp_path / "nothing.json") == []


def test_loading_a_corrupt_file_gives_an_empty_list_instead_of_crashing(tmp_path):
    broken = tmp_path / "scores.json"
    broken.write_text("{ this is not valid json", encoding="utf-8")
    assert scoreboard.load_scores(broken) == []


def test_saving_a_score_writes_it_to_disk(tmp_path):
    path = tmp_path / "scores.json"
    scoreboard.save_score("hangman", "asha", 70, path=path)
    saved = scoreboard.load_scores(path)
    assert len(saved) == 1
    assert saved[0]["player"] == "asha"
    assert saved[0]["score"] == 70


def test_a_saved_score_records_the_game_and_a_date(tmp_path):
    path = tmp_path / "scores.json"
    entry = scoreboard.save_score("guess", "ravi", 50, path=path)
    assert entry["game"] == "guess"
    assert entry["date"]


def test_scores_accumulate(tmp_path):
    path = tmp_path / "scores.json"
    scoreboard.save_score("guess", "a", 1, path=path)
    scoreboard.save_score("guess", "b", 2, path=path)
    assert len(scoreboard.load_scores(path)) == 2


def test_top_scores_puts_the_best_first(tmp_path):
    path = tmp_path / "scores.json"
    scoreboard.save_score("guess", "low", 3, path=path)
    scoreboard.save_score("guess", "high", 9, path=path)
    scoreboard.save_score("guess", "mid", 5, path=path)

    top = scoreboard.top_scores(path=path)
    assert [e["player"] for e in top] == ["high", "mid", "low"]


def test_top_scores_can_filter_by_game(tmp_path):
    path = tmp_path / "scores.json"
    scoreboard.save_score("guess", "a", 5, path=path)
    scoreboard.save_score("hangman", "b", 7, path=path)

    top = scoreboard.top_scores(game="hangman", path=path)
    assert len(top) == 1
    assert top[0]["player"] == "b"


def test_top_scores_respects_the_limit(tmp_path):
    path = tmp_path / "scores.json"
    for i in range(9):
        scoreboard.save_score("guess", f"p{i}", i, path=path)
    assert len(scoreboard.top_scores(limit=3, path=path)) == 3


def test_an_empty_scoreboard_renders_a_friendly_message():
    assert "No scores yet" in scoreboard.format_scoreboard([])


def test_the_scoreboard_table_includes_the_player_and_score():
    table = scoreboard.format_scoreboard(
        [{"player": "asha", "game": "hangman", "score": 70, "date": "2026-10-05 15:30"}]
    )
    assert "asha" in table
    assert "70" in table

# ---------------------------------------------------------------------------
# Numeric sorting, legacy text scores and corrupt data (the ranking bug fix)
# ---------------------------------------------------------------------------

import pytest


def _write_entries(path, entries):
    """Put raw entries straight on disk, bypassing save_score.

    This lets tests seed legacy or hand-edited files (text scores, junk).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries), encoding="utf-8")


def _score_of(top):
    return [e["score"] for e in top]


@pytest.mark.parametrize(
    "scores,expected",
    [
        # Two vs three digits: the original bug order was 9 then 100.
        ([100, 9], [100, 9]),
        ([9, 100], [100, 9]),
        # Two-digit scores.
        ([10, 42, 7], [42, 10, 7]),
        # Three-digit scores.
        ([300, 999, 100], [999, 300, 100]),
        # Out-of-order inserts across the two/three-digit boundary.
        ([1, 100, 9, 99, 10], [100, 99, 10, 9, 1]),
    ],
)
def test_top_scores_sorts_numerically_two_and_three_digits(tmp_path, scores, expected):
    path = tmp_path / "scores.json"
    for value in scores:
        scoreboard.save_score("guess", f"p{value}", value, path=path)
    assert _score_of(scoreboard.top_scores(limit=len(scores), path=path)) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        # Legacy text scores from older score files.
        (["100", "9"], ["100", "9"]),
        (["50"], ["50"]),
        (["50", "100", "9"], ["100", "50", "9"]),
        # Numeric and text forms of the same value tie and keep file order.
        ([50, "50"], [50, "50"]),
        (["50", 50], ["50", 50]),
        # Strings with surrounding whitespace still parse.
        ([" 12 ", "3"], [" 12 ", "3"]),
    ],
)
def test_top_scores_ranks_legacy_text_scores_numerically(tmp_path, raw, expected):
    path = tmp_path / "scores.json"
    entries = [
        {"game": "guess", "player": f"p{i}", "score": value, "date": "2026-01-01 00:00"}
        for i, value in enumerate(raw)
    ]
    _write_entries(path, entries)
    assert _score_of(scoreboard.top_scores(limit=len(raw), path=path)) == expected


@pytest.mark.parametrize(
    "bad",
    ["abc", "", "onehundred", None, [], {}, True, float("nan"), float("inf")],
)
def test_top_scores_never_crashes_on_bad_scores(tmp_path, bad):
    path = tmp_path / "scores.json"
    _write_entries(
        path,
        [
            {"game": "guess", "player": "ok", "score": 42, "date": "d"},
            {"game": "guess", "player": "junk", "score": bad, "date": "d"},
        ],
    )
    top = scoreboard.top_scores(path=path)
    assert top[0]["player"] == "ok"
    assert top[-1]["player"] == "junk"


def test_top_scores_ignores_non_dict_entries(tmp_path):
    path = tmp_path / "scores.json"
    _write_entries(path, [42, "garbage", None, {"game": "guess", "player": "ok", "score": 1}])
    top = scoreboard.top_scores(path=path)
    assert [e["player"] for e in top] == ["ok"]


# ---------------------------------------------------------------------------
# Boundaries, filters and invalid arguments
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("limit", [0, 1, 5])
def test_top_scores_handles_empty_single_and_boundary_limits(tmp_path, limit):
    path = tmp_path / "scores.json"
    assert scoreboard.top_scores(limit=limit, path=path) == []
    scoreboard.save_score("guess", "solo", 5, path=path)
    assert len(scoreboard.top_scores(limit=limit, path=path)) == min(limit, 1)


def test_top_scores_with_limit_zero_returns_empty(tmp_path):
    path = tmp_path / "scores.json"
    scoreboard.save_score("guess", "a", 10, path=path)
    assert scoreboard.top_scores(limit=0, path=path) == []


@pytest.mark.parametrize(
    "limit,error",
    [(-1, ValueError), (-10, ValueError), ("3", TypeError), (1.5, TypeError), (True, TypeError)],
)
def test_top_scores_rejects_invalid_limit_without_touching_disk(tmp_path, limit, error):
    path = tmp_path / "scores.json"
    _write_entries(path, [{"game": "guess", "player": "a", "score": 1, "date": "d"}])
    snapshot = copy.deepcopy(scoreboard.load_scores(path))
    with pytest.raises(error):
        scoreboard.top_scores(limit=limit, path=path)
    # Rejected call: state identical, field by field.
    assert copy.deepcopy(scoreboard.load_scores(path)) == snapshot


# ---------------------------------------------------------------------------
# Repeated calls, multiple rounds, deterministic replay
# ---------------------------------------------------------------------------

def test_repeated_top_scores_calls_are_stable(tmp_path):
    path = tmp_path / "scores.json"
    for value in (9, 100, 50, 9, 100):
        scoreboard.save_score("guess", f"p{value}", value, path=path)
    first = scoreboard.top_scores(limit=4, path=path)
    for _ in range(5):
        assert scoreboard.top_scores(limit=4, path=path) == first
    assert _score_of(first) == [100, 100, 50, 9]


def test_many_rounds_of_saving_and_ranking_remain_consistent(tmp_path):
    path = tmp_path / "scores.json"
    rounds = [12, 105, 7, 250, 9, 88]
    running_best = 0
    for value in rounds:
        scoreboard.save_score("guess", f"p{value}", value, path=path)
        running_best = max(running_best, value)
        assert scoreboard.top_scores(limit=1, path=path)[0]["score"] == running_best
    assert running_best == 250
    assert len(scoreboard.load_scores(path)) == len(rounds)


class _FrozenDateTime:
    @classmethod
    def now(cls):
        return datetime(2026, 1, 2, 3, 4)


def test_same_input_sequence_replays_byte_for_byte(tmp_path, monkeypatch):
    monkeypatch.setattr(scoreboard, "datetime", _FrozenDateTime)
    sequence = [("guess", "a", 9), ("guess", "b", 100), ("guess", "c", "50")]

    first = tmp_path / "first.json"
    second = tmp_path / "sub" / "second.json"
    for game, player, score in sequence:
        scoreboard.save_score(game, player, score, path=first)
    for game, player, score in sequence:
        scoreboard.save_score(game, player, score, path=second)

    assert first.read_text(encoding="utf-8") == second.read_text(encoding="utf-8")
    assert scoreboard.top_scores(limit=3, path=first) == scoreboard.top_scores(limit=3, path=second)


# ---------------------------------------------------------------------------
# Atomic writes: failure rolls back, later success is unaffected
# ---------------------------------------------------------------------------

def _save_with_tmp_failure(path, player, score, error):
    def _failing_mkstemp(*args, **kwargs):
        raise error

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(scoreboard.tempfile, "mkstemp", _failing_mkstemp)
        return scoreboard.save_score("guess", player, score, path=path)


def test_failed_save_rolls_back_and_a_later_save_succeeds(tmp_path, monkeypatch):
    path = tmp_path / "scores.json"
    scoreboard.save_score("guess", "keeper", 100, path=path)
    snapshot = copy.deepcopy(scoreboard.load_scores(path))

    # Resource exhaustion while creating the temporary file.
    with pytest.raises(OSError):
        _save_with_tmp_failure(path, "ghost", 200, OSError("No buffer space"))

    after = scoreboard.load_scores(path)
    assert after == snapshot
    assert not list(path.parent.glob("*.tmp"))

    # A successful call immediately after the failure is unaffected.
    scoreboard.save_score("guess", "survivor", 150, path=path)
    assert [e["player"] for e in scoreboard.load_scores(path)] == ["keeper", "survivor"]
    assert scoreboard.top_scores(limit=2, path=path)[0]["player"] == "survivor"


def test_mid_write_failure_leaves_previous_file_intact(tmp_path, monkeypatch):
    path = tmp_path / "scores.json"
    scoreboard.save_score("guess", "keeper", 100, path=path)
    snapshot_bytes = path.read_bytes()

    def _failing_fdopen(fd, *args, **kwargs):
        raise OSError("disk full")

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(scoreboard.os, "fdopen", _failing_fdopen)
        with pytest.raises(OSError):
            scoreboard.save_score("guess", "ghost", 200, path=path)

    assert path.read_bytes() == snapshot_bytes
    assert not list(path.parent.glob("*.tmp"))
    scoreboard.save_score("guess", "survivor", 150, path=path)
    assert scoreboard.top_scores(limit=1, path=path)[0]["score"] == 150


def test_save_score_raises_when_the_directory_cannot_be_created(tmp_path):
    blocker = tmp_path / "a-file"
    blocker.write_text("x", encoding="utf-8")
    target = blocker / "nested" / "scores.json"
    with pytest.raises(OSError):
        scoreboard.save_score("guess", "a", 1, path=target)
    assert not target.exists()
    # The blocker file is untouched.
    assert blocker.read_text(encoding="utf-8") == "x"


# ---------------------------------------------------------------------------
# Repeated reads and rendering robustness
# ---------------------------------------------------------------------------

def test_load_scores_returns_the_same_contents_on_repeated_reads(tmp_path):
    path = tmp_path / "scores.json"
    _write_entries(path, [{"game": "g", "player": "p", "score": 3, "date": "d"}])
    first = scoreboard.load_scores(path)
    assert scoreboard.load_scores(path) == first
    assert scoreboard.load_scores(path) == first


def test_format_scoreboard_renders_text_scores_and_skips_junk():
    entries = [
        {"player": "asha", "game": "guess", "score": "100", "date": "2026-01-01 00:00"},
        "not-an-entry",
        {"player": "bo", "game": "guess", "score": None, "date": "2026-01-01 00:00"},
    ]
    table = scoreboard.format_scoreboard(entries)
    assert "asha" in table
    assert "100" in table
    assert "bo" in table
    assert "\n  1  " in table
    assert "\n  2  " in table
    assert "\n  3  " not in table


def test_filtering_by_game_does_not_swallow_bad_scores(tmp_path):
    path = tmp_path / "scores.json"
    _write_entries(
        path,
        [
            {"game": "guess", "player": "g", "score": "9", "date": "d"},
            {"game": "rps", "player": "r", "score": 100, "date": "d"},
            {"game": "guess", "player": "bad", "score": "x", "date": "d"},
        ],
    )
    top = scoreboard.top_scores(game="guess", path=path)
    assert [e["player"] for e in top] == ["g", "bad"]
