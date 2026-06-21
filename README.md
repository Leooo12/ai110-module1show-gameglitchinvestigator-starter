# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

### The game's purpose

It's a number guessing game built with Streamlit. The app picks a secret number
inside a range that depends on the difficulty, and you try to guess it before you
run out of attempts. After each guess it tells you if you're too high or too low,
keeps a score, and shows a "Developer Debug Info" panel (secret, attempts, score,
history) to help with testing.

- **Easy** – range 1–20, 8 attempts
- **Normal** – range 1–50, 7 attempts
- **Hard** – range 1–100, 6 attempts

### Bugs I found

| # | Bug | What happened |
|---|-----|---------------|
| 1 | No range check | Out-of-range guesses like `100000`, `0`, or `-1` were accepted and just got a "Too Low/High" hint instead of being rejected. |
| 2 | Hints were backwards | Guessing low said "Go LOWER" and guessing high said "Go HIGHER" — the directions were swapped. |
| 3 | New Game didn't reset | Clicking New Game only reset the secret and attempts; the old score, history, and status stayed, so the page got stuck on "Game over." |
| 4 | Hints were inconsistent | On every other guess the secret was turned into a string, so the comparison was done as text instead of numbers and the hint flipped randomly. |
| 5 | "Attempts left" was wrong | The top banner and the bottom message disagreed (off-by-one), and the banner always said "between 1 and 100" no matter the difficulty. |
| 6 | Secret out of range | The secret only generated once, so switching difficulty left an old secret (e.g. 76) outside the new range. |
| 7 | Decimals could win | `42.2` was rounded down to `42`, so you could win with a decimal. |
| 8 | Bad guesses cost an attempt | Out-of-range / invalid guesses still used up an attempt. |
| 9 | Score went negative / over 100 | Wrong guesses pushed the score below 0, and a fast win added the bonus on top of 100 (e.g. 190). |
| 10 | Input box never cleared | After submitting, the old guess stayed in the box and new guesses didn't show up in history right away. |

### Fixes I applied

- **Difficulty ranges & attempts:** Easy 1–20 / 8, Normal 1–50 / 7, Hard 1–100 / 6.
- **Range check:** out-of-range and non-whole-number guesses are now rejected with a clear message and don't count as an attempt (they're labeled in the history).
- **Hints:** flipped the messages so "Too Low" → Go HIGHER and "Too High" → Go LOWER, and always compare the guess to the integer secret (removed the string conversion).
- **Secret:** regenerated whenever the difficulty changes, so it always stays inside the current range.
- **New Game / difficulty switch:** now fully reset secret, attempts, score, history, and status — no more "Game over" lockout.
- **Banner:** shows the real range and a correct (non-negative) "attempts left" count.
- **Scoring:** starts at 100, loses 5 per wrong guess but never goes below 0, and the win score is the speed bonus itself (capped at 100, floored at 10) instead of being added on top.
- **Input box:** clears after each submit and history updates immediately, by re-running the app and rotating the input's key.
- **Refactor & tests:** moved the core logic into `logic_utils.py`, fixed the starter tests (which compared a `(outcome, message)` tuple to a plain string), and added scoring tests — all 8 pass.

## 📸 Demo Walkthrough

Difficulty sets the number range and how many attempts you get:

- Easy: range 1–20, 8 attempts
- Normal: range 1–50, 7 attempts
- Hard: range 1–100, 6 attempts

A sample game on Normal difficulty (range 1–50, 7 attempts, secret is 37). Score starts at 100.

1. User enters a guess of 25 → "Too Low" (Go HIGHER), score drops to 95.
2. User enters a guess of 40 → "Too High" (Go LOWER), score drops to 90.
3. The secret stays at 37 the whole game — it no longer resets on each guess.
4. User enters a guess of 37 → "Correct!", final score is 70.
5. The game ends; clicking Reset starts a new round with score back to 100.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

### Edge cases tested

To make sure the game handles unusual inputs gracefully, I added
`tests/test_edge_cases.py` covering three categories of edge-case input:

1. **Negative numbers** (e.g. `-5`) — accepted as valid whole numbers by the
   parser (the range check rejects them later) without crashing.
2. **Decimals** (e.g. `42.5`) — rejected cleanly with "Enter a whole number."
   so a decimal can't be rounded down into a win.
3. **Extremely large values** (e.g. `99999999999999999999`) — parsed without
   overflow and compared correctly, since Python ints are unbounded.

Plus bonus checks for non-numeric text (`abc`, `12abc`) and missing input
(`None`, `""`), which all fail gracefully with a clear message.

### Terminal output

