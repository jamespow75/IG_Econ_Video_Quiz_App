import random
from datetime import datetime

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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Fraunces:wght@700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    max-width: 860px;
    padding-top: 1.5rem;
}

/* ── Header ── */
.pow-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding-bottom: 1.2rem;
    margin-bottom: 1.4rem;
    border-bottom: 1px solid #E8ECF2;
}
.pow-logo {
    width: 44px;
    height: 44px;
    background: #1A2B4C;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Fraunces', serif;
    font-size: 20px;
    color: #F4B400;
    font-weight: 700;
    flex-shrink: 0;
}
.pow-header-text h1 {
    font-family: 'Fraunces', serif;
    font-size: 1.35rem;
    font-weight: 700;
    margin: 0 0 2px;
    color: #1A2B4C;
}
.pow-header-text p {
    font-size: 0.78rem;
    color: #6B7A99;
    margin: 0;
}

/* ── Section labels ── */
.pow-section-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: #9AA3B5;
    margin: 0 0 0.6rem;
}

/* ── Quiz cards ── */
.quiz-card {
    border: 1px solid #E2E7F0;
    border-radius: 10px;
    padding: 13px 16px;
    margin-bottom: 8px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 14px;
    background: #fff;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.quiz-card:hover {
    border-color: #1A2B4C;
    box-shadow: 0 2px 8px rgba(26,43,76,0.08);
}
.quiz-card-num {
    width: 32px;
    height: 32px;
    background: #EEF1F8;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 600;
    color: #1A2B4C;
    flex-shrink: 0;
}
.quiz-card-title {
    flex: 1;
    font-size: 0.88rem;
    font-weight: 500;
    color: #1C2A44;
}

/* ── Progress bar ── */
.pow-progress-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1.2rem;
}
.pow-progress-track {
    flex: 1;
    height: 5px;
    background: #E8ECF2;
    border-radius: 3px;
    overflow: hidden;
}
.pow-progress-fill {
    height: 100%;
    background: #1A2B4C;
    border-radius: 3px;
    transition: width 0.3s;
}
.pow-progress-label {
    font-size: 0.78rem;
    color: #6B7A99;
    white-space: nowrap;
}

/* ── Question text ── */
.pow-question {
    font-family: 'Fraunces', serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: #1A2B4C;
    line-height: 1.5;
    margin-bottom: 1.2rem;
}

/* ── Answer buttons ── */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    border-radius: 8px !important;
    border: 1px solid #DDE2EE !important;
    background: #fff !important;
    color: #1C2A44 !important;
    padding: 10px 14px !important;
    text-align: left !important;
    transition: border-color 0.15s !important;
}
.stButton > button:hover {
    border-color: #1A2B4C !important;
    background: #F5F7FB !important;
}

/* ── Score display ── */
.pow-score-ring-wrap {
    text-align: center;
    padding: 1.5rem 0 1rem;
}
.pow-score-big {
    font-family: 'Fraunces', serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: #1A2B4C;
}
.pow-score-sub {
    font-size: 0.85rem;
    color: #6B7A99;
    margin-top: 4px;
}
.pow-stat-row {
    display: flex;
    gap: 10px;
    margin: 1.2rem 0;
}
.pow-stat {
    flex: 1;
    background: #F5F7FB;
    border-radius: 10px;
    padding: 12px;
    text-align: center;
}
.pow-stat-val {
    font-size: 1.3rem;
    font-weight: 600;
    color: #1A2B4C;
}
.pow-stat-lbl {
    font-size: 0.72rem;
    color: #9AA3B5;
    margin-top: 3px;
}

/* ── Explanation box ── */
.pow-explanation {
    background: #F0F4FF;
    border-left: 3px solid #1A2B4C;
    border-radius: 0 8px 8px 0;
    padding: 11px 14px;
    font-size: 0.84rem;
    color: #374160;
    line-height: 1.6;
    margin: 0.8rem 0;
}

/* ── Feedback banners ── */
.pow-correct {
    background: #EAF5EC;
    border: 1px solid #B6DFB9;
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 0.85rem;
    color: #2D6E35;
    font-weight: 500;
    margin-bottom: 0.6rem;
}
.pow-wrong {
    background: #FEF0F0;
    border: 1px solid #F5BFBF;
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 0.85rem;
    color: #9B2626;
    font-weight: 500;
    margin-bottom: 0.6rem;
}

