import os
import re
import random
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="IG Econ Video Quizzes", layout="wide")

RESULTS_FILE = "results.csv"
ANALYTICS_FILE = "question_analytics.csv"

# Add your teacher/admin email(s) here
ADMIN_EMAILS = {
    "yourname@sisb.ac.th",
}

# -----------------------------
# Save functions
# -----------------------------
def save_result(name, email, quiz_title, score, total):
    percent = round((score / total) * 100, 1) if total > 0 else 0

    row = pd.DataFrame([{
        "Name": name,
        "Email": email,
        "Quiz Title": quiz_title,
        "Score": score,
        "Total": total,
        "Percent": percent,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }])

    if os.path.exists(RESULTS_FILE):
        row.to_csv(RESULTS_FILE, mode="a", header=False, index=False)
    else:
        row.to_csv(RESULTS_FILE, index=False)


def save_question_analytics(quiz_title, email, q_num, question, selected, correct, is_correct):
    row = pd.DataFrame([{
        "Quiz Title": quiz_title,
        "Email": email,
        "Question Number": q_num,
        "Question": question,
        "Selected Answer": selected,
        "Correct Answer": correct,
        "Is Correct": is_correct,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }])

    if os.path.exists(ANALYTICS_FILE):
        row.to_csv(ANALYTICS_FILE, mode="a", header=False, index=False)
    else:
        row.to_csv(ANALYTICS_FILE, index=False)


# -----------------------------
# Quiz helpers
# -----------------------------
def shuffle_question(row, seed):
    rng = random.Random(seed)

    options = {
        "A": str(row["option_a"]).strip(),
        "B": str(row["option_b"]).strip(),
        "C": str(row["option_c"]).strip(),
        "D": str(row["option_d"]).strip(),
    }

    correct_letter = str(row["correct_answer"]).strip().upper()
    correct_text_value = options[correct_letter]

    values = list(options.values())
    rng.shuffle(values)

    shuffled = dict(zip(["A", "B", "C", "D"], values))
    new_correct = next(letter for letter, value in shuffled.items() if value == correct_text_value)

    return shuffled, new_correct


def format_options(options_dict):
    return [f"{letter}. {text}" for letter, text in options_dict.items()]


def make_correct_display(options_dict, correct_letter):
    return f"{correct_letter}. {options_dict[correct_letter]}"


def validate_quiz_df(df):
    required_cols = ["question", "option_a", "option_b", "option_c", "option_d", "correct_answer"]
    return [col for col in required_cols if col not in df.columns]


def convert_sheet_url(url):
    url = url.strip()

    if "export?format=csv" in url:
        return url

    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if not match:
        raise ValueError("Invalid Google Sheets URL")

    sheet_id = match.group(1)
    gid_match = re.search(r"gid=([0-9]+)", url)
    gid = gid_match.group(1) if gid_match else "0"

    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


@st.cache_data(show_spinner=False)
def load_csv_file(uploaded_file):
    return pd.read_csv(uploaded_file)


@st.cache_data(show_spinner=False)
def load_google_sheet(sheet_url):
    csv_url = convert_sheet_url(sheet_url)
    return pd.read_csv(csv_url)


def reset_quiz_state():
    keys_to_remove = [
        "submitted",
        "score",
        "total",
        "quiz_id",
    ]
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]


# -----------------------------
# Login
# -----------------------------
if not st.user.is_logged_in:
    st.title("🎓 IG Econ Video Quizzes")
    st.write("Please log in with Google to continue.")
    if st.button("Login with Google"):
        st.login()
    st.stop()

user = st.user
name = getattr(user, "name", "Student")
email = getattr(user, "email", "")

# -----------------------------
# Header
# -----------------------------
st.title("🎓 IG Econ Video Quizzes")

header_left, header_right = st.columns([5, 1])

with header_left:
    st.caption(f"Logged in as **{name}** ({email})")

with header_right:
    if st.button("Logout"):
        st.logout()

st.divider()

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("Quiz Settings")

    quiz_title = st.text_input("Quiz title", "IG Econ Video Quiz")

    source = st.radio(
        "Quiz source",
        ["Upload CSV", "Google Sheets"],
        index=0
    )

    youtube_url = st.text_input("YouTube link")

    if st.button("Reset current quiz"):
        reset_quiz_state()
        st.rerun()

# -----------------------------
# Load quiz
# -----------------------------
df = None

try:
    if source == "Upload CSV":
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file is not None:
            df = load_csv_file(uploaded_file)

    elif source == "Google Sheets":
        sheet_url = st.text_input("Paste Google Sheets link")
        if sheet_url.strip():
            df = load_google_sheet(sheet_url)

except Exception as e:
    st.error(f"Could not load quiz: {e}")
    st.stop()

if df is None:
    st.info("Upload a CSV or paste a Google Sheets link to begin.")
    st.stop()

