import random
from datetime import datetime

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Pow WOW Learning", layout="wide")

# -----------------------------------
# BRAND / STYLE
# -----------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap');

:root {
    --pow-navy: #1A2B4C;
    --pow-gold: #F4B400;
    --pow-white: #FFFFFF;
    --pow-gray: #9E9E9E;
    --pow-light: #F7F8FA;
    --pow-border: #E4E7EC;
    --pow-success: #2E7D32;
    --pow-error: #C62828;
}

html, body, [class*="css"]  {
    font-family: 'Open Sans', sans-serif;
}

h1, h2, h3, h4, .pow-heading, .pow-topic-title, .pow-quiz-title, .pow-question {
    font-family: 'Montserrat', sans-serif !important;
}

.block-container {
    max-width: 980px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

.pow-hero {
    background: linear-gradient(135deg, var(--pow-navy) 0%, #243C68 100%);
    color: white;
    border-radius: 18px;
    padding: 24px 28px;
    margin-bottom: 1rem;
    border: 1px solid rgba(255,255,255,0.08);
}

.pow-hero h1 {
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
    color: white;
}

.pow-hero p {
    margin: 0.35rem 0 0 0;
    color: rgba(255,255,255,0.88);
    font-size: 1rem;
}

.pow-meta {
    color: var(--pow-gray);
    font-size: 0.95rem;
    margin-top: 0.35rem;
}

.pow-section-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--pow-navy);
    margin: 1rem 0 0.5rem 0;
}

.pow-topic-note {
    color: var(--pow-gray);
    margin-bottom: 1rem;
}

div[data-testid="stExpander"] {
    border: 1px solid var(--pow-border);
    border-radius: 14px;
    background: white;
    margin-bottom: 16px;
}

div[data-testid="stExpander"] summary {
    font-family: 'Montserrat', sans-serif;
    font-weight: 700;
    color: var(--pow-navy);
}

.pow-topic-progress {
    color: var(--pow-gray);
    font-size: 0.95rem;
    margin-top: 0.25rem;
}

.pow-card {
    border: 1px solid var(--pow-border);
    border-radius: 14px;
    background: white;
    padding: 18px;
    min-height: 138px;
    margin-bottom: 12px;
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
}

.pow-card:hover {
    border-color: #CED4DA;
    background: #FCFCFD;
}

.pow-quiz-title {
    font-size: 1.08rem;
    font-weight: 700;
    color: var(--pow-navy);
    margin-bottom: 0.4rem;
    line-height: 1.35;
}

.pow-quiz-topic {
    color: var(--pow-gray);
    font-size: 0.92rem;
    margin-bottom: 0.55rem;
}

.pow-chip {
    display: inline-block;
    background: #FFF4CC;
    color: #7A5A00;
    border: 1px solid #F4D36A;
    border-radius: 999px;
    font-size: 0.82rem;
    padding: 3px 10px;
    margin-top: 0.2rem;
}

.pow-divider {
    margin: 1.25rem 0 1rem 0;
}

.pow-video-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--pow-navy);
    margin-bottom: 0.65rem;
}

.pow-quiz-shell {
    border: 1px solid var(--pow-border);
    border-radius: 18px;
    background: white;
    padding: 22px;
    box-shadow: 0 2px 8px rgba(16, 24, 40, 0.04);
}

.pow-question-meta {
    color: var(--pow-gray);
    font-size: 0.95rem;
    margin-bottom: 0.75rem;
    text-align: center;
}

.pow-question {
    font-size: 1.45rem;
    font-weight: 700;
    color: var(--pow-navy);
    line-height: 1.45;
    text-align: center;
    margin: 0.75rem 0 1.25rem 0;
}

div[data-testid="stButton"] > button {
    border-radius: 12px !important;
    min-height: 64px !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    white-space: normal !important;
    text-align: left !important;
    justify-content: flex-start !important;
    border: 1px solid var(--pow-border) !important;
    background: #FAFAFA !important;
    color: #222 !important;
    padding: 0.75rem 1rem !important;
    box-shadow: none !important;
}

