"""Tests for the art helpers."""

from arcade import art


def test_banner_draws_a_box_around_the_text():
    output = art.banner("HELLO")
    lines = output.splitlines()
    assert len(lines) == 3
    assert "HELLO" in lines[1]
    assert lines[0] == lines[2]


def test_banner_box_lines_are_all_the_same_width():
    lines = art.banner("TIC TAC TOE").splitlines()
    assert len({len(line) for line in lines}) == 1


def test_rule_has_the_requested_width():
    assert len(art.rule(width=20)) == 20


def test_colour_is_skipped_when_no_color_is_set(no_colour):
    assert art.green("plain") == "plain"


def test_there_are_seven_gallows_stages():
    assert len(art.GALLOWS) == 7
