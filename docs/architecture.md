# How this project is put together

Short version: a menu, some games, and two helper modules. Nothing clever.

```
arcade/
├── __main__.py      python -m arcade starts here
├── main.py          the menu, and the list of games
├── art.py           ASCII banners and terminal colours
├── input_utils.py   asking the player questions safely
├── scoreboard.py    saving and ranking high scores
└── games/
    ├── guess.py
    ├── hangman.py
    ├── rps.py
    └── tictactoe.py
```

## How a game gets played

```
you type `python3 -m arcade`
        │
        ▼
  main.main()  ───── loops forever ─────┐
        │                               │
        ▼                               │
  show_menu()  prints GAMES             │
        │                               │
        ▼                               │
  ask_int()    reads your choice        │
        │                               │
        ▼                               │
  run_game(game)                        │
        │                               │
        ├──▶ game.play()  returns a score
        │                               │
        └──▶ scoreboard.save_score()    │
                                        │
        back to the menu ───────────────┘
```

## The rules that hold it together

**Games do not know about each other.** A game imports `art` and
`input_utils`, and nothing else from the project. This is why two people can
add two games in the same week without ever touching the same lines.

**Games do not save their own scores.** `play()` returns a number; `main.py`
decides what to do with it. That keeps the save-or-not question in one place.

**Nothing outside `input_utils` calls `input()`.** All the "that is not a
number, try again" handling lives in one file, so every game behaves the same.

**Nothing outside `art` writes escape codes.** `art` also decides when to turn
colour off — piped output, or `NO_COLOR` set.

**No third-party dependencies, ever.** This project gets used at events on
campus Wi-Fi. `pip install` failing must never be the reason someone cannot
take part.

## Module reference

### `main.py`

Holds `GAMES`, the list of game modules. Adding a game means adding a line
here. `run_game()` calls `play()` and offers to save the score.

### `art.py`

Colour helpers (`red()`, `green()`, `bold()`, …) and the ASCII banners.
`colours_supported()` returns False when output is not a terminal or
`NO_COLOR` is set, and every helper checks it.

### `input_utils.py`

- `ask(prompt)` — raw text
- `ask_int(prompt, minimum, maximum)` — a whole number, re-asks until valid
- `ask_choice(prompt, choices)` — one of a list, case-insensitive
- `ask_letter(prompt)` — a single letter, lowercased
- `confirm(prompt)` — yes/no
- `pause()` — wait for Enter

### `scoreboard.py`

Scores live in `~/.terminal-arcade/scores.json` as a list of
`{game, player, score, date}`. `load_scores()` returns an empty list rather
than raising if the file is missing or corrupt — losing a scoreboard is
annoying, crashing the arcade is worse.

Every function takes an optional `path` so tests can use a temp file.

### `games/*.py`

One file per game. Each provides `NAME`, `DESCRIPTION`, and `play() -> int`.
See [how-to-add-a-game.md](how-to-add-a-game.md).

## Testing

`pytest` runs everything in `tests/`. The `fake_input` fixture in
`conftest.py` lets a test pretend the player typed a list of answers:

```python
def test_ask_int_accepts_a_number(fake_input):
    fake_input(["7"])
    assert input_utils.ask_int("Pick:") == 7
```

Test the logic, not the printing. `evaluate()`, `winner()`, `decide()` and
`mask_word()` are all pure functions, which is deliberate — it makes them easy
to test and easy to reason about.

## Known rough edges

There are real bugs in here. They are written up as issues with the file and
function named, because fixing a genuine bug in code you did not write is a
much better first contribution than adding a comment.

If you find one that is not already an issue, **open one**. That is a
contribution too.
