import random
import streamlit as st

def get_range_for_difficulty(difficulty: str):
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100
    return 1, 100


def parse_guess(raw: str):
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
    if guess == secret:
        return "Win", "🎉 Correct!"

    try:
        if guess > secret:
            return "Too High", "📉 Go LOWER!"
        else:
            return "Too Low", "📈 Go HIGHER!"
    except TypeError:
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g > secret:
            return "Too High", "📉 Go LOWER!"
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    if outcome == "Win":
        bonus = 100 - 10 * attempt_number
        if bonus < 10:
            bonus = 10
        # The win score is the bonus itself (100 minus 10 per attempt, floored
        # at 10) — not added to the running total, which would blow past 100.
        return bonus

    # Wrong guess: lose 5 points, but never drop below 0.
    return max(0, current_score - 5)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 8,
    "Normal": 7,
    "Hard": 6,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 100

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# Result message to show after a rerun (so the input can be cleared without
# losing the hint/error/win message).
if "feedback" not in st.session_state:
    st.session_state.feedback = None

# Rotating key for the guess input — bumping it gives a fresh, empty text box.
if "input_nonce" not in st.session_state:
    st.session_state.input_nonce = 0

# Regenerate the secret whenever the difficulty changes (or on first load),
# so the secret always falls inside the current range.
if st.session_state.get("difficulty") != difficulty:
    st.session_state.difficulty = difficulty
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 100
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.feedback = None
    st.session_state.input_nonce += 1

st.subheader("Make a guess")

attempts_left = max(0, attempt_limit - st.session_state.attempts)
st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempts_left}"
)

# Show the result of the previous guess (set before the rerun).
if st.session_state.feedback:
    kind, text = st.session_state.feedback
    getattr(st, kind)(text)
    if st.session_state.pop("celebrate", False):
        st.balloons()
    st.session_state.feedback = None

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{st.session_state.input_nonce}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.score = 100
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.feedback = ("success", "New game started.")
    st.session_state.input_nonce += 1
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(f"{raw_guess} (invalid — not counted)")
        st.session_state.feedback = ("error", err)
    elif guess_int < low or guess_int > high:
        st.session_state.history.append(f"{guess_int} (out of range — not counted)")
        st.session_state.feedback = (
            "error", f"Out of range! Pick a number between {low} and {high}."
        )
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        secret = st.session_state.secret

        outcome, message = check_guess(guess_int, secret)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.session_state.status = "won"
            st.session_state.celebrate = True
            st.session_state.feedback = (
                "success",
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}",
            )
        elif st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"
            st.session_state.feedback = (
                "error",
                f"Out of attempts! The secret was {st.session_state.secret}. "
                f"Score: {st.session_state.score}",
            )
        elif show_hint:
            st.session_state.feedback = ("warning", message)

    st.session_state.input_nonce += 1
    st.rerun()

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
