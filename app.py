import re
import random
from datetime import datetime

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="IG Econ Video Quizzes", layout="wide")

# -----------------------------------
# CONFIG
# -----------------------------------
ADMIN_EMAILS = {
    "james.p@sisbschool.com",
}

QUIZ_CATALOGUE_URL = "https://docs.google.com/spreadsheets/d/1M6QJOgDr5BYtsxpxLA-u1_RYRCugzlINQOUrVsTin-o/edit?usp=sharing"


# -----------------------------------
# GOOGLE SHEETS RESULTS CONNECTION
# -----------------------------------
@st.cache_resource
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes,
    )
    return gspread.authorize(creds)


@st.cache_resource
def get_results_workbooks():
    client = get_gspread_client()
    spreadsheet = client.open_by_url(st.secrets["results_sheet"]["spreadsheet_url"])
    results_ws = spreadsheet.worksheet(st.secrets["results_sheet"]["results_worksheet"])
    analytics_ws = spreadsheet.worksheet(st.secrets["results_sheet"]["analytics_worksheet"])
    return results_ws, analytics_ws


def ensure_sheet_headers():
    results_ws, analytics_ws = get_results_workbooks()

    if not results_ws.get_all_values():
        results_ws.append_row([
            "Name",
            "Email",
            "Role",
            "Quiz Title",
            "Score",
            "Total",
            "Percent",
            "Timestamp",
        ])

    if not analytics_ws.get_all_values():
        analytics_ws.append_row([
            "Quiz Title",
            "Email",
            "Role",
            "Question Number",
            "Question",
            "Selected Answer",
            "Correct Answer",
            "Is Correct",
            "Timestamp",
        ])


def load_results_from_sheets():
    ensure_sheet_headers()
    results_ws, analytics_ws = get_results_workbooks()

    results_records = results_ws.get_all_records()
    analytics_records = analytics_ws.get_all_records()

    results_df = pd.DataFrame(results_records)
    analytics_df = pd.DataFrame(analytics_records)

    return results_df, analytics_df


# -----------------------------------
# SAVE FUNCTIONS
# -----------------------------------
def save_result(name, email, role, quiz_title, score, total):
    percent = round((score / total) * 100, 1) if total > 0 else 0
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ensure_sheet_headers()
    results_ws, _ = get_results_workbooks()

    results_ws.append_row([
        name,
        email,
        role,
        quiz_title,
        score,
        total,
        percent,
        timestamp,
    ])


def save_question_analytics(quiz_title, email, role, q_num, question, selected, correct, is_correct):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ensure_sheet_headers()
    _, analytics_ws = get_results_workbooks()

    analytics_ws.append_row([
        quiz_title,
        email,
        role,
        q_num,
        question,
        selected,
        correct,
        is_correct,
        timestamp,
    ])


# -----------------------------------
# HELPERS
# -----------------------------------
def convert_sheet_url(url):
    url = str(url).strip()

    if "export?format=csv" in url:
        return url

    if "/d/" in url:
        sheet_id = url.split("/d/")[1].split("/")[0]
    else:
        raise ValueError("Invalid Google Sheets URL")

    gid = "0"
    if "gid=" in url:
        gid = url.split("gid=")[1].split("&")[0]

    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


@st.cache_data(show_spinner=False)
def load_google_sheet(sheet_url):
    csv_url = convert_sheet_url(sheet_url)
    return pd.read_csv(csv_url)


def validate_quiz_df(df):
    required_cols = ["question", "option_a", "option_b", "option_c", "option_d", "correct_answer"]
    return [col for col in required_cols if col not in df.columns]


def validate_catalogue_df(df):
    required_cols = ["quiz_id", "quiz_title", "youtube_url", "question_sheet_url", "visible"]
    return [col for col in required_cols if col not in df.columns]


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


def reset_quiz_state():
    keys_to_remove = [
        "submitted",
        "score",
        "total",
        "quiz_id",
        "selected_quiz_id",
    ]
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

    question_keys = [k for k in st.session_state.keys() if k.startswith("q_")]
    for key in question_keys:
        del st.session_state[key]


def clear_question_state_only():
    question_keys = [k for k in st.session_state.keys() if k.startswith("q_")]
    for key in question_keys:
        del st.session_state[key]

    for key in ["submitted", "score", "total", "quiz_id"]:
        if key in st.session_state:
            del st.session_state[key]


def parse_visible(value):
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


# -----------------------------------
# AUTH
# -----------------------------------
user_dict = st.user.to_dict()

if "is_logged_in" not in user_dict:
    st.error("Authentication is not configured correctly yet.")
    st.stop()