missing_cols = validate_quiz_df(df)
if missing_cols:
    st.error(f"Missing required columns: {', '.join(missing_cols)}")
    st.stop()

df = df.fillna("")

quiz_id = f"{quiz_title}|{len(df)}|{df.iloc[0]['question'] if len(df) > 0 else 'empty'}"
if st.session_state.get("quiz_id") != quiz_id:
    reset_quiz_state()
    st.session_state["quiz_id"] = quiz_id

# -----------------------------
# Video section
# -----------------------------
st.subheader("🎬 Video")

if youtube_url.strip():
    st.video(youtube_url)
else:
    st.info("Add a YouTube link if you want students to watch a video before the quiz.")

st.divider()

# -----------------------------
# Quiz section
# -----------------------------
st.subheader("📋 Quiz")

answers = {}
correct_answers = {}
questions = {}

for i, row in df.iterrows():
    shuffled_options, new_correct_letter = shuffle_question(row, seed=i)
    display_options = format_options(shuffled_options)
    correct_display = make_correct_display(shuffled_options, new_correct_letter)

    selected = st.radio(
        f"{i + 1}. {row['question']}",
        display_options,
        key=f"q_{i}"
    )

    answers[i] = selected
    correct_answers[i] = correct_display
    questions[i] = str(row["question"])

submit_clicked = st.button("Submit Quiz", disabled=st.session_state.get("submitted", False))

if submit_clicked:
    score = 0
    total = len(df)

    for i in answers:
        is_correct = answers[i] == correct_answers[i]

        if is_correct:
            score += 1

        save_question_analytics(
            quiz_title=quiz_title,
            email=email,
            q_num=i + 1,
            question=questions[i],
            selected=answers[i],
            correct=correct_answers[i],
            is_correct=is_correct,
        )

    save_result(
        name=name,
        email=email,
        quiz_title=quiz_title,
        score=score,
        total=total,
    )

    st.session_state["submitted"] = True
    st.session_state["score"] = score
    st.session_state["total"] = total

if st.session_state.get("submitted", False):
    score = st.session_state["score"]
    total = st.session_state["total"]
    percent = round((score / total) * 100, 1) if total > 0 else 0

    st.success(f"🎯 Score: {score}/{total} ({percent}%)")
    st.info("Try again to improve your score.")

    with st.expander("Review answers"):
        for i in questions:
            st.write(f"**Q{i + 1}. {questions[i]}**")
            st.write(f"Your answer: {answers[i]}")
            st.write(f"Correct answer: {correct_answers[i]}")
            st.write("---")

# -----------------------------
# Teacher-only leaderboard
# -----------------------------
if email in ADMIN_EMAILS:
    st.divider()
    st.subheader("🏆 Leaderboard")

    if os.path.exists(RESULTS_FILE):
        results_df = pd.read_csv(RESULTS_FILE)
        results_df = results_df[results_df["Quiz Title"] == quiz_title].copy()

        if not results_df.empty:
            leaderboard = (
                results_df
                .sort_values(by=["Percent", "Timestamp"], ascending=[False, True])
                .head(10)
            )
            st.dataframe(leaderboard, use_container_width=True)
        else:
            st.info("No results yet for this quiz.")
    else:
        st.info("No results file yet.")

# -----------------------------
# Teacher dashboard
# -----------------------------
if email in ADMIN_EMAILS:
    st.divider()
    st.subheader("📊 Teacher Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        if os.path.exists(RESULTS_FILE):
            results_df = pd.read_csv(RESULTS_FILE)
            results_df = results_df[results_df["Quiz Title"] == quiz_title].copy()

            st.write("### Results")

            if not results_df.empty:
                st.dataframe(results_df, use_container_width=True)
                st.metric("Average %", round(results_df["Percent"].mean(), 1))

                results_csv = results_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download results CSV",
                    data=results_csv,
                    file_name=f"{quiz_title}_results.csv",
                    mime="text/csv"
                )
            else:
                st.info("No results yet for this quiz.")

    with col2:
        if os.path.exists(ANALYTICS_FILE):
            analytics_df = pd.read_csv(ANALYTICS_FILE)
            analytics_df = analytics_df[analytics_df["Quiz Title"] == quiz_title].copy()

            st.write("### Question Analysis")

            if not analytics_df.empty:
                stats = (
                    analytics_df.groupby(["Question Number", "Question"], as_index=False)
                    .agg(
                        Attempts=("Is Correct", "count"),
                        Correct=("Is Correct", "sum")
                    )
                )

                stats["Correct %"] = (stats["Correct"] / stats["Attempts"] * 100).round(1)
                stats = stats.sort_values("Question Number")

                st.dataframe(stats, use_container_width=True)

                analytics_csv = stats.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download question analysis CSV",
                    data=analytics_csv,
                    file_name=f"{quiz_title}_question_analysis.csv",
                    mime="text/csv"
                )
            else:
                st.info("No analytics yet for this quiz.")
