"""The arcade menu — pick a game, play it, come back to the menu.

Games are registered in GAMES below. Each entry points at a module that
provides NAME, DESCRIPTION, and a play() function returning a score.
"""

from __future__ import annotations

from types import ModuleType

from arcade import __version__, art, scoreboard
from arcade.games import guess, hangman, rps, tictactoe
from arcade.input_utils import ask, ask_int, confirm, pause

# Exit codes follow the usual terminal convention: 128 + signal number for an
# interrupted program (SIGINT is 2), and 0 when input simply runs out (EOF),
# the way `cat` or the shell's `read` do.
EXIT_INTERRUPTED = 130
EXIT_END_OF_INPUT = 0

# To add a game: write arcade/games/yourgame.py, import it above, and add it
# here. That is the whole process. See docs/how-to-add-a-game.md.
GAMES: list[ModuleType] = [
    guess,
    hangman,
    rps,
    tictactoe,
]


def show_menu() -> None:
    """Print the list of games and the extra options."""
    print(art.ARCADE_BANNER)
    print(art.dim(f"  v{__version__}  ·  github-community-gitam\n"))

    for number, game in enumerate(GAMES, start=1):
        print(f"  {number}. {art.bold(game.NAME)}")
        print(f"     {art.dim(game.DESCRIPTION)}")

    print(f"\n  {len(GAMES) + 1}. High scores")
    print(f"  {len(GAMES) + 2}. Quit\n")


def show_high_scores() -> None:
    """Print the overall top scores."""
    print(f"\n{art.bold('  HIGH SCORES')}\n")
    print(scoreboard.format_scoreboard(scoreboard.top_scores(limit=10)))
    print()


def run_game(game: ModuleType) -> None:
    """Play one game and offer to save the score.

    Args:
        game: A game module with NAME and play().
    """
    print()
    score = game.play()

    if score and score > 0:
        if confirm("  Save this score to the scoreboard?"):
            name = ask("  Your name:").strip() or "anonymous"
            scoreboard.save_score(game.NAME, name, score)
            print(art.green("  Saved.\n"))


def main() -> None:
    """Start the arcade. Loops until the player chooses to quit."""
    quit_option = len(GAMES) + 2
    scores_option = len(GAMES) + 1

    try:
        while True:
            show_menu()
            choice = ask_int("  What would you like to play?", minimum=1, maximum=quit_option)

            if choice == quit_option:
                print(art.cyan("\n  Thanks for playing. See you next time.\n"))
                return

            if choice == scores_option:
                show_high_scores()
                pause()
                continue

            run_game(GAMES[choice - 1])
            pause()
    except KeyboardInterrupt:
        # Ctrl+C at any prompt — in the menu, inside a game, at a confirmation
        # or a pause. Every input helper reads through input(), so a single
        # handler here covers all of them.
        print(art.cyan("\n\n  Interrupted. Thanks for playing — see you next time.\n"))
        raise SystemExit(EXIT_INTERRUPTED)
    except EOFError:
        # Ctrl+D or piped input ending. No more questions can be answered, so
        # this is a calm goodbye rather than a crash with a traceback.
        print(art.cyan("\n  End of input. Thanks for playing — see you next time.\n"))
        raise SystemExit(EXIT_END_OF_INPUT)


if __name__ == "__main__":
    main()
