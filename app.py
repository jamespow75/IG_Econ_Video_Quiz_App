import os
import json
import uuid
from datetime import datetime
from io import BytesIO

import pandas as pd
import streamlit as st

# Optional Google Sheets support
# To enable this on Streamlit Community Cloud:
# 1. Add gspread and google-auth to requirements.txt
# 2. Put your service account JSON in st.secrets as GOOGLE_SERVICE_ACCOUNT
# 3. Put sheet names / IDs in st.secrets if needed
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except Exception:
    GSHEETS_AVAILABLE = False


# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Video Quiz Generator", page_icon="🎥", layout="wide")

LOCAL_QUIZ_FILE = "quizzes.csv"
LOCAL_SUBMISSION_FILE = "submissions.csv"
LOCAL_ANSWER_FILE = "answers.csv"

QUIZ_COLUMNS = [
    "quiz_id",
    "quiz_title",
    "youtube_url",
    "question_no",
    "question",
    "option_a",
    "option_b",
    "option_c",
    "option_d",
    "correct_answer",
    "created_at",
]

SUBMISSION_COLUMNS = [
    "submission_id",
    "quiz_id",
    "quiz_title",
    "student_name",
    "student_class",
    "score",
    "total_questions",
    "submitted_at",
]

ANSWER_COLUMNS = [
    "submission_id",
    "quiz_id",
    "question_no",
    "student_answer",
    "correct_answer",
    "is_correct",
]


# -----------------------------
# HELPERS
# -----------------------------
def ensure_local_files():
    for filename, cols in [
        (LOCAL_QUIZ_FILE, QUIZ_COLUMNS),
        (LOCAL_SUBMISSION_FILE, SUBMISSION_COLUMNS),
        (LOCAL_ANSWER_FILE, ANSWER_COLUMNS),
    ]:
        if not os.path.exists(filename):
            pd.DataFrame(columns=cols).to_csv(filename, index=False)


def load_csv(filename: str, columns: list[str]) -> pd.DataFrame:
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        return df[columns]
    return pd.DataFrame(columns=columns)


def save_csv(df: pd.DataFrame, filename: str):
    df.to_csv(filename, index=False)


def normalize_correct_answer(value: str) -> str:
    if pd.isna(value):
        return ""
    value = str(value).strip().upper()
    return value if value in {"A", "B", "C", "D"} else ""


def validate_question_df(df: pd.DataFrame) -> tuple[bool, str, pd.DataFrame]:
    required = [
        "question",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_answer",
    ]

    missing = [col for col in required if col not in df.columns]
    if missing:
        return False, f"Missing columns: {', '.join(missing)}", df

    cleaned = df.copy()
    cleaned = cleaned[required].fillna("")
    cleaned["correct_answer"] = cleaned["correct_answer"].apply(normalize_correct_answer)

    if cleaned.empty:
        return False, "The uploaded file has no questions.", cleaned

    if len(cleaned) < 10 or len(cleaned) > 15:
        return False, "Please upload between 10 and 15 questions.", cleaned

    invalid_correct = cleaned[cleaned["correct_answer"] == ""]
    if not invalid_correct.empty:
        return False, "Each correct_answer must be A, B, C, or D.", cleaned

    blank_questions = cleaned[cleaned["question"].astype(str).str.strip() == ""]
    if not blank_questions.empty:
        return False, "Some questions are blank.", cleaned

    return True, "OK", cleaned


def extract_youtube_id(url: str) -> str | None:
    if not url:
        return None
    url = url.strip()
    patterns = [
        "watch?v=",
        "youtu.be/",
        "shorts/",
        "embed/",
    ]
    for pattern in patterns:
        if pattern in url:
            part = url.split(pattern, 1)[1]
            return part.split("&")[0].split("?")[0].split("/")[0]
    return None


def get_embed_url(url: str) -> str:
    vid = extract_youtube_id(url)
    if vid:
        return f"https://www.youtube.com/embed/{vid}"
    return url


def get_google_sheets_client():
    if not GSHEETS_AVAILABLE:
        return None
    if "GOOGLE_SERVICE_ACCOUNT" not in st.secrets:
        return None

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds_dict = dict(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)


def append_to_gsheet(worksheet_name: str, row_values: list):
    client = get_google_sheets_client()
    if client is None:
        return False, "Google Sheets is not configured. Saved locally only."

    sheet_id = st.secrets.get("GOOGLE_SHEET_ID", None)
    if not sheet_id:
        return False, "GOOGLE_SHEET_ID is missing from secrets. Saved locally only."

    try:
        sh = client.open_by_key(sheet_id)
        ws = sh.worksheet(worksheet_name)
        ws.append_row(row_values)
        return True, "Saved to Google Sheets."
    except Exception as e:
        return False, f"Google Sheets save failed: {e}"