div[data-testid="stButton"] > button:hover {
    border-color: #C7CDD4 !important;
    background: #F3F5F7 !important;
}

.pow-answer-area {
    margin-top: 0.5rem;
}

.pow-feedback-ok {
    color: var(--pow-success);
    font-weight: 700;
    font-family: 'Montserrat', sans-serif;
    font-size: 1rem;
    margin-top: 1rem;
}

.pow-feedback-bad {
    color: var(--pow-error);
    font-weight: 700;
    font-family: 'Montserrat', sans-serif;
    font-size: 1rem;
    margin-top: 1rem;
}

.pow-score-box {
    border: 1px solid var(--pow-border);
    border-radius: 18px;
    background: white;
    padding: 26px;
    text-align: center;
    margin-top: 1rem;
}

.pow-score-box h2 {
    color: var(--pow-navy);
    margin-bottom: 0.5rem;
}

.pow-score-big {
    font-family: 'Montserrat', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--pow-gold);
}

.pow-small-muted {
    color: var(--pow-gray);
    font-size: 0.92rem;
}

[data-testid="stSidebar"] {
    background: #FBFBFC;
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------
# CONFIG
# -----------------------------------
ADMIN_EMAILS = {"james.p@sisbschool.com"}
QUIZ_CATALOGUE_URL = "https://docs.google.com/spreadsheets/d/1M6QJOgDr5BYtsxpxLA-u1_RYRCugzlINQOUrVsTin-o/edit?usp=sharing"

TOPIC_ORDER = [
    "1. The Basic Economic Problem",
    "2. The Allocation of Resources",
    "3. Microeconomic Decision Makers",
    "4. Government & The Macroeconomy",
    "5. Economic Development",
    "6. International Trade & Globalisation",
]

RESULTS_HEADERS = [
    "Name",
    "Email",
    "Role",
    "Quiz Title",
    "Score",
    "Total",
    "Percent",
    "Timestamp",
]

ANALYTICS_HEADERS = [
    "Quiz Title",
    "Email",
    "Role",
    "Question Number",
    "Question",
    "Selected Answer",
    "Correct Answer",
    "Is Correct",
    "Timestamp",
]

# -----------------------------------
# GOOGLE SHEETS CONNECTION
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

    results_values = results_ws.get_all_values()
    analytics_values = analytics_ws.get_all_values()

    if not results_values:
        results_ws.append_row(RESULTS_HEADERS)
    else:
        if results_values[0] != RESULTS_HEADERS:
            results_ws.clear()
            results_ws.append_row(RESULTS_HEADERS)

    if not analytics_values:
        analytics_ws.append_row(ANALYTICS_HEADERS)
    else:
        if analytics_values[0] != ANALYTICS_HEADERS:
            analytics_ws.clear()
            analytics_ws.append_row(ANALYTICS_HEADERS)


def worksheet_to_df(ws, headers):
    values = ws.get_all_values()

    if not values:
        return pd.DataFrame(columns=headers)

    if values[0] != headers:
        return pd.DataFrame(columns=headers)

    data_rows = values[1:]
    if not data_rows:
        return pd.DataFrame(columns=headers)

    cleaned_rows = []
    for row in data_rows:
        if len(row) < len(headers):
            row = row + [""] * (len(headers) - len(row))
        elif len(row) > len(headers):
            row = row[:len(headers)]
        cleaned_rows.append(row)

    return pd.DataFrame(cleaned_rows, columns=headers)


def load_results_from_sheets():
    ensure_sheet_headers()
    results_ws, analytics_ws = get_results_workbooks()

    results_df = worksheet_to_df(results_ws, RESULTS_HEADERS)
    analytics_df = worksheet_to_df(analytics_ws, ANALYTICS_HEADERS)

    return results_df, analytics_df


def save_result(name, email, role, quiz_title, score, total):
    ensure_sheet_headers()
    results_ws, _ = get_results_workbooks()
    percent = round((score / total) * 100, 1) if total > 0 else 0
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
    ensure_sheet_headers()
    _, analytics_ws = get_results_workbooks()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
def convert_sheet_url(url: str) -> str:
    url = str(url).strip()

    if "export?format=csv" in url:
        return url

    if "/d/" not in url:
        raise ValueError("Invalid Google Sheets URL")

    sheet_id = url.split("/d/")[1].split("/")[0]
    gid = "0"
    if "gid=" in url:
        gid = url.split("gid=")[1].split("&")[0]

    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


@st.cache_data(show_spinner=False)
def load_google_sheet(sheet_url: str) -> pd.DataFrame:
    csv_url = convert_sheet_url(sheet_url)
    return pd.read_csv(csv_url)


def visible(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def normalise_catalogue(df: pd.DataFrame) -> pd.DataFrame:
    df = df.fillna("").copy()

    if "visible" in df.columns:
        df = df[df["visible"].apply(visible)].copy()

    if "topic" not in df.columns:
        df["topic"] = ""

    required_cols = ["quiz_id", "quiz_title", "youtube_url", "question_sheet_url"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Catalogue sheet is missing columns: {', '.join(missing)}")

    return df


def validate_quiz_df(df: pd.DataFrame):
    required = ["question", "option_a", "option_b", "option_c", "option_d", "correct_answer"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Quiz sheet is missing columns: {', '.join(missing)}")


def shuffle_options(row: pd.Series, seed: int):
    rng = random.Random(seed)
    options = {
        "A": str(row["option_a"]).strip(),
        "B": str(row["option_b"]).strip(),
        "C": str(row["option_c"]).strip(),
        "D": str(row["option_d"]).strip(),
    }
    correct_letter = str(row["correct_answer"]).strip().upper()
    correct_text = options[correct_letter]

    values = list(options.values())
    rng.shuffle(values)

    shuffled = dict(zip(["A", "B", "C", "D"], values))
    new_correct = next(k for k, v in shuffled.items() if v == correct_text)
    return shuffled, new_correct


def reset_quiz_state(full_library_reset: bool = False):
    keys = [
        "selected_quiz_id",
        "selected_quiz_title",
        "question_order",
        "question_option_map",
        "current_q",
        "score",
        "answered_current",
        "current_feedback",
        "final_saved",
        "quiz_complete",
        "quiz_seed",
    ]
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]

    if full_library_reset and "selected_quiz_title" in st.session_state:
        del st.session_state["selected_quiz_title"]


def get_user_topic_progress(results_df: pd.DataFrame, catalogue_df: pd.DataFrame, email: str):
    progress = {}
    if results_df.empty:
        for topic in TOPIC_ORDER:
            total = len(catalogue_df[catalogue_df["topic"] == topic])
            progress[topic] = (0, total)
        return progress

    user_results = results_df[results_df["Email"].astype(str).str.lower() == email.lower()].copy()
    completed_quizzes = set(user_results["Quiz Title"].astype(str).tolist())

    for topic in TOPIC_ORDER:
        topic_quizzes = catalogue_df[catalogue_df["topic"] == topic]["quiz_title"].astype(str).tolist()
        total = len(topic_quizzes)
        completed = len([q for q in topic_quizzes if q in completed_quizzes])
        progress[topic] = (completed, total)

    return progress


def build_quiz_attempt_data(quiz_df: pd.DataFrame, quiz_seed: int):
    rng = random.Random(quiz_seed)
    question_order = list(range(len(quiz_df)))
    rng.shuffle(question_order)

    option_map = {}
    for position, original_index in enumerate(question_order):
        row = quiz_df.iloc[original_index]
        shuffled_options, correct_letter = shuffle_options(row, seed=quiz_seed + original_index + position)
        option_map[position] = {
            "options": shuffled_options,
            "correct_letter": correct_letter,
        }

    return question_order, option_map


def get_selected_quiz_row(catalogue_df: pd.DataFrame, selected_quiz_title: str):
    matches = catalogue_df[catalogue_df["quiz_title"] == selected_quiz_title]
    if matches.empty:
        return None
    return matches.iloc[0]


# -----------------------------------
# AUTH
# -----------------------------------
user_dict = st.user.to_dict()

if "is_logged_in" not in user_dict:
    st.error("Authentication is not configured correctly yet.")
    st.stop()

if not st.user.is_logged_in:
    st.markdown(
        """
        <div class="pow-hero">
            <h1>Pow WOW Learning</h1>
            <p>Interactive video learning with instant feedback</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.button("Login with Google", on_click=st.login, use_container_width=True)
    st.stop()

name = getattr(st.user, "name", "Student")
email = getattr(st.user, "email", "")

# -----------------------------------
# HEADER
# -----------------------------------
st.markdown(
    """
    <div class="pow-hero">
        <h1>Pow WOW Learning</h1>
        <p>Interactive video learning with instant feedback</p>
    </div>
    """,
    unsafe_allow_html=True,
)

top_left, top_right = st.columns([5, 1])
with top_left:
    st.markdown(
        f"<div class='pow-meta'>Signed in as <strong>{name}</strong> ({email})</div>",
        unsafe_allow_html=True,
    )
with top_right:
    if st.button("Logout", use_container_width=True):
        st.logout()

st.markdown("<div class='pow-divider'></div>", unsafe_allow_html=True)

# -----------------------------------
# ROLE
# -----------------------------------
role = st.radio("Role", ["Student", "Teacher"], horizontal=True)

is_teacher_mode = role == "Teacher"
if is_teacher_mode and email not in ADMIN_EMAILS:
    st.warning("Teacher mode is restricted.")
    st.stop()

# -----------------------------------
# LOAD DATA
# -----------------------------------
try:
    catalogue_df = load_google_sheet(QUIZ_CATALOGUE_URL)
    catalogue_df = normalise_catalogue(catalogue_df)
except Exception as e:
    st.error(f"Could not load quiz catalogue: {e}")
    st.stop()

try:
    results_df, analytics_df = load_results_from_sheets()
except Exception as e:
    st.error(f"Could not load results sheets: {e}")
    st.stop()

topic_progress = get_user_topic_progress(results_df, catalogue_df, email)

# -----------------------------------
# SIDEBAR
# -----------------------------------
with st.sidebar:
    st.markdown("### Pow WOW Learning")
    st.caption("Teacher tools and utilities")

    if st.button("Reset quiz session", use_container_width=True):
        reset_quiz_state(full_library_reset=False)
        st.rerun()

    if st.button("Return to quiz library", use_container_width=True):
        reset_quiz_state(full_library_reset=True)
        st.rerun()

    if st.button("Clear data cache", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    if is_teacher_mode and st.session_state.get("selected_quiz_title"):
        st.markdown("---")
        st.markdown("#### Current Quiz")
        st.caption(st.session_state.get("selected_quiz_title", ""))

# -----------------------------------
# QUIZ LIBRARY
# -----------------------------------
if "selected_quiz_title" not in st.session_state:
    st.session_state.selected_quiz_title = None

if not st.session_state.selected_quiz_title:
    st.markdown("<div class='pow-section-title'>Browse by Topic</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='pow-topic-note'>Choose a topic, then launch a quiz. Progress is based on quizzes you’ve already completed.</div>",
        unsafe_allow_html=True,
    )

    for topic in TOPIC_ORDER:
        topic_df = catalogue_df[catalogue_df["topic"] == topic].copy()
        if topic_df.empty:
            continue

        completed, total = topic_progress.get(topic, (0, len(topic_df)))
        expander_label = f"{topic}   ·   {completed}/{total} completed"

        with st.expander(expander_label, expanded=False):
            st.markdown(
                f"<div class='pow-topic-progress'>You have completed {completed} of {total} quizzes in this topic.</div>",
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)

            cols = st.columns(2)
            for idx, (_, row) in enumerate(topic_df.iterrows()):
                with cols[idx % 2]:
                    st.markdown(
                        f"""
                        <div class="pow-card">
                            <div class="pow-quiz-title">{row['quiz_title']}</div>
                            <div class="pow-quiz-topic">{row['topic']}</div>
                            <div class="pow-chip">Video quiz</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("Start quiz", key=f"start_{row['quiz_id']}", use_container_width=True):
                        st.session_state.selected_quiz_title = row["quiz_title"]
                        reset_quiz_state(full_library_reset=False)
                        st.session_state.selected_quiz_title = row["quiz_title"]
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

    st.stop()

# -----------------------------------
# LOAD SELECTED QUIZ
# -----------------------------------
selected_quiz_title = st.session_state.selected_quiz_title
selected_row = get_selected_quiz_row(catalogue_df, selected_quiz_title)

if selected_row is None:
    st.error("Selected quiz could not be found in the catalogue.")
    st.stop()

selected_quiz_id = selected_row["quiz_id"]
youtube_url = str(selected_row["youtube_url"]).strip()
question_sheet_url = str(selected_row["question_sheet_url"]).strip()
selected_topic = str(selected_row.get("topic", "")).strip()

try:
    quiz_df = load_google_sheet(question_sheet_url)
    quiz_df = quiz_df.fillna("")
    validate_quiz_df(quiz_df)
except Exception as e:
    st.error(f"Could not load quiz questions: {e}")
    st.stop()

# -----------------------------------
# INITIALISE ATTEMPT
# -----------------------------------
if "quiz_seed" not in st.session_state:
    st.session_state.quiz_seed = random.randint(100000, 999999)

if "question_order" not in st.session_state or "question_option_map" not in st.session_state:
    question_order, option_map = build_quiz_attempt_data(quiz_df, st.session_state.quiz_seed)
    st.session_state.question_order = question_order
    st.session_state.question_option_map = option_map

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "answered_current" not in st.session_state:
    st.session_state.answered_current = False

if "current_feedback" not in st.session_state:
    st.session_state.current_feedback = None

if "quiz_complete" not in st.session_state:
    st.session_state.quiz_complete = False

if "final_saved" not in st.session_state:
    st.session_state.final_saved = False

# -----------------------------------
# QUIZ HEADER
# -----------------------------------
back_col, title_col = st.columns([1, 5])
with back_col:
    if st.button("← Library", use_container_width=True):
        reset_quiz_state(full_library_reset=True)
        st.rerun()

with title_col:
    st.markdown(f"<div class='pow-section-title'>{selected_quiz_title}</div>", unsafe_allow_html=True)
    if selected_topic:
        st.markdown(f"<div class='pow-small-muted'>{selected_topic}</div>", unsafe_allow_html=True)

st.markdown("<div class='pow-divider'></div>", unsafe_allow_html=True)

# -----------------------------------
# VIDEO
# -----------------------------------
st.markdown("<div class='pow-video-title'>Watch the video</div>", unsafe_allow_html=True)
if youtube_url:
    st.video(youtube_url)
else:
    st.info("No video link has been added for this quiz.")

st.markdown("<div class='pow-divider'></div>", unsafe_allow_html=True)

# -----------------------------------
# QUIZ ENGINE
# -----------------------------------
question_order = st.session_state.question_order
option_map = st.session_state.question_option_map
current_position = st.session_state.current_q
total_questions = len(question_order)

if current_position >= total_questions:
    st.session_state.quiz_complete = True

if not st.session_state.quiz_complete:
    progress_value = current_position / total_questions if total_questions else 0
    st.progress(progress_value)
    st.markdown(
        f"<div class='pow-question-meta'>Question {current_position + 1} of {total_questions}</div>",
        unsafe_allow_html=True,
    )

    original_index = question_order[current_position]
    row = quiz_df.iloc[original_index]
    current_map = option_map[current_position]
    options = current_map["options"]
    correct_letter = current_map["correct_letter"]

    st.markdown(
        f"<div class='pow-quiz-shell'><div class='pow-question'>{row['question']}</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='pow-answer-area'></div>", unsafe_allow_html=True)
    cols = st.columns(2)
    clicked = None

    for idx, (letter, text) in enumerate(options.items()):
        with cols[idx % 2]:
            if st.button(f"{letter}. {text}", key=f"answer_{current_position}_{letter}", use_container_width=True):
                clicked = letter

    if clicked and not st.session_state.answered_current:
        is_correct = clicked == correct_letter
        st.session_state.answered_current = True
        st.session_state.current_feedback = {
            "selected": clicked,
            "correct": correct_letter,
            "is_correct": is_correct,
            "correct_text": options[correct_letter],
            "question_text": row["question"],
        }

        if is_correct:
            st.session_state.score += 1

        save_question_analytics(
            selected_quiz_title,
            email,
            role,
            current_position + 1,
            row["question"],
            clicked,
            correct_letter,
            is_correct,
        )
        st.rerun()

    if st.session_state.answered_current and st.session_state.current_feedback:
        feedback = st.session_state.current_feedback
        if feedback["is_correct"]:
            st.markdown("<div class='pow-feedback-ok'>Correct</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div class='pow-feedback-bad'>Correct answer: {feedback['correct']}. {feedback['correct_text']}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        if current_position < total_questions - 1:
            if st.button("Next question", use_container_width=True):
                st.session_state.current_q += 1
                st.session_state.answered_current = False
                st.session_state.current_feedback = None
                st.rerun()
        else:
            st.session_state.quiz_complete = True
            st.rerun()

# -----------------------------------
# FINAL SCORE
# -----------------------------------
if st.session_state.quiz_complete:
    score = st.session_state.score
    percent = round((score / total_questions) * 100, 1) if total_questions else 0

    if not st.session_state.final_saved:
        save_result(name, email, role, selected_quiz_title, score, total_questions)
        st.session_state.final_saved = True

    st.markdown(
        f"""
        <div class="pow-score-box">
            <h2>Quiz complete</h2>
            <div class="pow-score-big">{score}/{total_questions} ({percent}%)</div>
            <div class="pow-small-muted">Your result has been saved.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Try again", use_container_width=True):
            reset_quiz_state(full_library_reset=False)
            st.session_state.selected_quiz_title = selected_quiz_title
            st.rerun()

    with c2:
        if st.button("Back to library", use_container_width=True):
            reset_quiz_state(full_library_reset=True)
            st.rerun()

# -----------------------------------
# TEACHER DASHBOARD
# -----------------------------------
if is_teacher_mode:
    st.markdown("<div class='pow-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='pow-section-title'>Teacher Dashboard</div>", unsafe_allow_html=True)

    filtered_results = results_df.copy()
    if not filtered_results.empty:
        filtered_results = filtered_results[filtered_results["Quiz Title"] == selected_quiz_title].copy()

    filtered_analytics = analytics_df.copy()
    if not filtered_analytics.empty:
        filtered_analytics = filtered_analytics[filtered_analytics["Quiz Title"] == selected_quiz_title].copy()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Results")
        if filtered_results.empty:
            st.info("No results yet for this quiz.")
        else:
            filtered_results["Percent"] = pd.to_numeric(filtered_results["Percent"], errors="coerce")
            st.dataframe(filtered_results, use_container_width=True)
            st.metric("Average %", round(filtered_results["Percent"].mean(), 1))

    with col2:
        st.markdown("#### Question Analysis")
        if filtered_analytics.empty:
            st.info("No analytics yet for this quiz.")
        else:
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
