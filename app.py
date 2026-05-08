import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Pow WOW Learning", layout="wide")

# -----------------------------------
# STYLE
# -----------------------------------
st.markdown(
    """
<style>
.block-container {
    max-width: 980px;
}

.pow-hero {
    background: linear-gradient(135deg, #1A2B4C 0%, #243C68 100%);
    color: white;
    border-radius: 18px;
    padding: 24px 28px;
    margin-bottom: 1rem;
}

.pow-question {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
}

.pow-score {
    font-size: 2rem;
    font-weight: 700;
    color: #F4B400;
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------
# CONFIG
# -----------------------------------
QUIZ_CATALOGUE_URL = "https://docs.google.com/spreadsheets/d/1M6QJOgDr5BYtsxpxLA-u1_RYRCugzlINQOUrVsTin-o/edit?usp=sharing"

COURSES = ["IGCSE Economics", "A Level Economics"]
CAMPUSES = ["NR", "PU", "TR", "CM"]

CAMPUS_CLASSES = {
    "NR": [
        "G9B", "G9S", "G9M", "G9G",
        "G10L", "G10VG", "G10P", "G10M",
        "G11A", "G11S", "G11V", "G11P",
        "G12G", "G12M", "G12P", "G12U",
    ],
    "PU": [
        "G9B", "G9S", "G9M", "G9G",
        "G10L", "G10VG", "G10P", "G10M",
        "G11A", "G11S", "G11V", "G11P",
        "G12G", "G12M", "G12P", "G12U",
    ],
    "TR": [
        "G9B", "G9S", "G9M", "G9G",
        "G10L", "G10VG", "G10P", "G10M",
        "G11A", "G11S", "G11V", "G11P",
        "G12G", "G12M", "G12P", "G12U",
    ],
    "CM": [
        "G9B", "G9S", "G9M", "G9G",
        "G10L", "G10VG", "G10P", "G10M",
        "G11A", "G11S", "G11V", "G11P",
        "G12G", "G12M", "G12P", "G12U",
    ],
}

RESULTS_SHEETS = {
    "IGCSE Economics": {
        "NR": "IGCSE_Results_NR",
        "PU": "IGCSE_Results_PU",
        "TR": "IGCSE_Results_TR",
        "CM": "IGCSE_Results_CM",
    },
    "A Level Economics": {
        "NR": "ALevel_Results_NR",
        "PU": "ALevel_Results_PU",
        "TR": "ALevel_Results_TR",
        "CM": "ALevel_Results_CM",
    },
}

RESULTS_HEADERS = [
    "Name",
    "Email",
    "Course",
    "Campus",
    "Class",
    "Quiz Title",
    "Score",
    "Total",
    "Percent",
    "Timestamp",
]

QUIZ_REQUIRED_COLUMNS = [
    "question",
    "option_a",
    "option_b",
    "option_c",
    "option_d",
    "correct_answer",
]

# -----------------------------------
# SESSION STATE
# -----------------------------------
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "quiz_df" not in st.session_state:
    st.session_state.quiz_df = None

if "quiz_title" not in st.session_state:
    st.session_state.quiz_title = None

if "shuffled_options" not in st.session_state:
    st.session_state.shuffled_options = {}

if "saved_result" not in st.session_state:
    st.session_state.saved_result = False

# -----------------------------------
# GOOGLE SHEETS
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
def get_results_spreadsheet():
    client = get_gspread_client()
    spreadsheet = client.open_by_url(
        st.secrets["results_sheet"]["spreadsheet_url"]
    )
    return spreadsheet


def ensure_headers(ws):
    values = ws.get_all_values()

    if not values:
        ws.append_row(RESULTS_HEADERS)


def save_result(
    name,
    email,
    course,
    campus,
    student_class,
    quiz_title,
    score,
    total,
):
    spreadsheet = get_results_spreadsheet()

    sheet_name = RESULTS_SHEETS[course][campus]

    worksheet = spreadsheet.worksheet(sheet_name)

    ensure_headers(worksheet)

    percent = round((score / total) * 100, 1)

    worksheet.append_row([
        name,
        email,
        course,
        campus,
        student_class,
        quiz_title,
        score,
        total,
        percent,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ])

# -----------------------------------
# HELPERS
# -----------------------------------
def clean_columns(df):
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def convert_sheet_url(url: str) -> str:
    if "export?format=csv" in url:
        return url

    sheet_id = url.split("/d/")[1].split("/")[0]
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"


@st.cache_data(ttl=60)
def load_google_sheet(sheet_url):
    csv_url = convert_sheet_url(sheet_url)
    df = pd.read_csv(csv_url)
    df = clean_columns(df)
    return df


def validate_quiz_df(df):
    missing = [c for c in QUIZ_REQUIRED_COLUMNS if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    return df.reset_index(drop=True)


def shuffle_answers(row, seed):
    rng = random.Random(seed)

    options = {
        "A": row["option_a"],
        "B": row["option_b"],
        "C": row["option_c"],
        "D": row["option_d"],
    }

    correct_letter = row["correct_answer"].upper()
    correct_text = options[correct_letter]

    values = list(options.values())
    rng.shuffle(values)

    shuffled = dict(zip(["A", "B", "C", "D"], values))

    new_correct = next(
        letter for letter, text in shuffled.items()
        if text == correct_text
    )

    return shuffled, new_correct

# -----------------------------------
# HEADER
# -----------------------------------
st.markdown(
    """
    <div class="pow-hero">
        <h1>Pow WOW Learning</h1>
        <p>Interactive Economics Video Quizzes</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------
# STUDENT DETAILS
# -----------------------------------
name = st.text_input("Student name")
email = st.text_input("Student email")

course = st.selectbox("1. Select course", COURSES)

campus = st.selectbox("2. Select campus", CAMPUSES)

student_class = st.selectbox(
    "3. Select class",
    CAMPUS_CLASSES[campus]
)

if not name or not email:
    st.info("Please enter your name and email.")
    st.stop()

# -----------------------------------
# LOAD QUIZ CATALOGUE
# -----------------------------------
try:
    catalogue_df = load_google_sheet(QUIZ_CATALOGUE_URL)
except Exception as e:
    st.error(f"Could not load catalogue: {e}")
    st.stop()

quiz_titles = catalogue_df["quiz_title"].tolist()

selected_quiz = st.selectbox(
    "4. Select quiz/topic",
    quiz_titles
)

selected_row = catalogue_df[
    catalogue_df["quiz_title"] == selected_quiz
].iloc[0]

youtube_url = selected_row["youtube_url"]
question_sheet_url = selected_row["question_sheet_url"]

# -----------------------------------
# START QUIZ
# -----------------------------------
if not st.session_state.quiz_started:
    if st.button("5. Start quiz", use_container_width=True):

        quiz_df = load_google_sheet(question_sheet_url)
        quiz_df = validate_quiz_df(quiz_df)

        st.session_state.quiz_df = quiz_df
        st.session_state.quiz_title = selected_quiz
        st.session_state.quiz_started = True
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.shuffled_options = {}
        st.session_state.saved_result = False

        st.rerun()

if not st.session_state.quiz_started:
    st.stop()

# -----------------------------------
# VIDEO
# -----------------------------------
st.video(youtube_url)

# -----------------------------------
# QUIZ ENGINE
# -----------------------------------
quiz_df = st.session_state.quiz_df
current_q = st.session_state.current_q
score = st.session_state.score

if current_q >= len(quiz_df):

    percent = round((score / len(quiz_df)) * 100, 1)

    st.success("Quiz complete")

    st.markdown(
        f"<div class='pow-score'>{score}/{len(quiz_df)} ({percent}%)</div>",
        unsafe_allow_html=True,
    )

    if not st.session_state.saved_result:
        save_result(
            name,
            email,
            course,
            campus,
            student_class,
            st.session_state.quiz_title,
            score,
            len(quiz_df),
        )

        st.session_state.saved_result = True

    if st.button("Return to library"):
        st.session_state.quiz_started = False
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.quiz_df = None
        st.session_state.quiz_title = None
        st.session_state.shuffled_options = {}
        st.session_state.saved_result = False
        st.rerun()

    st.stop()

# -----------------------------------
# CURRENT QUESTION
# -----------------------------------
row = quiz_df.iloc[current_q]

st.progress(current_q / len(quiz_df))

st.write(f"Question {current_q + 1} of {len(quiz_df)}")

st.markdown(
    f"<div class='pow-question'>{row['question']}</div>",
    unsafe_allow_html=True,
)

question_key = f"q_{current_q}"

# IMPORTANT:
# QUESTIONS STAY IN ORIGINAL ORDER
# ONLY ANSWERS ARE RANDOMISED
if question_key not in st.session_state.shuffled_options:

    shuffled, correct_letter = shuffle_answers(
        row,
        current_q + 1000
    )

    st.session_state.shuffled_options[question_key] = {
        "options": shuffled,
        "correct": correct_letter,
    }

question_data = st.session_state.shuffled_options[question_key]

options = question_data["options"]
correct_letter = question_data["correct"]

cols = st.columns(2)

clicked = None

for idx, (letter, text) in enumerate(options.items()):
    with cols[idx % 2]:
        if st.button(
            f"{letter}. {text}",
            key=f"btn_{current_q}_{letter}",
            use_container_width=True,
        ):
            clicked = letter

if clicked:

    if clicked == correct_letter:
        st.success("Correct")
        st.session_state.score += 1
    else:
        st.error(f"Correct answer: {correct_letter}")

    if st.button("Next question", use_container_width=True):
        st.session_state.current_q += 1
        st.rerun()