def append_dataframe_rows_to_gsheet(worksheet_name: str, df: pd.DataFrame):
    client = get_google_sheets_client()
    if client is None:
        return False, "Google Sheets is not configured. Saved locally only."

    sheet_id = st.secrets.get("GOOGLE_SHEET_ID", None)
    if not sheet_id:
        return False, "GOOGLE_SHEET_ID is missing from secrets. Saved locally only."

    try:
        sh = client.open_by_key(sheet_id)
        ws = sh.worksheet(worksheet_name)
        for _, row in df.iterrows():
            ws.append_row(row.fillna("").tolist())
        return True, "Saved to Google Sheets."
    except Exception as e:
        return False, f"Google Sheets save failed: {e}"


def load_all_quizzes() -> pd.DataFrame:
    return load_csv(LOCAL_QUIZ_FILE, QUIZ_COLUMNS)


def load_all_submissions() -> pd.DataFrame:
    return load_csv(LOCAL_SUBMISSION_FILE, SUBMISSION_COLUMNS)


def load_all_answers() -> pd.DataFrame:
    return load_csv(LOCAL_ANSWER_FILE, ANSWER_COLUMNS)


def get_quiz_list() -> pd.DataFrame:
    quizzes = load_all_quizzes()
    if quizzes.empty:
        return pd.DataFrame(columns=["quiz_id", "quiz_title", "youtube_url", "created_at"])

    deduped = quizzes[["quiz_id", "quiz_title", "youtube_url", "created_at"]].drop_duplicates()
    deduped = deduped.sort_values(by="created_at", ascending=False)
    return deduped


def get_quiz_questions(quiz_id: str) -> pd.DataFrame:
    quizzes = load_all_quizzes()
    if quizzes.empty:
        return quizzes
    quiz_df = quizzes[quizzes["quiz_id"] == quiz_id].copy()
    if quiz_df.empty:
        return quiz_df
    quiz_df["question_no"] = pd.to_numeric(quiz_df["question_no"], errors="coerce")
    return quiz_df.sort_values("question_no")


def save_new_quiz(quiz_title: str, youtube_url: str, questions_df: pd.DataFrame) -> str:
    quiz_id = str(uuid.uuid4())[:8]
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    prepared = questions_df.copy().reset_index(drop=True)
    prepared["quiz_id"] = quiz_id
    prepared["quiz_title"] = quiz_title
    prepared["youtube_url"] = youtube_url
    prepared["question_no"] = list(range(1, len(prepared) + 1))
    prepared["created_at"] = created_at
    prepared = prepared[QUIZ_COLUMNS]

    all_quizzes = load_all_quizzes()
    all_quizzes = pd.concat([all_quizzes, prepared], ignore_index=True)
    save_csv(all_quizzes, LOCAL_QUIZ_FILE)

    append_dataframe_rows_to_gsheet("quizzes", prepared)
    return quiz_id


def save_submission(
    quiz_id: str,
    quiz_title: str,
    student_name: str,
    student_class: str,
    score: int,
    total_questions: int,
    answer_records: list[dict],
):
    submission_id = str(uuid.uuid4())[:12]
    submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sub_row = {
        "submission_id": submission_id,
        "quiz_id": quiz_id,
        "quiz_title": quiz_title,
        "student_name": student_name,
        "student_class": student_class,
        "score": score,
        "total_questions": total_questions,
        "submitted_at": submitted_at,
    }

    submissions = load_all_submissions()
    submissions = pd.concat([submissions, pd.DataFrame([sub_row])], ignore_index=True)
    save_csv(submissions, LOCAL_SUBMISSION_FILE)

    answers_df = pd.DataFrame(answer_records)
    answers_df.insert(0, "submission_id", submission_id)
    answers = load_all_answers()
    answers = pd.concat([answers, answers_df], ignore_index=True)
    save_csv(answers, LOCAL_ANSWER_FILE)

    append_to_gsheet("submissions", [
        submission_id,
        quiz_id,
        quiz_title,
        student_name,
        student_class,
        score,
        total_questions,
        submitted_at,
    ])

    for _, row in answers_df.iterrows():
        append_to_gsheet("answers", row.fillna("").tolist())

    return submission_id


def build_sample_csv() -> bytes:
    sample = pd.DataFrame([
        {
            "question": "What is the main idea of the video?",
            "option_a": "Answer A",
            "option_b": "Answer B",
            "option_c": "Answer C",
            "option_d": "Answer D",
            "correct_answer": "A",
        },
        {
            "question": "Which detail is mentioned in the video?",
            "option_a": "Detail 1",
            "option_b": "Detail 2",
            "option_c": "Detail 3",
            "option_d": "Detail 4",
            "correct_answer": "C",
        },
    ])
    buffer = BytesIO()
    sample.to_csv(buffer, index=False)
    return buffer.getvalue()


