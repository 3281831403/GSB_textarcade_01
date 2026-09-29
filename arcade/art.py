"""ASCII banners and terminal colours.

No external libraries. Colours are plain ANSI escape codes, which every modern
terminal understands (including Windows Terminal and PowerShell).

If you are adding a banner for a new game, keep it under 60 characters wide so
it does not wrap on a small terminal.
"""

from __future__ import annotations

import os
import shutil
import sys

# --- Colours -----------------------------------------------------------------

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"


def colours_supported() -> bool:
    """Return True if we should emit colour codes.

    Respects the NO_COLOR convention (https://no-color.org) and turns colour
    off when output is being piped to a file.
    """
    if os.environ.get("NO_COLOR"):
        return False
    if not sys.stdout.isatty():
        return False
    return True


def colour(text: str, code: str) -> str:
    """Wrap `text` in an ANSI colour, or return it unchanged if colour is off."""
    if not colours_supported():
        return text
    return f"{code}{text}{RESET}"


def red(text: str) -> str:
    return colour(text, RED)


def green(text: str) -> str:
    return colour(text, GREEN)


def yellow(text: str) -> str:
    return colour(text, YELLOW)


def cyan(text: str) -> str:
    return colour(text, CYAN)


def bold(text: str) -> str:
    return colour(text, BOLD)


def dim(text: str) -> str:
    return colour(text, DIM)


# --- Terminal size -----------------------------------------------------------

#: Width to assume when the real terminal size cannot be discovered (for
#: example when output is piped to a file and COLUMNS is not set).
DEFAULT_WIDTH = 80


def terminal_width(default: int = DEFAULT_WIDTH) -> int:
    """Return the current terminal width in columns.

    This never raises: if there is no real terminal (output is piped, the
    COLUMNS variable is missing or garbage, or the OS call fails) the
    `default` width is used instead. The size is looked up on every call, so
    resizing the terminal mid-game is picked up immediately.

    Args:
        default: Width to fall back on when the real size is unknown.

    Returns:
        A positive number of columns.
    """
    try:
        fallback = (max(1, int(default)), 24)
    except (TypeError, ValueError):
        fallback = (DEFAULT_WIDTH, 24)
    try:
        columns = shutil.get_terminal_size(fallback=fallback).columns
    except Exception:
        columns = fallback[0]
    try:
        columns = int(columns)
    except (TypeError, ValueError):
        columns = fallback[0]
    return max(1, columns)


# --- Banners -----------------------------------------------------------------

ARCADE_BANNER = r"""
  _____                  _             _
 |_   _|__ _ _ _ __  ___(_)_ _  __ _ | |
   | |/ -_) '_| '  \/ -_) | ' \/ _` || |
   |_|\___|_| |_|_|_\___|_|_||_\__,_||_|
         _   ___  ___   _   ___  ___
        /_\ | _ \/ __| /_\ |   \| __|
       / _ \|   / (__ / _ \| |) | _|
      /_/ \_\_|_\\___/_/ \_\___/|___|
"""

GUESS_BANNER = r"""
   ___                   _   _
  / __|_  _ ___ ______  | |_| |_  ___
 | (_ | || / -_|_-<_-<  |  _| ' \/ -_)
  \___|\_,_\___/__/__/   \__|_||_\___|
        _  _             _
       | \| |_  _ _ __ | |__  ___ _ _
       | .` | || | '  \| '_ \/ -_) '_|
       |_|\_|\_,_|_|_|_|_.__/\___|_|
"""

HANGMAN_BANNER = r"""
  _  _                                 
 | || |__ _ _ _  __ _ _ __  __ _ _ _   
 | __ / _` | ' \/ _` | '  \/ _` | ' \  
 |_||_\__,_|_||_\__, |_|_|_\__,_|_||_| 
                |___/                  
"""

RPS_BANNER = r"""
  ___         _     ___                  
 | _ \___  __| |__ | _ \__ _ _ __  ___ _ _ 
 |   / _ \/ _| / / |  _/ _` | '_ \/ -_) '_|
 |_|_\___/\__|_\_\ |_| \__,_| .__/\___|_|  
     ___     _              |_|            
    / __| __(_)_______ ___ _ _ ___         
    \__ \/ _| |_ / _ (_-< _ \ '_(_-<       
    |___/\__|_/__\___/__/___/_| /__/       
"""

# TODO: Tic Tac Toe has no banner yet. See the open issue if you would like to
# add one — it is a good first contribution.

GALLOWS = [
    # 0 wrong guesses through 6 (lost)
    r"""
     +---+
     |   |
         |
         |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
         |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
     |   |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
    /|\  |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
    /|\  |
    /    |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
    /|\  |
    / \  |
         |
    =========""",
]


def banner(text: str) -> str:
    """Return a simple boxed banner for text that has no ASCII art of its own."""
    width = len(text) + 4
    top = "+" + "-" * (width - 2) + "+"
    middle = f"| {text} |"
    return f"{top}\n{middle}\n{top}"


def fit_banner(artwork: str, title: str, width: int | None = None) -> str:
    """Fit ASCII art to the terminal, degrading to plain text when narrow.

    If the art fits inside the current width it is centred as a block. If the
    terminal is too narrow — where the art would wrap into unreadable noise —
    a plain text title is returned instead.

    Args:
        artwork: The ASCII art, usually one of the *_BANNER constants.
        title: Plain text to fall back to when the art does not fit.
        width: Columns available. None means the real terminal width.

    Returns:
        The centred art, or the plain title when space is tight.
    """
    if width is None:
        width = terminal_width()
    width = max(1, int(width))

    lines = artwork.strip("\n").splitlines()
    art_width = max((len(line) for line in lines), default=0)
    if 0 < art_width <= width:
        pad = " " * ((width - art_width) // 2)
        return "\n".join(pad + line for line in lines)

    if len(title) >= width:
        return title
    return title.center(width)


def rule(char: str = "-", width: int | None = None) -> str:
    """A horizontal divider line, as wide as the terminal by default.

    Args:
        char: The character to draw the line with.
        width: How long the line is. None means the current terminal width.
    """
    if width is None:
        width = terminal_width()
    return char * max(0, int(width))
