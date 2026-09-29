# Contributing to Terminal Arcade

Thanks for being here. This repository is part of **GITHUB Community GITAM** and
is participating in **Hacktoberfest 2026**. Whether this is your first pull
request ever or your hundredth, the guide below is everything you need.

**If this is your first time:** the single best place to start is
[docs/how-to-add-a-game.md](docs/how-to-add-a-game.md). It has a complete,
working game you can copy and turn into your own.

---

## What this project is

A collection of small games you play in your terminal — Hangman, Tic Tac Toe,
Guess the Number, Rock Paper Scissors — behind one menu. It exists to be a
gentle, genuinely fun first open source project.

**Tech stack:** Python 3.10+. Nothing else. No dependencies, by design.

---

## Setting up locally

**You will need:** Python 3.10 or newer, and Git. That is the whole list.

```bash
# 1. Fork this repo on GitHub (button at the top right), then:
git clone https://github.com/YOUR-USERNAME/terminal-arcade.git
cd terminal-arcade

# 2. Point at the original repo so you can stay up to date
git remote add upstream https://github.com/github-community-gitam/terminal-arcade.git

# 3. There is no step 3. There is nothing to install.

# 4. Check it works
python3 -m arcade
```

The menu should appear. If it does not, that is a bug in *our* instructions,
not a mistake on your part — open an issue and tell us where it broke.

To run the tests you need pytest, the only package this project ever asks for:

```bash
python3 -m pip install pytest
python3 -m pytest
```

> **Windows:** if `python3` is not found, try `python` or `py`.

---

## The contribution flow

### 1. Find an issue

Browse the [open issues](../../issues):

| Label | Means |
|---|---|
| `good first issue` | No knowledge of the codebase needed |
| `difficulty: beginner` | Small and self-contained |
| `difficulty: intermediate` | You will need to read some existing code |
| `difficulty: advanced` | Involves a design decision |

**Adding a new game** is the easiest starting point, because you are writing a
new file rather than working out how someone else's code fits together.

### 2. Claim it — this step is not optional

Comment `/claim` on the issue. A bot assigns it to you within seconds.

> **PRs on unclaimed issues are closed.** This is not us being strict for the
> sake of it. Without it, six people do the same task and five of them waste
> an evening.

You may hold **2 issues at a time**. Changed your mind? Comment `/unclaim` —
that is completely fine and nobody thinks less of you. Claims go stale after 5
days of no activity and the issue reopens for others.

### 3. Branch

```bash
git checkout main
git pull upstream main
git checkout -b feat/short-description
```

| Prefix | For | Example |
|---|---|---|
| `feat/` | Something new | `feat/coin-flip-game` |
| `fix/` | Something broken | `fix/hangman-repeated-letter` |
| `docs/` | Documentation | `docs/setup-instructions` |
| `test/` | Tests only | `test/scoreboard-sorting` |
| `ci/` | Workflows, linting | `ci/add-python-matrix` |

### 4. Make the change

- Change **only** what the issue asks for
- Match the style of the code around you — look at `arcade/games/guess.py`
- Add a test if you added or fixed logic
- Write docstrings on new functions

**Commit messages:**

```
fix: hangman no longer charges a life for a repeated letter

Closes #23
```

Format: `<type>: <what changed, lowercase, present tense>`, where type is
`feat`, `fix`, `docs`, `test`, `ci`, `refactor`, or `chore`.

### 5. Test before you push

```bash
python3 -m pytest        # all tests must pass
python3 -m arcade        # and play your change, actually play it
```

If you have ruff installed (optional):

```bash
python3 -m pip install ruff
ruff format .
ruff check .
```

CI runs exactly these. Running them locally takes 10 seconds and saves a round
trip.

### 6. Open the pull request

```bash
git push origin feat/short-description
```

GitHub shows a "Compare & pull request" button. Fill in the template.

**Your description must contain `Closes #<issue-number>`.**

**Paste your terminal output.** A few lines showing your game being played, or
the bug no longer happening, makes a reviewer's job trivial and gets you merged
faster than anything else you can do.

### 7. Review

A maintainer responds within **48 hours**:

- **Approved and merged** — we add `hacktoberfest-accepted`. Done
- **Changes requested** — we leave comments pointing at exact lines. Push more
  commits to the same branch; the PR updates itself. This is normal and happens
  to experienced developers constantly. It is not criticism
- **Closed** — only if the PR breaks a rule below, and we will always say which

---

## Quality standards

We would rather merge 40 real contributions than 400 fake ones. These rules
apply to everyone equally.

### Automatically rejected

Marked `invalid` / `spam` and excluded from Hacktoberfest:

- Whitespace, comma, or formatting-only changes to Markdown files
- Adding your name or a link to the README without being asked to
- AI-generated code pasted in without being read, that fails the linter or
  ships without tests
- PRs that duplicate an already-open PR
- Renaming variables or "improving" code nobody asked to change
- A PR with no linked issue

### Always welcome

- Fixing a genuine bug, however small
- Adding a missing test
- Rewriting confusing documentation so it is actually clear
- Improving an error message
- Telling us our setup instructions are wrong

### The 48-hour maintainer commitment

We commit to acknowledging every PR within 48 hours. If yours has been sitting
longer, ping us in Discord — you are not being annoying, we dropped the ball.

---

## Rules specific to this project

- **Standard library only.** No new dependencies, not even small ones
- **One file per game** in `arcade/games/`
- **Use `input_utils`**, never bare `input()`
- **Use `art` for colour**, never raw escape codes
- **`play()` returns a number** and must always terminate

---

## Getting unstuck

**Everyone gets stuck. It is not a sign that you do not belong here.**

1. Re-read the issue — the answer is often in "How to verify locally"
2. Read `arcade/games/guess.py`, the simplest game in the project
3. Comment on the issue and tag the mentor listed on it
4. Ask in Discord
5. Come to a **PR Debug Clinic** (Oct 12, Oct 21) and we will sit with you

Useful when Git misbehaves:

```bash
git status                       # what state am I in?
git log --oneline -5             # what did I commit?
git pull upstream main           # get the latest changes
git diff                         # what have I changed but not committed?
git restore <file>               # undo uncommitted changes to a file
```

---

## Code of conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
In short: be kind, assume good faith, and remember that the person asking a
"basic" question is exactly who this project is for.

---

## Maintainers

| Name | GitHub | Looks after |
|---|---|---|
| <!-- FILL: your name --> | <!-- FILL: @your-handle --> | Everything |

**Domain:** OS & DevX
