<h1 align="center">Terminal Arcade</h1>

<p align="center">A collection of small games you play in your terminal.<br>
Built as a friendly place to make your first ever pull request.</p>

<p align="center">
  <img src="https://img.shields.io/badge/Hacktoberfest-2026-FF8AE2" alt="Hacktoberfest 2026">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/dependencies-none-1F883D" alt="No dependencies">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="MIT">
</p>

---

## Play it

You need **Python 3.10 or newer**. Nothing else — no `pip install`, no
dependencies, no setup.

```bash
git clone https://github.com/github-community-gitam/terminal-arcade.git
cd terminal-arcade
python3 -m arcade
```

```
  _____                  _             _
 |_   _|__ _ _ _ __  ___(_)_ _  __ _ | |
   | |/ -_) '_| '  \/ -_) | ' \/ _` || |
   |_|\___|_| |_|_|_\___|_|_||_\__,_||_|
         _   ___  ___   _   ___  ___
        /_\ | _ \/ __| /_\ |   \| __|
       / _ \|   / (__ / _ \| |) | _|
      /_/ \_\_|_\\___/_/ \_\___/|___|

  1. Guess the Number
     Find the secret number in as few guesses as you can
  2. Hangman
     Guess the word before the drawing is finished
  3. Rock Paper Scissors
     Best of five against the computer
  4. Tic Tac Toe
     The classic, against a computer that plays at random

  5. High scores
  6. Quit

  What would you like to play?
```

---

## 🎃 Contributing — read this bit

**This repository exists so you can make your first pull request.** That is not
marketing. The issues were written specifically for people who have never
contributed to open source before.

### The fastest way in

1. Browse [issues labelled `good first issue`](../../issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
2. Comment **`/claim`** on one — a bot assigns it to you within seconds
3. Read [CONTRIBUTING.md](CONTRIBUTING.md)
4. Open a pull request with `Closes #<issue number>` in the description

### Three kinds of work here

| | |
|---|---|
| 🎮 **Add a game** | One new file, one line in a list. [Step-by-step guide with working code](docs/how-to-add-a-game.md) |
| 🐛 **Fix a bug** | There are real bugs in here on purpose. Each issue names the exact file and function |
| ✨ **Improve a game** | Difficulty levels, better ASCII art, an opponent that actually tries to win |

Every issue tells you the file to open, what "done" looks like, and how to
check your work. If an issue does not do that, it is our mistake — say so and
we will fix it.

---

## Project layout

```
terminal-arcade/
├── arcade/
│   ├── __main__.py      # python -m arcade starts here
│   ├── main.py          # the menu and the list of games
│   ├── art.py           # ASCII banners and colours
│   ├── input_utils.py   # asking the player questions
│   ├── scoreboard.py    # high scores
│   └── games/           # one file per game — add yours here
├── tests/               # pytest
└── docs/
    ├── how-to-add-a-game.md   # start here
    └── architecture.md
```

## Running the tests

Tests need `pytest`, which is the only thing in this project that does:

```bash
python3 -m pip install pytest
python3 -m pytest
```

## Design rules

- **Standard library only.** Ever. This gets used at events on campus Wi-Fi,
  and `pip install` failing must never be why someone cannot take part
- **One file per game.** So contributors never collide with each other
- **Every game returns a score** from `play()`, and `main.py` decides what to
  do with it
- **Only `input_utils` calls `input()`**, so "that is not a number" behaves the
  same everywhere

More detail in [docs/architecture.md](docs/architecture.md).

## Events

Maintained by **OS & DevX**, GITHUB Community GITAM.

| Date | Event |
|---|---|
| Mon, Oct 5 | Hacktoberfest Kickoff & Live PR Lab |
| Mon, Oct 12 | PR Debug Clinic #1 — bring a broken branch |
| Wed, Oct 21 | PR Debug Clinic #2 |

## License

[MIT](LICENSE)