if not st.user.is_logged_in:
    st.title("🎓 IG Econ Video Quizzes")
    st.write("Please log in with Google to continue.")
    st.button("Login with Google", on_click=st.login)
    st.stop()

user = st.user
name = getattr(user, "name", "Student")
email = getattr(user, "email", "")

# -----------------------------------
# HEADER
# -----------------------------------
st.title("🎓 IG Econ Video Quizzes")

header_left, header_right = st.columns([5, 1])

with header_left:
    st.caption(f"Logged in as **{name}** ({email})")

with header_right:
    if st.button("Logout"):
        st.logout()

st.divider()

# -----------------------------------
# ROLE SELECTION
# -----------------------------------
st.subheader("Choose your role")

role = st.radio(
    "Select role",
    ["Student", "Teacher"],
    horizontal=True,
    key="role_selector",
)

is_teacher_mode = role == "Teacher"

if is_teacher_mode and email not in ADMIN_EMAILS:
    st.warning("Teacher mode is restricted.")
    st.info("Your account is not listed in ADMIN_EMAILS in the app code.")
    st.stop()

# -----------------------------------
# LOAD QUIZ CATALOGUE
# -----------------------------------
if QUIZ_CATALOGUE_URL == "PASTE_YOUR_QUIZ_CATALOGUE_GOOGLE_SHEET_URL_HERE":
    st.error("Please add your quiz catalogue Google Sheet URL to QUIZ_CATALOGUE_URL in app.py")
    st.stop()

try:
    catalogue_df = load_google_sheet(QUIZ_CATALOGUE_URL)
except Exception as e:
    st.error(f"Could not load quiz catalogue: {e}")
    st.stop()

missing_catalogue_cols = validate_catalogue_df(catalogue_df)
if missing_catalogue_cols:
    st.error(f"Quiz catalogue is missing columns: {', '.join(missing_catalogue_cols)}")
    st.stop()

catalogue_df = catalogue_df.fillna("")
catalogue_df = catalogue_df[catalogue_df["visible"].apply(parse_visible)].copy()

if catalogue_df.empty:
    st.warning("No visible quizzes found in the catalogue.")
    st.stop()

# -----------------------------------
# QUIZ SELECTION
# -----------------------------------
st.subheader("Available quizzes")

quiz_titles = catalogue_df["quiz_title"].tolist()

selected_quiz_title = st.selectbox(
    "Choose a quiz",
    quiz_titles,
    index=None,
    placeholder="Select a quiz"
)

if selected_quiz_title is None:
    st.info("Choose a quiz to begin.")
    st.stop()

selected_quiz_row = catalogue_df[catalogue_df["quiz_title"] == selected_quiz_title].iloc[0]
selected_quiz_id = selected_quiz_row["quiz_id"]
youtube_url = str(selected_quiz_row["youtube_url"]).strip()
question_sheet_url = str(selected_quiz_row["question_sheet_url"]).strip()

if st.session_state.get("selected_quiz_id") != selected_quiz_id:
    clear_question_state_only()
    st.session_state["selected_quiz_id"] = selected_quiz_id

# -----------------------------------
# TEACHER INFO PANEL
# -----------------------------------
if is_teacher_mode:
    with st.sidebar:
        st.header("Teacher View")
        st.write(f"**Quiz title:** {selected_quiz_title}")
        st.write(f"**Quiz ID:** {selected_quiz_id}")

        if st.button("Reset current quiz"):
            reset_quiz_state()
            st.rerun()

        if st.button("Clear cache"):
            st.cache_data.clear()
            st.rerun()

        st.divider()
        st.write("**Question sheet URL**")
        st.caption(question_sheet_url)

        st.write("**Video URL**")
        st.caption(youtube_url if youtube_url else "No video link")

# -----------------------------------
# LOAD QUIZ QUESTIONS
# -----------------------------------
try:
    quiz_df = load_google_sheet(question_sheet_url)
except Exception as e:
    st.error(f"Could not load quiz questions: {e}")
    st.stop()

missing_quiz_cols = validate_quiz_df(quiz_df)
if missing_quiz_cols:
    st.error(f"Quiz sheet is missing columns: {', '.join(missing_quiz_cols)}")
    st.stop()

quiz_df = quiz_df.fillna("")

quiz_id = f"{selected_quiz_id}|{selected_quiz_title}|{len(quiz_df)}"
if st.session_state.get("quiz_id") != quiz_id:
    clear_question_state_only()
    st.session_state["quiz_id"] = quiz_id

