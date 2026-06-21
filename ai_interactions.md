# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

### Entry 1 — High Score tracker

**What task did you give the agent?**

I asked the agent to implement a meaningful new feature — a **High Score tracker**
that saves the best score to a file and shows it in the app — and to do it end to
end: add the logic, wire it into the UI, and cover it with tests.

**Files modified**

- `logic_utils.py` — added `load_high_scores`, `save_high_scores`, and
  `update_high_score` (plus a `DEFAULT_HIGH_SCORE_FILE` constant), which persist
  the best score *per difficulty* to a JSON file (`high_scores.json`).
- `app.py` — imported the new helpers, added a "🏆 High Scores" section to the
  sidebar showing the best Easy/Normal/Hard scores, and called
  `update_high_score(...)` on a win so a new record is saved and celebrated in the
  result message.
- `tests/test_high_scores.py` — new test file (8 cases).
- `.gitignore` — added `high_scores.json` so the per-machine save file isn't
  committed.

**What did the agent do?**

1. Designed the high score as a `{difficulty: best_score}` JSON map rather than a
   single number, so each difficulty keeps its own record.
2. Implemented the three logic functions in `logic_utils.py`, making `load`
   tolerate a missing/corrupt file (returns `{}`) and ignore non-integer values.
3. Updated `app.py`: sidebar display + recording the score on a win, with a
   "New high score!" vs "Best: N" message.
4. Wrote `tests/test_high_scores.py` using pytest's `tmp_path` fixture so tests
   write to a throwaway file instead of the real `high_scores.json`.
5. Ran `python -m pytest -q` → **36 passed**, and syntax-checked `app.py`.

**What did you have to verify or fix manually?**

- Confirmed the save file is per-machine state, so I had the agent add it to
  `.gitignore` rather than commit a generated file.
- Made sure the high-score tests use `tmp_path` and never touch the real save
  file — otherwise running the suite could overwrite a real high score.
- Verified `load_high_scores` fails gracefully on a corrupt/hand-edited file
  instead of crashing the Streamlit app on startup.

### Entry 2 — Best Attempt tracker

**What task did you give the agent?**

I asked the agent to implement a complementary feature — a **Best Attempt tracker**
that saves your *fewest guesses to win* (lower is better) to a file, per
difficulty, and shows it in the app. Same end-to-end scope: logic, UI, and tests.

**Files modified**

- `logic_utils.py` — added `load_best_attempts`, `save_best_attempts`, and
  `update_best_attempts` (plus a `DEFAULT_BEST_ATTEMPTS_FILE` constant), persisting
  the fewest winning guesses *per difficulty* to `best_attempts.json`.
- `app.py` — imported the new helpers, added a "🎯 Best Attempts" sidebar section
  beside the existing high-score block, and called `update_best_attempts(...)` on a
  win so the win message reports "Fewest guesses yet!" or the current best.
- `tests/test_best_attempts.py` — new test file (8 cases).
- `.gitignore` — added `best_attempts.json` (per-machine save file).

**What did the agent do?**

1. Mirrored the high-score design as a `{difficulty: attempts}` JSON map, but with
   **lower-is-better** comparison (a record is set when the new count is *fewer*).
2. Implemented the three logic functions, making `load` tolerate a
   missing/corrupt file and keep only **positive** integers (a win always uses ≥1
   guess), so a zero/negative/garbage value is ignored.
3. Wired the sidebar display and the win-time recording into `app.py`.
4. Wrote `tests/test_best_attempts.py` with the `tmp_path` fixture, including a
   case proving a *higher* attempt count does NOT overwrite the record.
5. Ran `python -m pytest -q` → **44 passed**, and syntax-checked `app.py`.

**What did you have to verify or fix manually?**

- Confirmed the intended metric with the user up front: "best attempt" means
  **fewest guesses to win** (lower is better), not most points.
- Made sure the comparison direction was inverted versus the high-score helper
  (`attempts < previous`, not `>`) — easy to copy-paste wrong from the high-score
  code.
- Verified the loader rejects non-positive counts so a bad save file can't show a
  nonsensical "0 guesses" best.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

**Main prompt used to generate the suite:**