/* ── Info/divider ── */
.pow-divider {
    border: none;
    border-top: 1px solid #E8ECF2;
    margin: 1.2rem 0;
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
    "NR":  ["G9B","G9S","G9M","G9G","G10L","G10VG","G10P","G10M","G11A","G11S","G11V","G11P","G12G","G12M","G12P","G12U"],
    "PU":  ["G9B","G9S","G9M","G9G","G10L","G10VG","G10P","G10M","G11A","G11S","G11V","G11P","G12G","G12M","G12P","G12U"],
    "TR":  ["G9B","G9S","G9M","G9G","G10L","G10VG","G10P","G10M","G11A","G11S","G11V","G11P","G12G","G12M","G12P","G12U"],
    "CM":  ["G9B","G9S","G9M","G9G","G10L","G10VG","G10P","G10M","G11A","G11S","G11V","G11P","G12G","G12M","G12P","G12U"],
}

RESULTS_SHEETS = {
    "IGCSE Economics":  {"NR":"IGCSE_Results_NR","PU":"IGCSE_Results_PU","TR":"IGCSE_Results_TR","CM":"IGCSE_Results_CM"},
    "A Level Economics":{"NR":"ALevel_Results_NR","PU":"ALevel_Results_PU","TR":"ALevel_Results_TR","CM":"ALevel_Results_CM"},
}

RESULTS_HEADERS = [
    "Timestamp", "Nickname", "Full Name", "Email", "Campus", "Class",
    "Year Group", "Course", "Quiz ID", "Topic", "Quiz Title",
    "Score", "Total", "Percentage",
]

QUIZ_REQUIRED_COLUMNS = ["question","option_a","option_b","option_c","option_d","correct_answer"]

# -----------------------------------
# SESSION STATE
# -----------------------------------
defaults = {
    "quiz_started": False,
    "current_q": 0,
    "score": 0,
    "quiz_df": None,
    "quiz_title": None,
    "quiz_youtube_url": None,
    "quiz_id": None,
    "quiz_topic": None,
    "shuffled_options": {},
    "saved_result": False,
    "answered": False,
    "clicked_letter": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

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
        st.secrets["gcp_service_account"], scopes=scopes
    )
    return gspread.authorize(creds)


@st.cache_resource
def get_results_spreadsheet():
    client = get_gspread_client()
    return client.open_by_url(st.secrets["results_sheet"]["spreadsheet_url"])


def ensure_headers(ws):
    if not ws.get_all_values():
        ws.append_row(RESULTS_HEADERS)


