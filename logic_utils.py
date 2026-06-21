"""Core game logic and persistence helpers for the guessing game.

This module holds the pure, UI-agnostic logic for the "Game Glitch
Investigator" guessing game: difficulty ranges, guess parsing, guess
checking, and scoring, plus small JSON-backed helpers for tracking the
best score and fewest winning guesses per difficulty.

Keeping this logic separate from ``app.py`` (the Streamlit UI) makes it
straightforward to unit test without spinning up the web app.
"""

import json
import os

DEFAULT_HIGH_SCORE_FILE = "high_scores.json"
DEFAULT_BEST_ATTEMPTS_FILE = "best_attempts.json"


def get_range_for_difficulty(difficulty: str):
    """Return the inclusive guessing range for a difficulty level.

    Args:
        difficulty: One of ``"Easy"``, ``"Normal"``, or ``"Hard"``.

    Returns:
        A ``(low, high)`` tuple of ints describing the inclusive range.
        Unknown difficulties fall back to the hardest range, ``(1, 100)``.
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100
    return 1, 100


def parse_guess(raw: str):
    """Parse raw user input into an integer guess.

    Args:
        raw: The raw text entered by the player. May be ``None`` or empty.

    Returns:
        A ``(ok, guess_int, error_message)`` tuple where:

        * ``ok`` (bool) is ``True`` only when parsing succeeded.
        * ``guess_int`` (int | None) is the parsed value, or ``None`` on
          failure.
        * ``error_message`` (str | None) explains the failure, or is
          ``None`` on success.
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        value = int(raw)
    except Exception:
        return False, None, "Enter a whole number."

    return True, value, None


def check_guess(guess, secret):
    """Compare a guess against the secret number.

    Args:
        guess: The player's parsed integer guess.
        secret: The secret integer the player is trying to find.

    Returns:
        An ``(outcome, message)`` tuple. ``outcome`` is one of
        ``"Win"``, ``"Too High"``, or ``"Too Low"``; ``message`` is a
        short, player-facing hint suitable for display.
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Compute the player's score after a guess.

    On a win the score is the attempt bonus itself (100 minus 10 points
    per attempt, floored at 10) rather than an addition to the running
    total, so the final score can never exceed 100. On a wrong guess the
    player loses 5 points but never drops below 0.

    Args:
        current_score: The player's score before this guess.
        outcome: The outcome from :func:`check_guess` (e.g. ``"Win"``).
        attempt_number: The 1-based number of the current attempt.

    Returns:
        The updated score as an int.
    """
    if outcome == "Win":
        bonus = 100 - 10 * attempt_number
        if bonus < 10:
            bonus = 10
        # The win score is the bonus itself (100 minus 10 per attempt, floored
        # at 10) — not added to the running total, which would blow past 100.
        return bonus

    # Wrong guess: lose 5 points, but never drop below 0.
    return max(0, current_score - 5)


def proximity_hint(guess, secret, low, high):
    """Describe how close a guess is to the secret as a Hot/Cold label.

    The distance between ``guess`` and ``secret`` is measured relative to
    the size of the playing range, so "Hot" means the same thing whether
    the range is 1–20 or 1–100. This is a presentation-only helper: it
    never affects scoring or win/lose logic.

    Args:
        guess: The player's parsed integer guess.
        secret: The secret integer.
        low: The inclusive lower bound of the current range.
        high: The inclusive upper bound of the current range.

    Returns:
        An ``(emoji, label, color)`` tuple, e.g. ``("🔥", "Hot", "red")``.
        ``color`` is one of Streamlit's named badge colors and is handy
        for color-coding the hint. A correct guess returns the "Got it"
        bullseye.
    """
    distance = abs(guess - secret)
    if distance == 0:
        return "🎯", "Got it!", "green"

    span = max(1, high - low)
    closeness = distance / span

    if closeness <= 0.05:
        return "🔥", "Blazing hot", "red"
    if closeness <= 0.15:
        return "♨️", "Hot", "orange"
    if closeness <= 0.30:
        return "🌤️", "Warm", "orange"
    if closeness <= 0.50:
        return "❄️", "Cold", "blue"
    return "🥶", "Freezing", "blue"