```
$ python -m pytest -v
============================= test session starts ==============================
platform darwin -- Python 3.10.15, pytest-7.1.2, pluggy-1.0.0
cachedir: .pytest_cache
rootdir: /Users/leo/ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.13.0
collecting ... collected 28 items

tests/test_edge_cases.py::test_parse_accepts_negative_whole_numbers[-5--5] PASSED [  3%]
tests/test_edge_cases.py::test_parse_accepts_negative_whole_numbers[-1--1] PASSED [  7%]
tests/test_edge_cases.py::test_parse_accepts_negative_whole_numbers[-100--100] PASSED [ 10%]
tests/test_edge_cases.py::test_check_guess_handles_negative_guess PASSED [ 14%]
tests/test_edge_cases.py::test_parse_rejects_decimals[42.5] PASSED       [ 17%]
tests/test_edge_cases.py::test_parse_rejects_decimals[42.0] PASSED       [ 21%]
tests/test_edge_cases.py::test_parse_rejects_decimals[0.1] PASSED        [ 25%]
tests/test_edge_cases.py::test_parse_rejects_decimals[-3.7] PASSED       [ 28%]
tests/test_edge_cases.py::test_parse_rejects_decimals[1e3] PASSED        [ 32%]
tests/test_edge_cases.py::test_parse_accepts_extremely_large_values[99999999999999999999] PASSED [ 35%]
tests/test_edge_cases.py::test_parse_accepts_extremely_large_values[10000000000] PASSED [ 39%]
tests/test_edge_cases.py::test_parse_accepts_extremely_large_values[12345678901234567890] PASSED [ 42%]
tests/test_edge_cases.py::test_check_guess_handles_extremely_large_guess PASSED [ 46%]
tests/test_edge_cases.py::test_parse_rejects_non_numeric_text[abc] PASSED [ 50%]
tests/test_edge_cases.py::test_parse_rejects_non_numeric_text[  ] PASSED [ 53%]
tests/test_edge_cases.py::test_parse_rejects_non_numeric_text[12abc] PASSED [ 57%]
tests/test_edge_cases.py::test_parse_rejects_non_numeric_text[++5] PASSED [ 60%]
tests/test_edge_cases.py::test_parse_rejects_non_numeric_text[None] PASSED [ 64%]
tests/test_edge_cases.py::test_parse_handles_missing_input[None] PASSED  [ 67%]
tests/test_edge_cases.py::test_parse_handles_missing_input[] PASSED      [ 71%]
tests/test_game_logic.py::test_winning_guess PASSED                      [ 75%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [ 78%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 82%]
tests/test_game_logic.py::test_win_score_never_exceeds_100 PASSED        [ 85%]
tests/test_game_logic.py::test_win_score_is_floored_at_10 PASSED         [ 89%]
tests/test_game_logic.py::test_win_score_does_not_add_to_running_total PASSED [ 92%]
tests/test_game_logic.py::test_wrong_guess_loses_5_points PASSED         [ 96%]
tests/test_game_logic.py::test_score_never_drops_below_zero PASSED       [100%]

============================== 28 passed in 0.03s ==============================
```

## 🎨 UI Enhancements

I added structured, user-friendly output on top of the fixed game **without
touching the core win/lose, scoring, or range-check logic**. Everything below is
presentation-only:

- **Hot/Cold proximity hints** — a new pure helper,
  `proximity_hint(guess, secret, low, high)` in `logic_utils.py`, measures how
  far a guess is from the secret *relative to the range size* (so "Hot" means the
  same thing on Easy and Hard). It returns an `(emoji, label, color)` tuple:
  🎯 Got it! / 🔥 Blazing hot / ♨️ Hot / 🌤️ Warm / ❄️ Cold / 🥶 Freezing. It
  never affects scoring — it's covered by `tests/test_edge_cases.py`-style logic
  and verified at import.
- **Color-coded hint message** — in `app.py`'s submit handler (the
  `elif show_hint:` branch), the directional hint ("Go HIGHER/LOWER") is now
  rendered as Markdown with a colored Streamlit badge
  (`:{color}-badge[{emoji} {label}]`) whose color reflects proximity — red when
  blazing hot, blue when freezing.
- **At-a-glance scoreboard** — three `st.metric` widgets near the top of `app.py`
  (just below the range banner) show **Score**, **Attempts left**, and
  **Guesses made**, so the player doesn't need the Developer Debug panel to track
  progress.
- **Session summary table** — a new `📋 Session Summary` section at the bottom of
  `app.py` renders `st.session_state.guess_log` via `st.table`. Each counted guess
  is appended in the submit handler as a row with `#`, `Guess`, `Result`,
  `Distance`, and `Proximity` (emoji + label). The log is reset on **New Game**
  and on difficulty changes, alongside the other session state.

## 🚀 Stretch Features

- [x] **High Score tracker** — the best score for each difficulty is saved to a
  JSON file (`high_scores.json`) and shown in a "🏆 High Scores" sidebar section.
  When you win, the game compares your final score to the stored best, saves it if
  it's a new record, and tells you whether you beat your record or what the best
  still is. Logic lives in `logic_utils.py` (`load_high_scores`,
  `save_high_scores`, `update_high_score`) and is covered by
  `tests/test_high_scores.py`.
