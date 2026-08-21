import os
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Lecture Notes to Flashcards",
    page_icon="📚",
    layout="wide"
)

st.title("Lecture Notes to Flashcards")
st.write("Convert your lecture recording or notes into flashcards and a short quiz.")

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "flashcards" not in st.session_state:
    st.session_state.flashcards = pd.DataFrame()

if "quiz" not in st.session_state:
    st.session_state.quiz = pd.DataFrame()

if "score" not in st.session_state:
    st.session_state.score = None

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key is missing. Add GEMINI_API_KEY to your environment variables.")
    st.stop()

client = genai.Client(api_key=api_key)

model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def parse_response(text):
    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "", 1)
        text = text.replace("```", "", 1)

    return json.loads(text)


def create_study_material(content, subject, number_of_cards, is_audio=False):

    system_prompt = """
You are an assistant that helps college students study.

Read the provided lecture content and create useful study material.

Do not add information that is not present in the lecture.
Keep the explanations simple and suitable for a college student.

Return only JSON in this format:

{
    "transcript": "clean version of the lecture",
    "flashcards": [
        {
            "question": "question",
            "answer": "answer",
            "difficulty": "Easy",
            "topic": "topic"
        }
    ],
    "quiz": [
        {
            "question": "question",
            "option_a": "option",
            "option_b": "option",
            "option_c": "option",
            "option_d": "option",
            "answer": "A"
        }
    ]
}

Create the requested number of flashcards and at least 5 quiz questions.
"""

    user_prompt = f"""
Subject: {subject}

Number of flashcards: {number_of_cards}

Create study material from this lecture.
"""

    if is_audio:
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_bytes(
                    data=content,
                    mime_type="audio/wav"
                ),
                user_prompt
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3,
                response_mime_type="application/json"
            )
        )
    else:
        response = client.models.generate_content(
            model=model,
            contents=user_prompt + "\n\nLecture notes:\n" + content,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3,
                response_mime_type="application/json"
            )
        )

    return parse_response(response.text)


def save_result(result, source):

    st.session_state.transcript = result.get("transcript", "")

    cards = pd.DataFrame(result.get("flashcards", []))

    if not cards.empty:
        cards["source"] = source

    st.session_state.flashcards = cards

    st.session_state.quiz = pd.DataFrame(
        result.get("quiz", [])
    )

    st.session_state.score = None


with st.sidebar:

    st.header("Study Settings")

    subject = st.text_input(
        "Subject",
        "Computer Science"
    )

    number_of_cards = st.slider(
        "Number of flashcards",
        5,
        15,
        8
    )

    st.divider()

    st.write("Model")
    st.code(model)


tab1, tab2 = st.tabs(
    ["Record Lecture", "Paste Notes"]
)


with tab1:

    st.subheader("Record your lecture")

    st.write(
        "Record a short explanation of the topic you want to study."
    )

    with st.form("audio_form"):

        audio = st.audio_input(
            "Lecture recording"
        )

        generate_audio = st.form_submit_button(
            "Generate Study Material",
            type="primary"
        )

    if generate_audio:

        if audio is None:

            st.warning(
                "Please record something before generating the study material."
            )

        else:

            try:

                with st.spinner(
                    "Processing your lecture..."
                ):

                    result = create_study_material(
                        audio.getvalue(),
                        subject,
                        number_of_cards,
                        True
                    )

                    save_result(
                        result,
                        "Lecture recording"
                    )

                st.success(
                    "Study material generated."
                )

            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )


with tab2:

    st.subheader("Paste lecture notes")

    with st.form("notes_form"):

        notes = st.text_area(
            "Lecture notes",
            height=250,
            placeholder="Paste your lecture notes here..."
        )

        generate_notes = st.form_submit_button(
            "Generate Study Material",
            type="primary"
        )

    if generate_notes:

        if len(notes.strip()) < 30:

            st.warning(
                "Please enter a little more content."
            )

        else:

            try:

                with st.spinner(
                    "Creating flashcards..."
                ):

                    result = create_study_material(
                        notes,
                        subject,
                        number_of_cards
                    )

                    save_result(
                        result,
                        "Pasted notes"
                    )

                st.success(
                    "Study material generated."
                )

            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )


cards = st.session_state.flashcards
quiz = st.session_state.quiz


st.divider()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Flashcards",
    len(cards)
)

col2.metric(
    "Quiz Questions",
    len(quiz)
)

if st.session_state.score is None:

    col3.metric(
        "Quiz Score",
        "Not attempted"
    )

else:

    col3.metric(
        "Quiz Score",
        f"{st.session_state.score:.0f}%"
    )


if st.session_state.transcript:

    st.divider()

    st.subheader("Lecture Summary")

    with st.expander(
        "View transcript",
        expanded=True
    ):

        st.write(
            st.session_state.transcript
        )


if not cards.empty:

    st.divider()

    st.subheader("Flashcards")

    edited_cards = st.data_editor(
        cards,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic"
    )

    st.session_state.flashcards = edited_cards

    st.download_button(
        "Download Flashcards",
        edited_cards.to_csv(index=False),
        file_name="flashcards.csv",
        mime="text/csv"
    )

    if "difficulty" in cards.columns:

        st.subheader(
            "Flashcard Difficulty"
        )

        difficulty_data = (
            cards["difficulty"]
            .value_counts()
            .reset_index()
        )

        difficulty_data.columns = [
            "difficulty",
            "count"
        ]

        chart = px.bar(
            difficulty_data,
            x="difficulty",
            y="count",
            title="Flashcards by Difficulty"
        )

        st.plotly_chart(
            chart,
            use_container_width=True
        )


if not quiz.empty:

    st.divider()

    st.subheader("Quick Quiz")

    with st.form("quiz_form"):

        selected_answers = {}

        for i, row in quiz.iterrows():

            st.write(
                f"**{i + 1}. {row['question']}**"
            )

            selected_answers[i] = st.radio(
                "Select an answer",
                [
                    f"A. {row['option_a']}",
                    f"B. {row['option_b']}",
                    f"C. {row['option_c']}",
                    f"D. {row['option_d']}"
                ],
                key=f"question_{i}"
            )

        submit_quiz = st.form_submit_button(
            "Check Answers",
            type="primary"
        )

    if submit_quiz:

        correct = 0

        for i, row in quiz.iterrows():

            selected = selected_answers[i][0]

            correct_answer = str(
                row["answer"]
            ).strip().upper()

            if selected == correct_answer:
                correct += 1

        score = (
            correct / len(quiz)
        ) * 100

        st.session_state.score = score

        if score >= 80:

            st.success(
                f"Good job. Your score is {score:.0f}%."
            )

        elif score >= 50:

            st.warning(
                f"You scored {score:.0f}%. "
                "Review the flashcards once more."
            )

        else:

            st.error(
                f"You scored {score:.0f}%. "
                "It would be useful to review the lecture again."
            )


if st.session_state.transcript:

    st.divider()

    with st.expander("How the application works"):

        st.write(
            "The application accepts either a lecture recording "
            "or written notes. Gemini processes the content and "
            "returns a transcript, flashcards and quiz questions. "
            "The results are stored in Streamlit session state "
            "and displayed using Pandas and Streamlit components."
        )
