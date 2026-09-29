"""Keeps track of high scores between sessions.

Scores are stored as JSON in the player's home directory, so they survive
closing the terminal. The file is created the first time a score is saved.
"""

from __future__ import annotations

import json
import math
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

SCORES_PATH = Path.home() / ".terminal-arcade" / "scores.json"


def load_scores(path: Path | None = None) -> list[dict[str, Any]]:
    """Read every saved score.

    A corrupt or unreadable file is treated as empty rather than crashing the
    arcade — losing a scoreboard is annoying, losing the whole game is worse.

    Args:
        path: Where to read from. Defaults to the player's scores file.

    Returns:
        A list of score entries. Empty if nothing has been saved yet.
    """
    target = path or SCORES_PATH
    if not target.exists():
        return []
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    return data


def _numeric_score(value: Any) -> float | None:
    """Best-effort conversion of a stored score to a number.

    Old score files kept scores as text, and hand-edited files may contain
    junk. Such values are reported as ``None`` and sorted last instead of
    raising, so one bad entry can never take down the arcade.

    Booleans are rejected on purpose: ``True``/``False`` are not meaningful
    game scores even though Python treats them as numbers.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str):
        try:
            number = float(value.strip())
        except ValueError:
            return None
    else:
        return None
    if not math.isfinite(number):
        return None
    return number


def save_score(
    game: str,
    player: str,
    score: int,
    path: Path | None = None,
) -> dict[str, Any]:
    """Add one score to the scoreboard and write it to disk.

    Args:
        game: Which game the score is for, e.g. "hangman".
        player: The player's name.
        score: The points scored. Higher is better.
        path: Where to write. Defaults to the player's scores file.

    Returns:
        The entry that was saved.
    """
    target = path or SCORES_PATH
    target.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "game": game,
        "player": player,
        "score": score,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    scores = load_scores(target)
    scores.append(entry)

    payload = json.dumps(scores, indent=2)
    # Build the new file in a sibling temporary file and rename it over the
    # old one. If writing is interrupted or fails halfway, the rename never
    # happens, so every score saved before this call is still on disk.
    fd, temp_name = tempfile.mkstemp(dir=target.parent, suffix=".tmp", prefix=target.name)
    temp_path = Path(temp_name)
    fd_owned = True
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            fd_owned = False
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, target)
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise
    finally:
        if fd_owned:
            try:
                os.close(fd)
            except OSError:
                pass
    return entry


def top_scores(
    game: str | None = None,
    limit: int = 5,
    path: Path | None = None,
) -> list[dict[str, Any]]:
    """Return the best scores, highest first.

    Args:
        game: Only show scores for this game. None means all games.
        limit: How many to return.
        path: Where to read from. Defaults to the player's scores file.

    Returns:
        Up to `limit` score entries, best first.
    """
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise TypeError("limit must be an integer")
    if limit < 0:
        raise ValueError("limit must not be negative")

    scores = load_scores(path)
    # Entries are expected to be objects. Anything else in a hand-edited file
    # is skipped rather than allowed to crash the lookup below.
    scores = [s for s in scores if isinstance(s, dict)]
    if game is not None:
        scores = [s for s in scores if s.get("game") == game]

    # Older score files stored the score as text (e.g. "50"); coercing to a
    # number keeps those entries ranking correctly. Unparseable entries get a
    # None key and sort last. The sort is stable, so ties keep file order and
    # identical input always yields identical output.
    keyed = [(entry, _numeric_score(entry.get("score", 0))) for entry in scores]
    # Valid numbers rank first (descending); unparseable entries rank last and
    # keep their original order thanks to the stable sort.
    ranked = [
        entry
        for entry, number in sorted(
            keyed,
            key=lambda pair: (pair[1] is not None, pair[1] if pair[1] is not None else 0.0),
            reverse=True,
        )
    ]
    return ranked[:limit]


def format_scoreboard(entries: list[dict[str, Any]]) -> str:
    """Render score entries as a plain text table.

    Args:
        entries: Score entries, already in the order you want them shown.

    Returns:
        A multi-line string ready to print.
    """
    if not entries:
        return "  No scores yet. Be the first."

    lines = [
        "  #  Player          Game            Score  Date",
        "  -  --------------  --------------  -----  ----------------",
    ]
    rendered = 0
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        rendered += 1
        player = str(entry.get("player", "?"))[:14]
        game = str(entry.get("game", "?"))[:14]
        score = str(entry.get("score", 0))
        date = entry.get("date", "")
        lines.append(f"  {rendered}  {player:<14}  {game:<14}  {score:>5}  {date}")
    return "\n".join(lines)