def save_result(nickname, full_name, email, course, campus, student_class,
                year_group, quiz_id, topic, quiz_title, score, total):
    spreadsheet = get_results_spreadsheet()
    sheet_name = RESULTS_SHEETS[course][campus]
    ws = spreadsheet.worksheet(sheet_name)
    ensure_headers(ws)
    percent = round((score / total) * 100, 1)
    ws.append_row([
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        nickname,
        full_name,
        email,
        campus,
        student_class,
        year_group,
        course,
        quiz_id,
        topic,
        quiz_title,
        score,
        total,
        percent,
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
    # Preserve gid if present (e.g. ?gid=711367124 or #gid=711367124)
    gid = None
    for sep in ["gid=", "#gid="]:
        if sep in url:
            gid = url.split(sep)[1].split("&")[0].split("#")[0]
            break
    base = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    return f"{base}&gid={gid}" if gid else base


@st.cache_data(ttl=300)
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
    options = {"A": row["option_a"], "B": row["option_b"], "C": row["option_c"], "D": row["option_d"]}
    correct_text = options[row["correct_answer"].upper()]
    values = list(options.values())
    rng.shuffle(values)
    shuffled = dict(zip(["A", "B", "C", "D"], values))
    new_correct = next(letter for letter, text in shuffled.items() if text == correct_text)
    return shuffled, new_correct


def reset_quiz():
    st.session_state.quiz_started = False
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.quiz_df = None
    st.session_state.quiz_title = None
    st.session_state.quiz_youtube_url = None
    st.session_state.quiz_id = None
    st.session_state.quiz_topic = None
    st.session_state.shuffled_options = {}
    st.session_state.saved_result = False
    st.session_state.answered = False
    st.session_state.clicked_letter = None


# -----------------------------------
# HEADER
# -----------------------------------
st.markdown(
    """
    <div class="pow-header">
        <div class="pow-logo">P</div>
        <div class="pow-header-text">
            <h1>Pow WOW Learning</h1>
            <p>Interactive Economics Video Quizzes</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------
# STUDENT DETAILS
# -----------------------------------
col1, col2 = st.columns(2)
with col1:
    nickname = st.text_input("Nickname (e.g. Moohin, Sand)")
with col2:
    full_name = st.text_input("Full name")

col_email, _ = st.columns([2, 1])
with col_email:
    email = st.text_input("School email address")

col3, col4, col5 = st.columns(3)
with col3:
    course = st.selectbox("Course", COURSES)
with col4:
    campus = st.selectbox("Campus", CAMPUSES)
with col5:
    student_class = st.selectbox("Class", CAMPUS_CLASSES[campus])

# Derive year group from class and course
def get_year_group(cls, crs):
    grade_num = ''.join(filter(str.isdigit, cls[:4]))
    if "IGCSE" in crs:
        return "IGCSE Year 1" if grade_num in ("9", "11") else "IGCSE Year 2"
    elif "A Level" in crs:
        return "A Level Year 1" if grade_num in ("11",) else "A Level Year 2"
    return f"Grade {grade_num}"

year_group = get_year_group(student_class, course)

if not nickname or not full_name or not email:
    st.info("Please enter your nickname, full name, and school email to get started.")
    st.stop()

st.markdown('<hr class="pow-divider">', unsafe_allow_html=True)

# -----------------------------------
# LOAD CATALOGUE
# -----------------------------------
try:
    catalogue_df = load_google_sheet(QUIZ_CATALOGUE_URL)
except Exception as e:
    st.error(f"Could not load quiz catalogue: {e}")
    st.stop()

# Filter to visible quizzes only
if "visible" in catalogue_df.columns:
    catalogue_df = catalogue_df[catalogue_df["visible"].astype(str).str.upper() == "TRUE"]

catalogue_df = catalogue_df.reset_index(drop=True)

# -----------------------------------
# QUIZ LIBRARY  (unit tabs)
# -----------------------------------
if not st.session_state.quiz_started:

    # Get ordered unique units
    units = catalogue_df["topic"].dropna().unique().tolist()

    st.markdown('<p class="pow-section-label">Select a quiz</p>', unsafe_allow_html=True)

    tabs = st.tabs(units)

    for tab, unit in zip(tabs, units):
        with tab:
            unit_df = catalogue_df[catalogue_df["topic"] == unit].reset_index(drop=True)

            for _, row in unit_df.iterrows():
                quiz_id   = row["quiz_id"]
                title     = row["quiz_title"]
                yt_url    = row["youtube_url"]
                sheet_url = row["question_sheet_url"]

                # Render card as a button with custom HTML label
                card_label = f"**{quiz_id}** — {title}"
                if st.button(card_label, key=f"quiz__{quiz_id}", use_container_width=True):
                    try:
                        quiz_df = load_google_sheet(sheet_url)
                        quiz_df = validate_quiz_df(quiz_df)
                    except Exception as e:
                        st.error(f"Could not load quiz: {e}")
                        st.stop()

                    st.session_state.quiz_df          = quiz_df
                    st.session_state.quiz_title        = title
                    st.session_state.quiz_youtube_url  = yt_url
                    st.session_state.quiz_id           = quiz_id
                    st.session_state.quiz_topic        = unit
                    st.session_state.quiz_started      = True
                    st.session_state.current_q         = 0
                    st.session_state.score             = 0
                    st.session_state.shuffled_options  = {}
                    st.session_state.saved_result      = False
                    st.session_state.answered          = False
                    st.session_state.clicked_letter    = None
                    st.rerun()

    st.stop()

# =====================================================
# QUIZ IN PROGRESS
# =====================================================
quiz_df     = st.session_state.quiz_df
current_q   = st.session_state.current_q
score       = st.session_state.score
youtube_url = st.session_state.quiz_youtube_url

# -----------------------------------
# RESULTS SCREEN
# -----------------------------------
if current_q >= len(quiz_df):

    if not st.session_state.saved_result:
        save_result(
            nickname,
            full_name,
            email,
            course,
            campus,
            student_class,
            year_group,
            st.session_state.quiz_id,
            st.session_state.quiz_topic,
            st.session_state.quiz_title,
            score,
            len(quiz_df),
        )
        st.session_state.saved_result = True

    percent = round((score / len(quiz_df)) * 100, 1)

    if percent >= 80:
        verdict = "Excellent work"
        colour  = "#2D6E35"
    elif percent >= 60:
        verdict = "Good effort"
        colour  = "#1A2B4C"
    else:
        verdict = "Keep practising"
        colour  = "#7A4A10"

    st.markdown(
        f"""
        <div class="pow-score-ring-wrap">
            <div class="pow-score-big" style="color:{colour};">{percent}%</div>
            <div class="pow-score-sub">{verdict} · {score}/{len(quiz_df)} correct</div>
            <div style="font-size:0.82rem; color:#9AA3B5; margin-top:6px;">
                {st.session_state.quiz_title}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="pow-stat-row">
            <div class="pow-stat"><div class="pow-stat-val">{score}</div><div class="pow-stat-lbl">Correct</div></div>
            <div class="pow-stat"><div class="pow-stat-val">{len(quiz_df) - score}</div><div class="pow-stat-lbl">Incorrect</div></div>
            <div class="pow-stat"><div class="pow-stat-val">{percent}%</div><div class="pow-stat-lbl">Score</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("← Back to library", use_container_width=True):
            reset_quiz()
            st.rerun()
    with col_b:
        if st.button("Retry this quiz ↺", use_container_width=True):
            st.session_state.current_q        = 0
            st.session_state.score            = 0
            st.session_state.shuffled_options = {}
            st.session_state.saved_result     = False
            st.session_state.answered         = False
            st.session_state.clicked_letter   = None
            st.rerun()

    st.stop()

# -----------------------------------
# VIDEO  (always visible above question)
# -----------------------------------
st.video(youtube_url)

st.markdown('<hr class="pow-divider">', unsafe_allow_html=True)

# -----------------------------------
# PROGRESS BAR
# -----------------------------------
pct = int((current_q / len(quiz_df)) * 100)
st.markdown(
    f"""
    <div class="pow-progress-wrap">
        <div class="pow-progress-track">
            <div class="pow-progress-fill" style="width:{pct}%"></div>
        </div>
        <span class="pow-progress-label">Question {current_q + 1} of {len(quiz_df)}</span>
        <span class="pow-progress-label" style="margin-left:6px;">· Score: <strong>{score}</strong></span>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------
# CURRENT QUESTION
# -----------------------------------
row = quiz_df.iloc[current_q]
question_key = f"q_{current_q}"

st.markdown(
    f'<div class="pow-question">{row["question"]}</div>',
    unsafe_allow_html=True,
)

# Shuffle answers once per question
if question_key not in st.session_state.shuffled_options:
    shuffled, correct_letter = shuffle_answers(row, current_q + 1000)
    st.session_state.shuffled_options[question_key] = {
        "options": shuffled,
        "correct": correct_letter,
    }

question_data  = st.session_state.shuffled_options[question_key]
options        = question_data["options"]
correct_letter = question_data["correct"]
answered       = st.session_state.answered
clicked_letter = st.session_state.clicked_letter

# -----------------------------------
# ANSWER BUTTONS
# IMPORTANT: questions stay in original order; only answers are shuffled
# -----------------------------------
col_left, col_right = st.columns(2)
cols = [col_left, col_right, col_left, col_right]

for idx, (letter, text) in enumerate(options.items()):
    with cols[idx]:
        # Disable all buttons once the student has answered
        btn_disabled = answered
        if st.button(
            f"{letter}.  {text}",
            key=f"btn_{current_q}_{letter}",
            use_container_width=True,
            disabled=btn_disabled,
        ):
            st.session_state.answered       = True
            st.session_state.clicked_letter = letter
            if letter == correct_letter:
                st.session_state.score += 1
            st.rerun()

# -----------------------------------
# FEEDBACK  (shown after answering)
# -----------------------------------
if answered:
    if clicked_letter == correct_letter:
        st.markdown('<div class="pow-correct">✓ Correct!</div>', unsafe_allow_html=True)
    else:
        correct_text = options[correct_letter]
        st.markdown(
            f'<div class="pow-wrong">✗ Not quite — the correct answer was <strong>{correct_letter}. {correct_text}</strong></div>',
            unsafe_allow_html=True,
        )

    # Optional explanation column
    if "explanation" in row and pd.notna(row["explanation"]) and str(row["explanation"]).strip():
        st.markdown(
            f'<div class="pow-explanation">{row["explanation"]}</div>',
            unsafe_allow_html=True,
        )

    if st.button("Next question →", use_container_width=True):
        st.session_state.current_q      += 1
        st.session_state.answered        = False
        st.session_state.clicked_letter  = None
        st.rerun()