# --- High score tracking -----------------------------------------------------


def load_high_scores(path: str = DEFAULT_HIGH_SCORE_FILE):
    """Load the best score per difficulty from a JSON file.

    Missing or corrupt files are treated as "no scores yet", so a fresh
    checkout (or a hand-edited file) never crashes the game.

    Args:
        path: Path to the high-score JSON file.

    Returns:
        A ``{difficulty: best_score}`` dict (e.g. ``{"Easy": 90}``)
        containing only well-formed integer scores. Returns an empty
        dict when the file is missing, unreadable, or malformed.
    """
    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

    if not isinstance(data, dict):
        return {}

    # Keep only well-formed integer scores.
    return {k: v for k, v in data.items() if isinstance(v, int)}


def save_high_scores(scores: dict, path: str = DEFAULT_HIGH_SCORE_FILE):
    """Persist the high-score dict to a JSON file.

    Args:
        scores: A ``{difficulty: best_score}`` mapping to save.
        path: Path to the high-score JSON file to write.

    Returns:
        None.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2, sort_keys=True)


def update_high_score(
    difficulty: str,
    score: int,
    path: str = DEFAULT_HIGH_SCORE_FILE,
):
    """Record a score as the new best for its difficulty if it wins.

    The stored score is only replaced when ``score`` beats the existing
    record (higher is better).

    Args:
        difficulty: The difficulty level the score was earned on.
        score: The finished game's score.
        path: Path to the high-score JSON file.

    Returns:
        An ``(is_new_record, best_score)`` tuple so the UI can celebrate
        a new record and always display the current best.
    """
    scores = load_high_scores(path)
    previous = scores.get(difficulty)

    if previous is None or score > previous:
        scores[difficulty] = score
        save_high_scores(scores, path)
        return True, score

    return False, previous


# --- Best attempt tracking ---------------------------------------------------


def load_best_attempts(path: str = DEFAULT_BEST_ATTEMPTS_FILE):
    """Load the fewest guesses needed to win, per difficulty.

    Missing or corrupt files are treated as "no records yet". Only
    positive integer counts are kept (a win always uses at least one
    guess), so a hand-edited or garbage file never crashes the game.

    Args:
        path: Path to the best-attempts JSON file.

    Returns:
        A ``{difficulty: attempts}`` dict (e.g. ``{"Easy": 2}``)
        containing only positive integer counts. Returns an empty dict
        when the file is missing, unreadable, or malformed.
    """
    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

    if not isinstance(data, dict):
        return {}

    return {k: v for k, v in data.items() if isinstance(v, int) and v > 0}


def save_best_attempts(attempts: dict, path: str = DEFAULT_BEST_ATTEMPTS_FILE):
    """Persist the best-attempts dict to a JSON file.

    Args:
        attempts: A ``{difficulty: attempts}`` mapping to save.
        path: Path to the best-attempts JSON file to write.

    Returns:
        None.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(attempts, f, indent=2, sort_keys=True)


def update_best_attempts(
    difficulty: str,
    attempts: int,
    path: str = DEFAULT_BEST_ATTEMPTS_FILE,
):
    """Record a win's guess count as the new best if it's fewer.

    The stored count is only replaced when ``attempts`` is fewer than the
    existing record (lower is better).

    Args:
        difficulty: The difficulty level the win was earned on.
        attempts: The number of guesses used to win.
        path: Path to the best-attempts JSON file.

    Returns:
        An ``(is_new_record, best_attempts)`` tuple so the UI can
        celebrate a new record and always display the current best.
    """
    records = load_best_attempts(path)
    previous = records.get(difficulty)

    if previous is None or attempts < previous:
        records[difficulty] = attempts
        save_best_attempts(records, path)
        return True, attempts

    return False, previous