```
For this challenge, identify three potential "edge case" inputs (e.g., negative
numbers, decimals, or extremely large values) that might still break my guessing
game, and generate a suite of pytest cases that verify the game handles these
inputs gracefully. Test against parse_guess and check_guess in logic_utils.py.
```

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Why this edge case was chosen |
|-----------|-------------|-------------------|--------------|----------------|
| Negative numbers (`-5`, `-1`, `-100`) | "generate pytest cases for negative number inputs" | `test_parse_accepts_negative_whole_numbers`, `test_check_guess_handles_negative_guess` |  Yes | A minus sign is a valid whole number, so the parser must accept it without crashing — the range check is what rejects it later. |
| Decimals (`42.5`, `42.0`, `0.1`, `-3.7`, `1e3`) | "generate pytest cases that reject decimal inputs" | `test_parse_rejects_decimals` |  Yes | Decimals must be rejected cleanly so `42.5` can't be rounded down into a sneaky win. |
| Extremely large values (`99999999999999999999`) | "generate pytest cases for extremely large numeric inputs" | `test_parse_accepts_extremely_large_values`, `test_check_guess_handles_extremely_large_guess` | Yes | Huge inputs must parse and compare without overflow — Python ints are unbounded, so the math should never break. |

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompts used:**

```
Add professional-grade docstrings to every function in logic_utils.py.
```

```
Review my code for PEP 8 style compliance and apply its suggestions to
resolve any formatting or naming issues it identifies. (app.py + logic_utils.py)
```

**Linter:** `flake8` 6.0.0 (pycodestyle 2.10.0, pyflakes 3.0.1) on CPython 3.10.15.
Full before/after capture is committed in [lint_output.txt](lint_output.txt).

**Linting output before:**

```
$ flake8 logic_utils.py
logic_utils.py:62:1: E402 module level import not at top of file
logic_utils.py:63:1: E402 module level import not at top of file
logic_utils.py:98:80: E501 line too long (88 > 79 characters)
logic_utils.py:152:80: E501 line too long (97 > 79 characters)

$ flake8 app.py
app.py:11:1: E302 expected 2 blank lines, found 1
app.py:66:1: E305 expected 2 blank lines after class or function definition, found 1
app.py:198:80: E501 line too long (84 > 79 characters)
app.py:220:80: E501 line too long (83 > 79 characters)
app.py:240:80: E501 line too long (85 > 79 characters)
```

**Linting output after:**

```
$ flake8 logic_utils.py app.py
(no output — 0 issues)
```

**What the AI suggested and what I applied:**

The AI flagged five distinct issue types. I applied **all** of them, since each
is a low-risk, mechanical fix that doesn't change behavior:

- **E402 (imports not at top)** — `import json` / `import os` lived halfway down
  `logic_utils.py`. Moved both to the top of the module, and consolidated the
  two file-path constants (`DEFAULT_HIGH_SCORE_FILE`,
  `DEFAULT_BEST_ATTEMPTS_FILE`) up near them.
- **E501 (line too long)** — wrapped the over-length lines: the
  `update_high_score` / `update_best_attempts` signatures now use one argument
  per line, and the long `app.py` history-append, `update_high_score` call, and
  win-message f-string were split across multiple lines.
- **E302 (2 blank lines before a top-level def)** — added the missing blank line
  before `get_range_for_difficulty` in `app.py`.
- **E305 (2 blank lines after a function)** — added the missing blank line after
  `update_score` before the top-level Streamlit setup code in `app.py`.
- **Naming** — flake8 found **no** naming issues (no N-codes); the existing
  `snake_case` functions and `UPPER_CASE` constants already follow PEP 8, so no
  renames were needed.

After applying the fixes, `flake8 logic_utils.py app.py` reports **0 issues** and
the full pytest suite still passes (**44 passed**), confirming the style cleanup
was behavior-preserving. I also added professional-grade docstrings (module-level
summary plus Args/Returns sections) to every function in `logic_utils.py`.

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

<!-- Describe what you asked each model to do -->

| | Model A | Model B |
|-|---------|---------|
| **Model name** | | |
| **Response summary** | | |
| **More Pythonic?** | | |
| **Clearer explanation?** | | |

**Which did you prefer and why?**

<!-- Your conclusion -->
