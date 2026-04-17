import re
import random
from datetime import datetime

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="IG Econ Video Quizzes", layout="wide")

# -----------------------------------
# STYLE (KAHOOT FEEL)
# -----------------------------------
st.markdown("""
<style>
.block-container {
    max-width: 800px;
    margin: auto;
}

button {
    font-size: 18px !important;
    padding: 15px !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# CONFIG
# -----------------------------------
ADMIN_EMAILS = {"james.p@sisbschool.com"}

QUIZ_CATALOGUE_URL = "https://docs.google.com/spreadsheets/d/1M6QJOgDr5BYtsxpxLA-u1_RYRCugzlINQOUrVsTin-o/edit?usp=sharing"

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
    return (
        spreadsheet.worksheet("Results"),
        spreadsheet.worksheet("QuestionAnalytics"),
    )

def save_result(name, email, role, quiz_title, score, total):
    ws, _ = get_results_workbooks()
    percent = round((score / total) * 100, 1)
    ws.append_row([name, email, role, quiz_title, score, total, percent, datetime.now()])

def save_question_analytics(quiz_title, email, role, q_num, question, selected, correct, is_correct):
    _, ws = get_results_workbooks()
    ws.append_row([quiz_title, email, role, q_num, question, selected, correct, is_correct, datetime.now()])

# -----------------------------------
# HELPERS
# -----------------------------------
def convert_sheet_url(url):
    if "export" in url:
        return url
    sheet_id = url.split("/d/")[1].split("/")[0]
    gid = url.split("gid=")[1].split("&")[0] if "gid=" in url else "0"
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

@st.cache_data
def load_google_sheet(url):
    return pd.read_csv(convert_sheet_url(url))

def shuffle_question(row, seed):
    rng = random.Random(seed)
    options = {
        "A": row["option_a"],
        "B": row["option_b"],
        "C": row["option_c"],
        "D": row["option_d"],
    }
    correct = row["correct_answer"].strip().upper()
    correct_text = options[correct]

    values = list(options.values())
    rng.shuffle(values)
    shuffled = dict(zip(["A","B","C","D"], values))
    new_correct = next(k for k,v in shuffled.items() if v == correct_text)

    return shuffled, new_correct

def parse_visible(v):
    return str(v).lower() in ["true","1","yes"]

# -----------------------------------
# AUTH
# -----------------------------------
if not st.user.is_logged_in:
    st.title("🎓 IG Econ Video Quizzes")
    st.button("Login", on_click=st.login)
    st.stop()

name = getattr(st.user, "name", "Student")
email = getattr(st.user, "email", "")

# -----------------------------------
# ROLE
# -----------------------------------
role = st.radio("Select role", ["Student", "Teacher"], horizontal=True)
if role == "Teacher" and email not in ADMIN_EMAILS:
    st.stop()

# -----------------------------------
# LOAD QUIZ LIST
# -----------------------------------
catalogue = load_google_sheet(QUIZ_CATALOGUE_URL)
catalogue = catalogue[catalogue["visible"].apply(parse_visible)]

quiz_title = st.selectbox("Choose a quiz", catalogue["quiz_title"])

row = catalogue[catalogue["quiz_title"] == quiz_title].iloc[0]
youtube_url = row["youtube_url"]
question_url = row["question_sheet_url"]

quiz_df = load_google_sheet(question_url)

# -----------------------------------
# VIDEO
# -----------------------------------
st.markdown("<h3 style='text-align:center;'>🎬 Watch the video</h3>", unsafe_allow_html=True)
st.video(youtube_url)

# -----------------------------------
# KAHOOT QUIZ
# -----------------------------------
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.answered = False

i = st.session_state.q_index
total = len(quiz_df)

st.progress(i / total)

row = quiz_df.iloc[i]
options, correct = shuffle_question(row, i)

st.markdown(f"""
<div style='text-align:center; font-size:26px; font-weight:700;'>
Question {i+1} of {total}
</div>

<div style='text-align:center; font-size:22px; margin-bottom:30px;'>
{row['question']}
</div>
""", unsafe_allow_html=True)

cols = st.columns(2)
clicked = None

for idx, (k,v) in enumerate(options.items()):
    with cols[idx % 2]:
        if st.button(f"{k}. {v}", key=f"{i}_{k}", use_container_width=True):
            clicked = k

if clicked and not st.session_state.answered:
    st.session_state.answered = True

    correct_bool = clicked == correct
    if correct_bool:
        st.session_state.score += 1
        st.success("✅ Correct!")
    else:
        st.error(f"❌ Correct answer: {correct}")

    save_question_analytics(
        quiz_title, email, role, i+1, row["question"], clicked, correct, correct_bool
    )

if st.session_state.answered:
    if i < total - 1:
        if st.button("Next ➡", use_container_width=True):
            st.session_state.q_index += 1
            st.session_state.answered = False
            st.rerun()
    else:
        score = st.session_state.score
        percent = round(score/total*100,1)

        save_result(name, email, role, quiz_title, score, total)

        st.markdown(f"""
        <div style='text-align:center; font-size:40px; font-weight:800; color:green;'>
        🎉 {score}/{total} ({percent}%)
        </div>
        """, unsafe_allow_html=True)

        if st.button("Play Again"):
            st.session_state.q_index = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.rerun()
