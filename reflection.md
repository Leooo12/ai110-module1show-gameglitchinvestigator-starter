# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").
When I first ran the AI-generated guessing game it looked playable, but the scoring and a lot of the core logic were "off," which is what the project is named after. The most visible problems were in the gameplay itself: the high/low hint was inverted (guessing a low number like `1` told me to "Go LOWER" instead of "Go HIGHER"), there was no range check so it happily accepted nonsense guesses like `100000`, `-1`, or `0`, and the "New Game" button only reset the secret and attempts while leaving the old score and history in place — and because it never reset the game *status*, the page stayed locked on "Game over. Start a new game to try again," so I couldn't actually submit a guess. The scoring was broken too: it was supposed to be out of 100, but winning quickly could push the final score *above* 100 because the win bonus was added to the running total instead of replacing it. Digging into the code with AI, I also found `check_guess` had a `try/except TypeError` branch that could never actually run and was internally broken (it compared a string to an integer). On top of all that, the starter unit tests were wrong — they compared `check_guess(...)` to a plain string even though the function returns a `(outcome, message)` tuple.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Guess of `1` at Normal difficulty | "Too Low" hint → tells me to **go HIGHER** | "Go LOWER!" shown — higher/lower directions were swapped | None — silently wrong hint |
| Guess of `99` at Normal difficulty | "Too High" hint → tells me to **go LOWER** | "Go HIGHER!" shown — same inverted-direction bug | None — silently wrong hint |
| Click "New Game" | Whole game resets: secret, attempts, score, history, and status | Only the secret and attempts reset; score, history, and status stayed put | None |
| Guess of `-1` at Normal difficulty | Rejected as out of range; only numbers inside 1–50 should count | Accepted as a real guess and given a "Too Low" hint | None — invalid guess counted |
| Score showing `-25` after a few wrong guesses / New Game | Score should never go below 0 and should reset to start on New Game | Score dropped to `-25` (no floor at 0) and didn't reset on New Game | None |
| Guess of `1`, then Submit | Input box clears (empty) for the next guess after submitting | `1` stayed in the box after submitting; the box never reset | None |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
I used Claude Code (in the IDE) to read through `app.py` and `logic_utils.py` and explain the logic in plain language. One **correct** suggestion was tracing the inverted hint: the AI pointed out that `check_guess` returned `"Go LOWER!"` for the "Too Low" case and `"Go HIGHER!"` for "Too High," so the messages were swapped relative to the outcomes — I flipped them and pinned the directions with `test_guess_too_high`/`test_guess_too_low`. It also caught two state bugs I'd missed: the "New Game" button only reset `secret` and `attempts` (leaving `score`, `history`, and `status` stale, which caused the "Game over" lockout), and the wrong-guess path did `current_score - 5` with no floor, so the score went negative. One **incorrect** suggestion came when I asked the AI to make the score update on every guess: it rewrote `update_score` so a win returned `current_score + bonus`. Because the score already started at 100, a first-try win gave `100 + 90 = 190`, blowing past the intended 100 max — so I **rejected** that version. I caught it by reasoning through the numbers (and flagged it with a `FIXME`), then changed the win branch to `return bonus` so the win score *replaces* the total instead of stacking on it, and locked it in with `test_win_score_never_exceeds_100`. The AI had also written the matching test to expect `90` (not `190`), so trusting its code blindly would have shipped a score that breaks the game's own rules.
---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?
I decided a bug was really fixed when I could reproduce it as a failing test first, then watch that same test pass after the change. For the inverted hint I wrote `test_guess_too_high` (`check_guess(60, 50)` → `"Too High"`) and `test_guess_too_low` (`check_guess(40, 50)` → `"Too Low"`), which would have failed on the swapped-message code. For the negative-score bug I wrote `test_score_never_drops_below_zero`, which asserts `update_score(3, "Too Low", 4) == 0` instead of `-2`, and I kept the scoring tests around the win bonus (≤ 100, floored at 10, not added to the running total). The "New Game" and out-of-range bugs were behavior I checked by hand in the running app — I confirmed New Game now clears score/history/status and that out-of-range guesses are rejected before they count. AI helped me design these by suggesting the exact boundary inputs to target (a low guess, a high guess, a low starting score) so the tests pin down the behavior instead of just checking the happy path; running `pytest tests/test_game_logic.py -q` gave me 8 passing tests.
---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
A Streamlit "rerun" means the entire script runs top-to-bottom again every time you interact with a widget (click a button, type in a box), so you can't rely on normal variables to remember anything between clicks. That's why the game keeps values like `secret`, `score`, `attempts`, `status`, and `history` in `st.session_state`, which survives reruns. This is exactly where two of my bugs lived: the "New Game" button only reset `secret` and `attempts`, so the *stale* `score`, `history`, and `status` survived the rerun and the leftover `"lost"` status hit `st.stop()` and locked the page — a real "forgot to clear part of the fridge" bug. The input box that wouldn't clear was the same idea: its widget key was fixed, so the rerun kept showing my old guess; bumping an `input_nonce` in the key forces a fresh, empty box. I'd explain it to a friend as: "the page is a recipe that re-cooks itself from scratch on every click, and `session_state` is the fridge — if you only restock half of it, the game keeps serving yesterday's leftovers."

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
The habit I most want to reuse is **reproduce-the-bug-as-a-test-first**: writing a failing test that captures the bad behavior before fixing it, so I know the fix actually did something — that's how I locked down the inverted hint and the negative score. A prompting strategy that worked was asking the AI to *explain* suspicious logic before changing it, which is how I caught that the `except` branch and the "turn the secret into a string" line were causing the very error they pretended to handle, instead of blindly trusting them. I also learned to actually *play* the app for the bugs a unit test won't catch — the "New Game" lockout and the input box that wouldn't clear only showed up by clicking around, because they were state/UI bugs, not pure-logic ones. Next time I'd be more skeptical of AI-generated code from the start — run the existing tests *first* and click through the real UI — because this project showed me generated code can look polished and "production-ready" while hiding silent logic bugs *and* broken state handling, so my job is to verify it, not just read it and nod.