# -----------------------------
# UI
# -----------------------------
ensure_local_files()

st.title("🎥 Video Quiz Generator")
st.caption("Create reusable YouTube quizzes, collect scores, and publish with Streamlit.")

page = st.sidebar.radio(
    "Choose a page",
    ["Student Quiz", "Teacher: Create Quiz", "Teacher: Results", "Setup Guide"],
)


if page == "Teacher: Create Quiz":
    st.header("Create a New Quiz")
    st.write("Upload a CSV file with 10 to 15 multiple-choice questions and paste a YouTube link.")

    with st.expander("CSV format", expanded=True):
        st.code(
            "question,option_a,option_b,option_c,option_d,correct_answer\n"
            "What is the main idea?,A,B,C,D,B\n"
            "What colour is the car?,Red,Blue,Green,Black,A",
            language="csv",
        )
        st.download_button(
            "Download sample CSV",
            data=build_sample_csv(),
            file_name="sample_quiz_questions.csv",
            mime="text/csv",
        )

    quiz_title = st.text_input("Quiz title", placeholder="e.g. Climate Change Video Quiz")
    youtube_url = st.text_input("YouTube URL", placeholder="Paste a YouTube link here")
    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

    preview_df = None
    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith(".csv"):
                raw_df = pd.read_csv(uploaded_file)
            else:
                raw_df = pd.read_excel(uploaded_file)

            ok, msg, cleaned_df = validate_question_df(raw_df)
            if ok:
                preview_df = cleaned_df.copy()
                st.success("Question file looks good.")
                st.dataframe(preview_df, use_container_width=True)
            else:
                st.error(msg)
        except Exception as e:
            st.error(f"Could not read the file: {e}")

    if youtube_url:
        st.subheader("Video preview")
        st.video(youtube_url)

    if st.button("Save quiz", type="primary"):
        if not quiz_title.strip():
            st.error("Please add a quiz title.")
        elif not youtube_url.strip():
            st.error("Please add a YouTube URL.")
        elif preview_df is None:
            st.error("Please upload a valid question file first.")
        else:
            quiz_id = save_new_quiz(quiz_title.strip(), youtube_url.strip(), preview_df)
            st.success(f"Quiz saved successfully. Quiz ID: {quiz_id}")


elif page == "Student Quiz":
    st.header("Take a Quiz")

    quiz_list = get_quiz_list()
    if quiz_list.empty:
        st.info("No quizzes have been created yet.")
    else:
        quiz_options = {
            f"{row['quiz_title']} ({row['quiz_id']})": row["quiz_id"]
            for _, row in quiz_list.iterrows()
        }

        selected_label = st.selectbox("Choose a quiz", list(quiz_options.keys()))
        selected_quiz_id = quiz_options[selected_label]
        quiz_df = get_quiz_questions(selected_quiz_id)

        if quiz_df.empty:
            st.error("Quiz data could not be loaded.")
        else:
            quiz_title = quiz_df.iloc[0]["quiz_title"]
            youtube_url = quiz_df.iloc[0]["youtube_url"]

            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader(quiz_title)
                st.video(youtube_url)
            with col2:
                student_name = st.text_input("Your name")
                student_class = st.text_input("Class")
                st.metric("Questions", len(quiz_df))

            st.markdown("---")

            with st.form(key=f"quiz_form_{selected_quiz_id}"):
                student_answers = {}
                for _, row in quiz_df.iterrows():
                    q_no = int(row["question_no"])
                    st.write(f"**{q_no}. {row['question']}**")
                    import random

options = [
    ("A", row["option_a"]),
    ("B", row["option_b"]),
    ("C", row["option_c"]),
    ("D", row["option_d"]),
]

random.shuffle(options)

labels = [f"{k}. {v}" for k, v in options]

selected = st.radio(
    f"Question {q_no}",
    labels,
    index=None,
    key=f"q_{selected_quiz_id}_{q_no}",
    label_visibility="collapsed",
)

