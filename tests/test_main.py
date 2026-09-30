"""Tests for the arcade menu itself."""

import builtins
import copy
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from arcade import main


def _scripted(monkeypatch, script):
    """Feed answers/exceptions to input(), like the shared fake_input fixture."""
    queue = list(script)

    def _fake(prompt: str = "") -> str:
        if not queue:
            raise AssertionError(f"The code asked for more input than scripted: {prompt!r}")
        item = queue.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    monkeypatch.setattr(builtins, "input", _fake)
    return _fake


INTERRUPTIONS = [
    pytest.param(EOFError(), main.EXIT_END_OF_INPUT, "End of input", id="eof"),
    pytest.param(
        KeyboardInterrupt(), main.EXIT_INTERRUPTED, "Interrupted", id="keyboard-interrupt"
    ),
]


@pytest.mark.parametrize("failure,exit_code,farewell", INTERRUPTIONS)
def test_interrupting_the_menu_exits_cleanly(monkeypatch, capsys, failure, exit_code, farewell):
    _scripted(monkeypatch, [failure])
    with pytest.raises(SystemExit) as excinfo:
        main.main()
    assert excinfo.value.code == exit_code
    output = capsys.readouterr().out
    assert farewell in output
    assert "Traceback" not in output


@pytest.mark.parametrize("failure,exit_code,farewell", INTERRUPTIONS)
def test_interrupting_inside_a_game_exits_cleanly(
    monkeypatch, capsys, failure, exit_code, farewell
):
    def _play():
        raise failure

    fake_game = SimpleNamespace(NAME="Fake", DESCRIPTION="A fake game", play=_play)
    monkeypatch.setattr(main, "GAMES", [fake_game])
    _scripted(monkeypatch, ["1"])

    with pytest.raises(SystemExit) as excinfo:
        main.main()
    assert excinfo.value.code == exit_code
    assert farewell in capsys.readouterr().out


@pytest.mark.parametrize("failure,exit_code,_farewell", INTERRUPTIONS)
def test_interrupting_a_pause_exits_cleanly(monkeypatch, failure, exit_code, _farewell):
    fake_game = SimpleNamespace(NAME="Fake", DESCRIPTION="A fake game", play=lambda: 0)
    monkeypatch.setattr(main, "GAMES", [fake_game])
    _scripted(monkeypatch, ["1", failure])

    with pytest.raises(SystemExit) as excinfo:
        main.main()
    assert excinfo.value.code == exit_code


@pytest.mark.parametrize("failure,exit_code,_farewell", INTERRUPTIONS)
def test_interrupting_a_confirmation_exits_cleanly(monkeypatch, failure, exit_code, _farewell):
    fake_game = SimpleNamespace(NAME="Fake", DESCRIPTION="A fake game", play=lambda: 50)
    monkeypatch.setattr(main, "GAMES", [fake_game])
    _scripted(monkeypatch, ["1", failure])

    with pytest.raises(SystemExit) as excinfo:
        main.main()
    assert excinfo.value.code == exit_code


def test_the_menu_can_run_for_several_rounds_before_ending(monkeypatch, capsys):
    fake_game = SimpleNamespace(NAME="Fake", DESCRIPTION="A fake game", play=lambda: 0)
    monkeypatch.setattr(main, "GAMES", [fake_game])
    quit_option = 3
    _scripted(monkeypatch, ["1", "", "1", "", "1", "", str(quit_option)])

    main.main()
    assert capsys.readouterr().out.count("Thanks for playing. See you next time.") == 1


def test_same_input_sequence_replays_identically(monkeypatch, capsys):
    def one_run():
        fake_game = SimpleNamespace(NAME="Fake", DESCRIPTION="A fake game", play=lambda: 0)
        monkeypatch.setattr(main, "GAMES", [fake_game])
        _scripted(monkeypatch, ["1", "", "3"])
        main.main()
        return capsys.readouterr().out

    assert one_run() == one_run()


def test_an_interrupted_save_rolls_back_then_the_next_save_succeeds(monkeypatch, tmp_path):
    scores_file = tmp_path / "scores.json"
    fake_game = SimpleNamespace(NAME="Fake", DESCRIPTION="A fake game", play=lambda: 50)
    monkeypatch.setattr(main, "GAMES", [fake_game])
    monkeypatch.setattr(main.scoreboard, "SCORES_PATH", scores_file)

    # Interrupted while asking for the name: nothing must have been written.
    _scripted(monkeypatch, ["1", "y", EOFError()])
    with pytest.raises(SystemExit) as excinfo:
        main.main()
    assert excinfo.value.code == main.EXIT_END_OF_INPUT
    assert not scores_file.exists()

    # The very next successful run must be unaffected and save normally.
    _scripted(monkeypatch, ["1", "y", "winner", "", "3"])
    main.main()
    saved = main.scoreboard.load_scores()
    assert len(saved) == 1
    assert saved[0]["player"] == "winner"
    assert saved[0]["score"] == 50


def test_interrupted_runs_leave_the_games_registry_unchanged(monkeypatch):
    before = copy.deepcopy([(g.NAME, g.DESCRIPTION) for g in main.GAMES])
    for failure in (EOFError(), KeyboardInterrupt()):
        _scripted(monkeypatch, [failure])
        with pytest.raises(SystemExit):
            main.main()
    after = [(g.NAME, g.DESCRIPTION) for g in main.GAMES]
    assert after == before


def test_normal_quit_still_returns_cleanly(monkeypatch, capsys):
    _scripted(monkeypatch, [str(len(main.GAMES) + 2)])
    assert main.main() is None
    assert "Thanks for playing" in capsys.readouterr().out


def _arcade_subprocess(inp=None, sigint=False):
    repo_root = Path(main.__file__).resolve().parent.parent
    if sigint:
        reader, writer = os.pipe()
        proc = subprocess.Popen(
            [sys.executable, "-m", "arcade"],
            cwd=repo_root,
            stdin=reader,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if inp:
            os.write(writer, inp.encode())
            time.sleep(0.2)
        time.sleep(0.5)
        proc.send_signal(signal.SIGINT)
        out, err = proc.communicate()
        os.close(reader)
        os.close(writer)
        return proc.returncode, out, err

    result = subprocess.run(
        [sys.executable, "-m", "arcade"],
        cwd=repo_root,
        input=inp.encode() if inp else b"",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.returncode, result.stdout, result.stderr


def test_end_of_input_as_a_real_process_exits_zero_without_a_traceback():
    code, _out, err = _arcade_subprocess(inp="1\n")
    assert code == 0
    assert not err


def test_ctrl_c_as_a_real_process_exits_130_without_a_traceback():
    code, out, err = _arcade_subprocess(inp="1\n", sigint=True)
    assert code == 130
    assert not err
    assert b"Interrupted" in out


def test_every_registered_game_has_a_name():
    for game in main.GAMES:
        assert isinstance(game.NAME, str) and game.NAME


def test_every_registered_game_has_a_description():
    for game in main.GAMES:
        assert isinstance(game.DESCRIPTION, str) and game.DESCRIPTION


def test_every_registered_game_is_playable():
    for game in main.GAMES:
        assert callable(game.play)


def test_game_names_are_unique():
    names = [game.NAME for game in main.GAMES]
    assert len(names) == len(set(names))


def test_the_menu_lists_every_game(capsys):
    main.show_menu()
    output = capsys.readouterr().out
    for game in main.GAMES:
        assert game.NAME in output


def test_the_menu_offers_high_scores_and_quit(capsys):
    main.show_menu()
    output = capsys.readouterr().out
    assert "High scores" in output
    assert "Quit" in output
