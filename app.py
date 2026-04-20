import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

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

html, body, [class*="css"] {
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
UNCATEGORIZED_TOPIC = "Other Quizzes"

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

QUIZ_REQUIRED_COLUMNS = [
    "question",
    "option_a",
    "option_b",
    "option_c",
    "option_d",
    "correct_answer",
]

CATALOGUE_REQUIRED_COLUMNS = [
    "quiz_id",
    "quiz_title",
    "youtube_url",
    "question_sheet_url",
]

# -----------------------------------
# STATE
# -----------------------------------
def init_app_state() -> None:
    defaults = {
        "page": "library",
        "selected_quiz_title": None,
        "selected_quiz_id": None,
        "attempt": {},
        "results_headers_checked": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_attempt_state() -> None:
    st.session_state.attempt = {}


def go_to_library() -> None:
    reset_attempt_state()
    st.session_state.selected_quiz_title = None
    st.session_state.selected_quiz_id = None
    st.session_state.page = "library"


def open_quiz(quiz_row: pd.Series) -> None:
    reset_attempt_state()
    st.session_state.selected_quiz_title = str(quiz_row["quiz_title"]).strip()
    st.session_state.selected_quiz_id = str(quiz_row["quiz_id"]).strip()
    st.session_state.page = "quiz"


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
def get_results_workbooks():
    client = get_gspread_client()
    spreadsheet = client.open_by_url(st.secrets["results_sheet"]["spreadsheet_url"])
    results_ws = spreadsheet.worksheet(st.secrets["results_sheet"]["results_worksheet"])
    analytics_ws = spreadsheet.worksheet(st.secrets["results_sheet"]["analytics_worksheet"])
    return results_ws, analytics_ws


def worksheet_to_df(ws, headers: List[str]) -> pd.DataFrame:
    values = ws.get_all_values()
    if not values:
        return pd.DataFrame(columns=headers)

    header_row = values[0]
    if header_row != headers:
        return pd.DataFrame(columns=headers)

    data_rows = values[1:]
    cleaned_rows = []
    for row in data_rows:
        if len(row) < len(headers):
            row = row + [""] * (len(headers) - len(row))
        elif len(row) > len(headers):
            row = row[: len(headers)]
        cleaned_rows.append(row)

    return pd.DataFrame(cleaned_rows, columns=headers)


def ensure_sheet_headers() -> None:
    if st.session_state.get("results_headers_checked"):
        return

    results_ws, analytics_ws = get_results_workbooks()

    results_values = results_ws.get_all_values()
    analytics_values = analytics_ws.get_all_values()

    if not results_values:
        results_ws.append_row(RESULTS_HEADERS)
    elif results_values[0] != RESULTS_HEADERS:
        results_ws.clear()
        results_ws.append_row(RESULTS_HEADERS)

    if not analytics_values:
        analytics_ws.append_row(ANALYTICS_HEADERS)
    elif analytics_values[0] != ANALYTICS_HEADERS:
        analytics_ws.clear()
        analytics_ws.append_row(ANALYTICS_HEADERS)

    st.session_state["results_headers_checked"] = True


@st.cache_data(ttl=60, show_spinner=False)
def load_results_from_sheets_cached() -> Tuple[pd.DataFrame, pd.DataFrame]:
    results_ws, analytics_ws = get_results_workbooks()
    results_df = worksheet_to_df(results_ws, RESULTS_HEADERS)
    analytics_df = worksheet_to_df(analytics_ws, ANALYTICS_HEADERS)
    return results_df, analytics_df


def load_results_from_sheets() -> Tuple[pd.DataFrame, pd.DataFrame]:
    ensure_sheet_headers()
    return load_results_from_sheets_cached()


def save_result(name: str, email: str, role: str, quiz_title: str, score: int, total: int) -> None:
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
    load_results_from_sheets_cached.clear()


def save_question_analytics(
    quiz_title: str,
    email: str,
    role: str,
    q_num: int,
    question: str,
    selected: str,
    correct: str,
    is_correct: bool,
) -> None:
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
    load_results_from_sheets_cached.clear()


# -----------------------------------
# DATA HELPERS
# -----------------------------------
def visible(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def clean_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [clean_text(c).lower() for c in df.columns]
    return df


def convert_sheet_url(url: str) -> str:
    url = clean_text(url)
    if "export?format=csv" in url:
        return url
    if "/d/" not in url:
        raise ValueError("Invalid Google Sheets URL")
    sheet_id = url.split("/d/")[1].split("/")[0]
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"


@st.cache_data(show_spinner=False)
def load_google_sheet(sheet_url: str) -> pd.DataFrame:
    csv_url = convert_sheet_url(sheet_url)
    df = pd.read_csv(csv_url)
    df = clean_columns(df)
    return df


def normalize_topic_name(topic: str) -> str:
    topic = clean_text(topic)
    canonical = {t.casefold(): t for t in TOPIC_ORDER}
    return canonical.get(topic.casefold(), topic)


def normalise_catalogue(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_columns(df).fillna("").copy()

    for col in df.columns:
        df[col] = df[col].apply(clean_text)

    if "visible" in df.columns:
        df = df[df["visible"].apply(visible)].copy()

    missing = [c for c in CATALOGUE_REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Catalogue sheet is missing columns: {', '.join(missing)}")

    if "topic" not in df.columns:
        df["topic"] = ""

    df["topic"] = df["topic"].apply(normalize_topic_name)
    df["quiz_id"] = df["quiz_id"].replace("", pd.NA)
    df["quiz_id"] = df["quiz_id"].fillna(df["quiz_title"])

    return df


def validate_quiz_df(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_columns(df).fillna("").copy()
    for col in df.columns:
        df[col] = df[col].apply(clean_text)

    missing = [c for c in QUIZ_REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Quiz sheet is missing columns: {', '.join(missing)}")

    df = df[QUIZ_REQUIRED_COLUMNS + (["explanation"] if "explanation" in df.columns else [])].copy()
    df["correct_answer"] = df["correct_answer"].str.upper()
    df = df[df["question"] != ""].copy()

    valid_letters = {"A", "B", "C", "D"}
    invalid = df[~df["correct_answer"].isin(valid_letters)]
    if not invalid.empty:
        raise ValueError("Every row in correct_answer must be A, B, C, or D.")

    return df.reset_index(drop=True)


def shuffle_options_for_row(row: pd.Series, seed: int) -> Dict[str, object]:
    rng = random.Random(seed)
    original_options = {
        "A": clean_text(row["option_a"]),
        "B": clean_text(row["option_b"]),
        "C": clean_text(row["option_c"]),
        "D": clean_text(row["option_d"]),
    }
    correct_letter = clean_text(row["correct_answer"]).upper()
    correct_text = original_options[correct_letter]

    option_values = list(original_options.values())
    rng.shuffle(option_values)
    shuffled_options = dict(zip(["A", "B", "C", "D"], option_values))
    new_correct_letter = next(letter for letter, text in shuffled_options.items() if text == correct_text)

    return {
        "options": shuffled_options,
        "correct_letter": new_correct_letter,
        "correct_text": shuffled_options[new_correct_letter],
    }


def build_attempt_from_quiz(quiz_df: pd.DataFrame) -> Dict[str, object]:
    seed = random.SystemRandom().randint(100000, 999999)
    question_order = list(range(len(quiz_df)))
    random.Random(seed).shuffle(question_order)

    question_data = []
    for position, original_index in enumerate(question_order):
        row = quiz_df.iloc[original_index]
        shuffle_seed = seed + original_index + (position * 997)
        shuffled = shuffle_options_for_row(row, shuffle_seed)
        question_data.append({
            "original_index": original_index,
            "question": clean_text(row["question"]),
            "options": shuffled["options"],
            "correct_letter": shuffled["correct_letter"],
            "correct_text": shuffled["correct_text"],
            "explanation": clean_text(row["explanation"]) if "explanation" in row.index else "",
        })

    return {
        "seed": seed,
        "current_q": 0,
        "score": 0,
        "answered_current": False,
        "current_feedback": None,
        "quiz_complete": False,
        "final_saved": False,
        "question_data": question_data,
    }


def get_selected_quiz_row(catalogue_df: pd.DataFrame, selected_quiz_title: Optional[str], selected_quiz_id: Optional[str]) -> Optional[pd.Series]:
    if selected_quiz_id:
        matches = catalogue_df[catalogue_df["quiz_id"].astype(str) == str(selected_quiz_id)]
        if not matches.empty:
            return matches.iloc[0]

    if selected_quiz_title:
        matches = catalogue_df[catalogue_df["quiz_title"].astype(str) == str(selected_quiz_title)]
        if not matches.empty:
            return matches.iloc[0]

    return None


def build_topic_groups(catalogue_df: pd.DataFrame) -> List[Tuple[str, pd.DataFrame]]:
    groups: List[Tuple[str, pd.DataFrame]] = []
    used_topics = set()

    for topic in TOPIC_ORDER:
        topic_df = catalogue_df[catalogue_df["topic"].astype(str).str.casefold() == topic.casefold()].copy()
        if not topic_df.empty:
            groups.append((topic, topic_df))
            used_topics.add(topic.casefold())

    remainder = catalogue_df[~catalogue_df["topic"].astype(str).str.casefold().isin(used_topics)].copy()
    if not remainder.empty:
        for actual_topic, group_df in remainder.groupby(remainder["topic"].replace("", UNCATEGORIZED_TOPIC)):
            groups.append((actual_topic or UNCATEGORIZED_TOPIC, group_df.copy()))

    return groups


def get_user_topic_progress(results_df: pd.DataFrame, catalogue_df: pd.DataFrame, email: str) -> Dict[str, Tuple[int, int]]:
    topic_groups = build_topic_groups(catalogue_df)
    progress: Dict[str, Tuple[int, int]] = {}

    if results_df.empty:
        for topic_name, topic_df in topic_groups:
            progress[topic_name] = (0, len(topic_df))
        return progress

    user_results = results_df[results_df["Email"].astype(str).str.lower() == email.lower()].copy()
    completed_quizzes = set(user_results["Quiz Title"].astype(str).tolist())

    for topic_name, topic_df in topic_groups:
        titles = topic_df["quiz_title"].astype(str).tolist()
        completed = len([title for title in titles if title in completed_quizzes])
        progress[topic_name] = (completed, len(titles))

    return progress


# -----------------------------------
# RENDER HELPERS
# -----------------------------------
def render_header(name: str, email: str) -> None:
    st.markdown(
        """
        <div class="pow-hero">
            <h1>Pow WOW Learning</h1>
            <p>Interactive video learning with instant feedback</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([5, 1])
    with left:
        st.markdown(
            f"<div class='pow-meta'>Signed in as <strong>{name}</strong> ({email})</div>",
            unsafe_allow_html=True,
        )
    with right:
        if st.button("Logout", use_container_width=True):
            st.logout()

    st.markdown("<div class='pow-divider'></div>", unsafe_allow_html=True)


def render_sidebar(is_teacher_mode: bool) -> None:
    with st.sidebar:
        st.markdown("### Pow WOW Learning")
        st.caption("Teacher tools and utilities")

        if st.button("Reset current quiz", use_container_width=True):
            reset_attempt_state()
            st.rerun()

        if st.button("Return to quiz library", use_container_width=True):
            go_to_library()
            st.rerun()

        if st.button("Clear data cache", use_container_width=True):
            st.cache_data.clear()
            load_results_from_sheets_cached.clear()
            st.rerun()

        if is_teacher_mode:
            st.markdown("---")
            st.caption(f"Page: {st.session_state.get('page')}")
            if st.session_state.get("selected_quiz_title"):
                st.caption(f"Quiz: {st.session_state.get('selected_quiz_title')}")


def render_library(catalogue_df: pd.DataFrame, topic_progress: Dict[str, Tuple[int, int]]) -> None:
    st.markdown("<div class='pow-section-title'>Browse by Topic</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='pow-topic-note'>Choose a topic, then launch a quiz. Progress is based on quizzes you’ve already completed.</div>",
        unsafe_allow_html=True,
    )

    topic_groups = build_topic_groups(catalogue_df)
    if not topic_groups:
        st.info("No visible quizzes are currently available.")
        return

    for topic_name, topic_df in topic_groups:
        completed, total = topic_progress.get(topic_name, (0, len(topic_df)))
        expander_label = f"{topic_name}   ·   {completed}/{total} completed"

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
                            <div class="pow-quiz-topic">{row['topic'] or UNCATEGORIZED_TOPIC}</div>
                            <div class="pow-chip">Video quiz</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("Start quiz", key=f"start_{row['quiz_id']}", use_container_width=True):
                        open_quiz(row)
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)


def render_quiz_header(selected_quiz_title: str, selected_topic: str) -> None:
    back_col, title_col = st.columns([1, 5])
    with back_col:
        if st.button("← Library", use_container_width=True):
            go_to_library()
            st.rerun()

    with title_col:
        st.markdown(f"<div class='pow-section-title'>{selected_quiz_title}</div>", unsafe_allow_html=True)
        if selected_topic:
            st.markdown(f"<div class='pow-small-muted'>{selected_topic}</div>", unsafe_allow_html=True)

    st.markdown("<div class='pow-divider'></div>", unsafe_allow_html=True)


def ensure_attempt_loaded(quiz_df: pd.DataFrame) -> None:
    attempt = st.session_state.get("attempt", {})
    if not attempt or len(attempt.get("question_data", [])) != len(quiz_df):
        st.session_state.attempt = build_attempt_from_quiz(quiz_df)


def render_quiz_video(youtube_url: str) -> None:
    st.markdown("<div class='pow-video-title'>Watch the video</div>", unsafe_allow_html=True)
    if youtube_url:
        st.video(youtube_url)
    else:
        st.info("No video link has been added for this quiz.")
    st.markdown("<div class='pow-divider'></div>", unsafe_allow_html=True)


def render_quiz_engine(
    quiz_title: str,
    quiz_df: pd.DataFrame,
    name: str,
    email: str,
    role: str,
) -> None:
    ensure_attempt_loaded(quiz_df)
    attempt = st.session_state.attempt
    question_data = attempt["question_data"]
    total_questions = len(question_data)

    if total_questions == 0:
        st.warning("This quiz has no questions.")
        return

    current_position = attempt["current_q"]
    if current_position >= total_questions:
        attempt["quiz_complete"] = True
        st.session_state.attempt = attempt

    if not attempt["quiz_complete"]:
        progress_value = current_position / total_questions if total_questions else 0
        st.progress(progress_value)
        st.markdown(
            f"<div class='pow-question-meta'>Question {current_position + 1} of {total_questions}</div>",
            unsafe_allow_html=True,
        )

        current = question_data[current_position]
        options = current["options"]

        st.markdown(
            f"<div class='pow-quiz-shell'><div class='pow-question'>{current['question']}</div></div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div class='pow-answer-area'></div>", unsafe_allow_html=True)
        cols = st.columns(2)
        clicked = None

        for idx, (letter, text) in enumerate(options.items()):
            with cols[idx % 2]:
                if st.button(f"{letter}. {text}", key=f"answer_{current_position}_{letter}", use_container_width=True):
                    clicked = letter

        if clicked and not attempt["answered_current"]:
            is_correct = clicked == current["correct_letter"]
            attempt["answered_current"] = True
            attempt["current_feedback"] = {
                "selected": clicked,
                "correct": current["correct_letter"],
                "is_correct": is_correct,
                "correct_text": current["correct_text"],
                "question_text": current["question"],
                "explanation": current["explanation"],
            }

            if is_correct:
                attempt["score"] += 1

            save_question_analytics(
                quiz_title,
                email,
                role,
                current_position + 1,
                current["question"],
                clicked,
                current["correct_letter"],
                is_correct,
            )
            st.session_state.attempt = attempt
            st.rerun()

        if attempt["answered_current"] and attempt["current_feedback"]:
            feedback = attempt["current_feedback"]
            if feedback["is_correct"]:
                st.markdown("<div class='pow-feedback-ok'>Correct</div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    f"<div class='pow-feedback-bad'>Correct answer: {feedback['correct']}. {feedback['correct_text']}</div>",
                    unsafe_allow_html=True,
                )

            if feedback.get("explanation"):
                st.info(feedback["explanation"])

            st.markdown("<br>", unsafe_allow_html=True)

            if current_position < total_questions - 1:
                if st.button("Next question", use_container_width=True):
                    attempt["current_q"] += 1
                    attempt["answered_current"] = False
                    attempt["current_feedback"] = None
                    st.session_state.attempt = attempt
                    st.rerun()
            else:
                attempt["quiz_complete"] = True
                st.session_state.attempt = attempt
                st.rerun()

    if st.session_state.attempt["quiz_complete"]:
        render_final_score(quiz_title, name, email, role)


def render_final_score(quiz_title: str, name: str, email: str, role: str) -> None:
    attempt = st.session_state.attempt
    total_questions = len(attempt.get("question_data", []))
    score = attempt.get("score", 0)
    percent = round((score / total_questions) * 100, 1) if total_questions else 0

    if not attempt.get("final_saved", False):
        save_result(name, email, role, quiz_title, score, total_questions)
        attempt["final_saved"] = True
        st.session_state.attempt = attempt

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
            reset_attempt_state()
            st.rerun()

    with c2:
        if st.button("Back to library", use_container_width=True):
            go_to_library()
            st.rerun()


def render_teacher_dashboard(selected_quiz_title: str) -> None:
    try:
        results_df, analytics_df = load_results_from_sheets()
    except Exception as e:
        st.error(f"Could not load teacher dashboard data: {e}")
        return

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
                filtered_analytics["Is Correct"].astype(str).str.lower().isin(["true", "1", "yes"])
            )
            filtered_analytics["Question Number"] = pd.to_numeric(
                filtered_analytics["Question Number"], errors="coerce"
            )

            stats = (
                filtered_analytics.groupby(["Question Number", "Question"], as_index=False)
                .agg(Attempts=("Is Correct", "count"), Correct=("Is Correct", "sum"))
            )
            stats["Correct %"] = (stats["Correct"] / stats["Attempts"] * 100).round(1)
            stats = stats.sort_values("Question Number")
            st.dataframe(stats, use_container_width=True)


# -----------------------------------
# AUTH
# -----------------------------------
init_app_state()

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
# APP CHROME
# -----------------------------------
render_header(name, email)

role = st.radio("Role", ["Student", "Teacher"], horizontal=True)
is_teacher_mode = role == "Teacher"
if is_teacher_mode and email not in ADMIN_EMAILS:
    st.warning("Teacher mode is restricted.")
    st.stop()

render_sidebar(is_teacher_mode)

# -----------------------------------
# LOAD CATALOGUE
# -----------------------------------
try:
    catalogue_df = load_google_sheet(QUIZ_CATALOGUE_URL)
    catalogue_df = normalise_catalogue(catalogue_df)
except Exception as e:
    st.error(f"Could not load quiz catalogue: {e}")
    st.stop()

# -----------------------------------
# LOAD PROGRESS WHEN USEFUL
# -----------------------------------
results_df = pd.DataFrame(columns=RESULTS_HEADERS)
analytics_df = pd.DataFrame(columns=ANALYTICS_HEADERS)
topic_progress: Dict[str, Tuple[int, int]] = {}

if st.session_state.page == "library" or is_teacher_mode:
    try:
        results_df, analytics_df = load_results_from_sheets()
        topic_progress = get_user_topic_progress(results_df, catalogue_df, email)
    except Exception as e:
        st.error(f"Could not load results sheets: {e}")
        st.stop()

# -----------------------------------
# LIBRARY PAGE
# -----------------------------------
if st.session_state.page == "library":
    render_library(catalogue_df, topic_progress)
    st.stop()

# -----------------------------------
# QUIZ PAGE SAFETY CHECKS
# -----------------------------------
if st.session_state.page == "quiz" and not st.session_state.selected_quiz_title and not st.session_state.selected_quiz_id:
    go_to_library()
    st.rerun()

selected_row = get_selected_quiz_row(
    catalogue_df,
    st.session_state.get("selected_quiz_title"),
    st.session_state.get("selected_quiz_id"),
)

if selected_row is None:
    st.warning("That quiz could not be found, so the app returned to the library.")
    go_to_library()
    st.rerun()

selected_quiz_title = clean_text(selected_row["quiz_title"])
selected_quiz_id = clean_text(selected_row["quiz_id"])
youtube_url = clean_text(selected_row["youtube_url"])
question_sheet_url = clean_text(selected_row["question_sheet_url"])
selected_topic = clean_text(selected_row.get("topic", ""))

try:
    quiz_df = load_google_sheet(question_sheet_url)
    quiz_df = validate_quiz_df(quiz_df)
except Exception as e:
    st.error(f"Could not load quiz questions: {e}")
    st.stop()

st.session_state.selected_quiz_title = selected_quiz_title
st.session_state.selected_quiz_id = selected_quiz_id

# -----------------------------------
# RENDER QUIZ PAGE
# -----------------------------------
render_quiz_header(selected_quiz_title, selected_topic)
render_quiz_video(youtube_url)
render_quiz_engine(selected_quiz_title, quiz_df, name, email, role)

if is_teacher_mode:
    render_teacher_dashboard(selected_quiz_title)
