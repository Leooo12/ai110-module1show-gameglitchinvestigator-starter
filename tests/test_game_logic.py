from logic_utils import check_guess, update_score


# ---------------------------------------------------------------------------
# check_guess
# check_guess returns a (outcome, message) tuple, so we unpack it. The old
# tests compared the whole tuple to a plain string ("Win") and would fail.
# ---------------------------------------------------------------------------

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# ---------------------------------------------------------------------------
# update_score  --  THE BUG WE FIXED
#
# Original bug: a win did `return current_score + bonus`. Starting from 100,
# a fast win pushed the final score ABOVE 100 (win on attempt 1 -> 100 + 90
# = 190). The fix makes the win score BE the bonus, capped at 100.
# ---------------------------------------------------------------------------

def test_win_score_never_exceeds_100():
    # Regression test for the score-inflation bug.
    # Win on the first attempt: bonus = 100 - 10*1 = 90.
    # Buggy code returned 100 + 90 = 190; fixed code returns 90.
    score = update_score(current_score=100, outcome="Win", attempt_number=1)
    assert score == 90
    assert score <= 100


def test_win_score_is_floored_at_10():
    # bonus = 100 - 10*20 = -100, floored to 10.
    score = update_score(current_score=100, outcome="Win", attempt_number=20)
    assert score == 10


def test_win_score_does_not_add_to_running_total():
    # Even with a low running score, a win should not add bonus on top of it.
    # attempt 2 -> bonus = 80, NOT current_score(30) + 80 = 110.
    score = update_score(current_score=30, outcome="Win", attempt_number=2)
    assert score == 80


def test_wrong_guess_loses_5_points():
    assert update_score(current_score=100, outcome="Too High", attempt_number=1) == 95


def test_score_never_drops_below_zero():
    assert update_score(current_score=3, outcome="Too Low", attempt_number=4) == 0