# -----------------------------------
# VIDEO
# -----------------------------------
st.divider()
st.subheader("🎬 Video")

if youtube_url:
    st.video(youtube_url)
else:
    st.info("No video link has been added for this quiz.")

# -----------------------------------
# QUIZ
# -----------------------------------
st.divider()
st.subheader("📋 Quiz")

answers = {}
correct_answers = {}
questions = {}

for i, row in quiz_df.iterrows():
    shuffled_options, new_correct_letter = shuffle_question(row, seed=i)
    display_options = format_options(shuffled_options)
    correct_display = make_correct_display(shuffled_options, new_correct_letter)

    selected = st.radio(
        f"{i + 1}. {row['question']}",
        display_options,
        index=None,
        key=f"q_{i}"
    )

    answers[i] = selected
    correct_answers[i] = correct_display
    questions[i] = str(row["question"])

submit_clicked = st.button("Submit Quiz", disabled=st.session_state.get("submitted", False))

if submit_clicked:
    unanswered = [i + 1 for i, answer in answers.items() if answer is None]

    if unanswered:
        st.error(f"Please answer all questions before submitting. Missing: {', '.join(map(str, unanswered))}")
    else:
        score = 0
        total = len(quiz_df)

        for i in answers:
            is_correct = answers[i] == correct_answers[i]

            if is_correct:
                score += 1

            save_question_analytics(
                quiz_title=selected_quiz_title,
                email=email,
                role=role,
                q_num=i + 1,
                question=questions[i],
                selected=answers[i],
                correct=correct_answers[i],
                is_correct=is_correct,
            )

        save_result(
            name=name,
            email=email,
            role=role,
            quiz_title=selected_quiz_title,
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

    if st.button("Start this quiz again"):
        clear_question_state_only()
        st.rerun()

    with st.expander("Review answers"):
        for i in questions:
            st.write(f"**Q{i + 1}. {questions[i]}**")
            st.write(f"Your answer: {answers[i]}")
            st.write(f"Correct answer: {correct_answers[i]}")
            st.write("---")

# -----------------------------------
# TEACHER-ONLY LEADERBOARD
# -----------------------------------
if is_teacher_mode:
    st.divider()
    st.subheader("🏆 Leaderboard")

    results_df, analytics_df = load_results_from_sheets()

    if not results_df.empty:
        results_df = results_df[results_df["Quiz Title"] == selected_quiz_title].copy()

        if not results_df.empty:
            results_df["Percent"] = pd.to_numeric(results_df["Percent"], errors="coerce")
            leaderboard = (
                results_df
                .sort_values(by=["Percent", "Timestamp"], ascending=[False, True])
                .head(10)
            )
            st.dataframe(leaderboard, use_container_width=True)
        else:
            st.info("No results yet for this quiz.")
    else:
        st.info("No results yet.")

# -----------------------------------
# TEACHER DASHBOARD
# -----------------------------------
if is_teacher_mode:
    st.divider()
    st.subheader("📊 Teacher Dashboard")

    results_df, analytics_df = load_results_from_sheets()

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Results")

        if not results_df.empty:
            filtered_results = results_df[results_df["Quiz Title"] == selected_quiz_title].copy()

            if not filtered_results.empty:
                filtered_results["Percent"] = pd.to_numeric(filtered_results["Percent"], errors="coerce")
                st.dataframe(filtered_results, use_container_width=True)
                st.metric("Average %", round(filtered_results["Percent"].mean(), 1))

                results_csv = filtered_results.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download results CSV",
                    data=results_csv,
                    file_name=f"{selected_quiz_title}_results.csv",
                    mime="text/csv"
                )
            else:
                st.info("No results yet for this quiz.")
        else:
            st.info("No results sheet data yet.")

    with col2:
        st.write("### Question Analysis")

        if not analytics_df.empty:
            filtered_analytics = analytics_df[analytics_df["Quiz Title"] == selected_quiz_title].copy()

            if not filtered_analytics.empty:
                filtered_analytics["Is Correct"] = (
                    filtered_analytics["Is Correct"]
                    .astype(str)
                    .str.lower()
                    .isin(["true", "1", "yes"])
                )

                filtered_analytics["Question Number"] = pd.to_numeric(
                    filtered_analytics["Question Number"], errors="coerce"
                )

                stats = (
                    filtered_analytics.groupby(["Question Number", "Question"], as_index=False)
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
                    file_name=f"{selected_quiz_title}_question_analysis.csv",
                    mime="text/csv"
                )
            else:
                st.info("No analytics yet for this quiz.")
        else:
            st.info("No analytics sheet data yet.")