if selected:
    chosen_letter = selected[0]

    # find original answer
    for original_letter, text in options:
        if original_letter == chosen_letter:
            student_answers[q_no] = chosen_letter
                    labels = [f"{k}. {v}" for k, v in options_map.items()]
                    selected = st.radio(
                        f"Question {q_no}",
                        labels,
                        index=None,
                        key=f"q_{selected_quiz_id}_{q_no}",
                        label_visibility="collapsed",
                    )
                    if selected:
                        student_answers[q_no] = selected[0]
                    st.write("")

                submitted = st.form_submit_button("Submit quiz", type="primary")

            if submitted:
                if not student_name.strip():
                    st.error("Please enter your name.")
                elif len(student_answers) != len(quiz_df):
                    st.error("Please answer every question before submitting.")
                else:
                    score = 0
                    answer_records = []

                    for _, row in quiz_df.iterrows():
                        q_no = int(row["question_no"])
                        correct = str(row["correct_answer"]).strip().upper()
                        student_answer = student_answers.get(q_no, "")
                        is_correct = student_answer == correct
                        if is_correct:
                            score += 1
                        answer_records.append({
                            "quiz_id": selected_quiz_id,
                            "question_no": q_no,
                            "student_answer": student_answer,
                            "correct_answer": correct,
                            "is_correct": is_correct,
                        })

                    save_submission(
                        quiz_id=selected_quiz_id,
                        quiz_title=quiz_title,
                        student_name=student_name.strip(),
                        student_class=student_class.strip(),
                        score=score,
                        total_questions=len(quiz_df),
                        answer_records=answer_records,
                    )

                    st.success(f"Submitted. Your score is {score}/{len(quiz_df)}.")

                    with st.expander("Review answers"):
                        for _, row in quiz_df.iterrows():
                            q_no = int(row["question_no"])
                            correct = str(row["correct_answer"]).strip().upper()
                            student_answer = student_answers.get(q_no, "")
                            st.write(f"**Q{q_no}. {row['question']}**")
                            st.write(f"Your answer: {student_answer}")
                            st.write(f"Correct answer: {correct}")
                            st.write("✅ Correct" if student_answer == correct else "❌ Incorrect")
                            st.write("---")


elif page == "Teacher: Results":
    st.header("Results")

    submissions = load_all_submissions()
    answers = load_all_answers()
    quiz_list = get_quiz_list()

    if submissions.empty:
        st.info("No submissions yet.")
    else:
        filter_quiz = st.selectbox("Filter by quiz", ["All"] + quiz_list["quiz_title"].drop_duplicates().tolist())
        filtered = submissions.copy()
        if filter_quiz != "All":
            filtered = filtered[filtered["quiz_title"] == filter_quiz]

        filtered["percent"] = (pd.to_numeric(filtered["score"], errors="coerce") / pd.to_numeric(filtered["total_questions"], errors="coerce") * 100).round(1)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total submissions", len(filtered))
        with c2:
            avg = filtered["percent"].mean() if not filtered.empty else 0
            st.metric("Average %", f"{avg:.1f}%")
        with c3:
            best = filtered["percent"].max() if not filtered.empty else 0
            st.metric("Highest %", f"{best:.1f}%")

        st.dataframe(filtered.sort_values("submitted_at", ascending=False), use_container_width=True)

        st.download_button(
            "Download submissions CSV",
            filtered.to_csv(index=False).encode("utf-8"),
            file_name="quiz_submissions.csv",
            mime="text/csv",
        )

        if not answers.empty:
            st.subheader("Question analysis")
            quiz_title_to_id = {row["quiz_title"]: row["quiz_id"] for _, row in quiz_list.iterrows()}
            if filter_quiz != "All" and filter_quiz in quiz_title_to_id:
                chosen_id = quiz_title_to_id[filter_quiz]
                answer_filtered = answers[answers["quiz_id"] == chosen_id].copy()
            else:
                answer_filtered = answers.copy()

            if not answer_filtered.empty:
                answer_filtered["is_correct"] = answer_filtered["is_correct"].astype(str).str.lower().isin(["true", "1"])
                summary = answer_filtered.groupby("question_no").agg(
                    attempts=("question_no", "count"),
                    correct_rate=("is_correct", "mean"),
                ).reset_index()
                summary["correct_rate"] = (summary["correct_rate"] * 100).round(1)
                st.dataframe(summary, use_container_width=True)


else:
    st.header("Setup Guide")
    st.markdown(
        """
### What this app does
- lets you create reusable quizzes from YouTube videos
- accepts 10 to 15 multiple-choice questions per quiz
- stores quiz attempts and scores
- can save locally or to Google Sheets

### Recommended project files
```text
app.py
requirements.txt
quizzes.csv
submissions.csv
answers.csv
```

### requirements.txt
```text
streamlit
pandas
openpyxl
gspread
google-auth
```

### Streamlit deployment steps
1. Create a GitHub repository.
2. Upload this file as `app.py`.
3. Add `requirements.txt`.
4. Deploy on Streamlit Community Cloud.
5. Point Streamlit at your GitHub repo.

### Google Sheets setup
Create a Google Sheet with three tabs:
- `quizzes`
- `submissions`
- `answers`

Add these secrets in Streamlit Community Cloud:
- `GOOGLE_SHEET_ID`
- `GOOGLE_SERVICE_ACCOUNT`

`GOOGLE_SERVICE_ACCOUNT` should contain the full service account JSON.
Share the Google Sheet with that service account email.

### Notes
- Local CSV files are fine for testing.
- For real repeated classroom use, Google Sheets is better.
- You can extend this to include passwords, class codes, or a teacher-only admin PIN.
        """
    )
