import os
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Voice Notes to Flashcards",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Voice Notes to Flashcards")
st.caption(
    "Turn lecture recordings or notes into flashcards and quizzes with Gemini AI."
)

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "flashcards" not in st.session_state:
    st.session_state.flashcards = pd.DataFrame()

if "quiz" not in st.session_state:
    st.session_state.quiz = pd.DataFrame()

if "score" not in st.session_state:
    st.session_state.score = None

if "source" not in st.session_state:
    st.session_state.source = ""

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

if not api_key:
    st.error("GEMINI_API_KEY is not configured.")
    st.stop()

client = genai.Client(api_key=api_key)

model = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)


def parse_response(text):
    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "", 1)
        text = text.replace("```JSON", "", 1)
        text = text.replace("```", "", 1)

    return json.loads(text.strip())


def generate_material(
    content,
    subject,
    number_of_cards,
    difficulty,
    learning_goal,
    is_audio=False
):
    system_prompt = """
You are an expert college study assistant.

Convert the provided lecture into accurate study material.

Use only information present in the lecture.
Do not invent facts or add unrelated information.
Keep explanations clear and useful for students.
Adapt the questions to the requested difficulty and learning goal.
Focus on important concepts, definitions, examples and exam-relevant ideas.

Return only valid JSON in this structure:

{
  "transcript": "clean lecture transcript",
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
      "option_a": "option A",
      "option_b": "option B",
      "option_c": "option C",
      "option_d": "option D",
      "answer": "A"
    }
  ]
}

Generate exactly the requested number of flashcards.
Generate exactly 5 quiz questions.
"""

    user_prompt = f"""
Subject: {subject}
Number of flashcards: {number_of_cards}
Difficulty: {difficulty}
Learning goal: {learning_goal}

Create study material based on the following lecture.

The student is preparing for {learning_goal.lower()}.
Make the material appropriate for a {difficulty.lower()} level.
"""

    try:
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
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )
        else:
            response = client.models.generate_content(
                model=model,
                contents=user_prompt + "\n" + content,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )

        result = parse_response(response.text)

        if not isinstance(result, dict):
            raise ValueError("Invalid response from Gemini.")

        result.setdefault("transcript", "")
        result.setdefault("flashcards", [])
        result.setdefault("quiz", [])

        flashcards = []

        for card in result["flashcards"]:
            if not isinstance(card, dict):
                continue

            question = str(
                card.get("question", "")
            ).strip()

            answer = str(
                card.get("answer", "")
            ).strip()

            if question and answer:
                flashcards.append(
                    {
                        "question": question,
                        "answer": answer,
                        "difficulty": str(
                            card.get(
                                "difficulty",
                                difficulty
                            )
                        ),
                        "topic": str(
                            card.get(
                                "topic",
                                "General"
                            )
                        )
                    }
                )

        quiz = []

        for item in result["quiz"]:
            if not isinstance(item, dict):
                continue

            fields = [
                "question",
                "option_a",
                "option_b",
                "option_c",
                "option_d",
                "answer"
            ]

            if all(
                str(item.get(field, "")).strip()
                for field in fields
            ):
                answer = str(
                    item["answer"]
                ).strip().upper()

                if answer in ["A", "B", "C", "D"]:
                    quiz.append(
                        {
                            "question": str(
                                item["question"]
                            ).strip(),
                            "option_a": str(
                                item["option_a"]
                            ).strip(),
                            "option_b": str(
                                item["option_b"]
                            ).strip(),
                            "option_c": str(
                                item["option_c"]
                            ).strip(),
                            "option_d": str(
                                item["option_d"]
                            ).strip(),
                            "answer": answer
                        }
                    )

        result["flashcards"] = flashcards[
            :number_of_cards
        ]

        result["quiz"] = quiz[:5]

        return result

    except json.JSONDecodeError:
        raise ValueError(
            "Gemini returned an invalid response. Please try again."
        )

    except Exception as e:
        raise RuntimeError(
            f"Gemini request failed: {e}"
        )


def save_result(result, source):
    st.session_state.transcript = result.get(
        "transcript",
        ""
    )

    cards = pd.DataFrame(
        result.get("flashcards", [])
    )

    if not cards.empty:
        cards["source"] = source

    st.session_state.flashcards = cards

    st.session_state.quiz = pd.DataFrame(
        result.get("quiz", [])
    )

    st.session_state.score = None
    st.session_state.source = source


with st.sidebar:
    st.header("Study Settings")

    subject = st.text_input(
        "Subject",
        value="Computer Science"
    )

    number_of_cards = st.slider(
        "Number of flashcards",
        5,
        15,
        8
    )

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"],
        index=1
    )

    learning_goal = st.selectbox(
        "Learning goal",
        [
            "Quick revision",
            "Exam preparation",
            "Understand concepts deeply",
            "Interview preparation"
        ]
    )

    st.divider()

    st.caption(
        f"Model: {model}"
    )


audio_tab, notes_tab = st.tabs(
    [
        "🎙️ Record Lecture",
        "📝 Paste Notes"
    ]
)


with audio_tab:
    st.subheader("Record your lecture")

    st.write(
        "Record a lecture explanation or revision note "
        "and turn it into structured study material."
    )

    with st.form("audio_form"):
        audio = st.audio_input(
            "Lecture recording"
        )

        generate_audio = st.form_submit_button(
            "Generate Study Material",
            type="primary",
            use_container_width=True
        )

    if generate_audio:
        if audio is None:
            st.warning(
                "Please record a lecture first."
            )
        else:
            try:
                with st.spinner(
                    "Processing your lecture..."
                ):
                    result = generate_material(
                        audio.getvalue(),
                        subject,
                        number_of_cards,
                        difficulty,
                        learning_goal,
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
                st.error(str(e))


with notes_tab:
    st.subheader("Paste lecture notes")

    with st.form("notes_form"):
        notes = st.text_area(
            "Lecture notes",
            height=250,
            placeholder="Paste your lecture notes here..."
        )

        generate_notes = st.form_submit_button(
            "Generate Study Material",
            type="primary",
            use_container_width=True
        )

    if generate_notes:
        if len(notes.strip()) < 30:
            st.warning(
                "Please enter at least 30 characters."
            )
        else:
            try:
                with st.spinner(
                    "Creating your study material..."
                ):
                    result = generate_material(
                        notes,
                        subject,
                        number_of_cards,
                        difficulty,
                        learning_goal
                    )

                    save_result(
                        result,
                        "Pasted notes"
                    )

                st.success(
                    "Study material generated."
                )

            except Exception as e:
                st.error(str(e))


cards = st.session_state.flashcards
quiz = st.session_state.quiz

st.divider()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Flashcards",
    len(cards),
    delta=f"{len(cards)} generated"
)

col2.metric(
    "Quiz Questions",
    len(quiz),
    delta=f"{len(quiz)} available"
)

word_count = (
    len(
        st.session_state.transcript.split()
    )
    if st.session_state.transcript
    else 0
)

col3.metric(
    "Transcript Words",
    word_count,
    delta=(
        "Processed"
        if word_count
        else "Waiting"
    )
)

if st.session_state.score is None:
    col4.metric(
        "Quiz Score",
        "Not attempted",
        delta="Start quiz"
    )
else:
    col4.metric(
        "Quiz Score",
        f"{st.session_state.score:.0f}%",
        delta="Completed"
    )


if st.session_state.transcript:
    st.divider()

    st.subheader(
        "📝 Lecture Transcript"
    )

    with st.expander(
        "View transcript",
        expanded=True
    ):
        st.write(
            st.session_state.transcript
        )


if not cards.empty:
    st.divider()

    st.subheader(
        "🧠 Flashcards"
    )

    edited_cards = st.data_editor(
        cards,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "question": st.column_config.TextColumn(
                "Question",
                width="large"
            ),
            "answer": st.column_config.TextColumn(
                "Answer",
                width="large"
            ),
            "difficulty": st.column_config.SelectboxColumn(
                "Difficulty",
                options=[
                    "Easy",
                    "Medium",
                    "Hard"
                ]
            ),
            "topic": st.column_config.TextColumn(
                "Topic"
            ),
            "source": st.column_config.TextColumn(
                "Source"
            )
        }
    )

    st.session_state.flashcards = edited_cards

    st.download_button(
        "⬇️ Download Flashcards",
        edited_cards.to_csv(index=False),
        file_name="flashcards.csv",
        mime="text/csv",
        use_container_width=True
    )

    if "difficulty" in edited_cards.columns:
        st.subheader(
            "📊 Flashcard Difficulty"
        )

        difficulty_data = (
            edited_cards["difficulty"]
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
            title="Flashcards by Difficulty",
            labels={
                "difficulty": "Difficulty",
                "count": "Number of Flashcards"
            }
        )

        st.plotly_chart(
            chart,
            use_container_width=True
        )


if not quiz.empty:
    st.divider()

    st.subheader(
        "🎯 Quiz"
    )

    with st.form("quiz_form"):
        answers = {}

        for index, row in quiz.iterrows():
            st.markdown(
                f"**{index + 1}. {row['question']}**"
            )

            answers[index] = st.radio(
                "Choose an answer",
                [
                    f"A. {row['option_a']}",
                    f"B. {row['option_b']}",
                    f"C. {row['option_c']}",
                    f"D. {row['option_d']}"
                ],
                key=f"question_{index}",
                label_visibility="collapsed"
            )

            st.divider()

        submit_quiz = st.form_submit_button(
            "Check Answers",
            type="primary",
            use_container_width=True
        )

    if submit_quiz:
        correct = 0

        for index, row in quiz.iterrows():
            selected = answers[index][0]

            if selected == row["answer"]:
                correct += 1

        st.session_state.score = (
            correct / len(quiz) * 100
        )

        st.success(
            f"You scored {correct}/{len(quiz)} "
            f"({st.session_state.score:.0f}%)."
        )

        if st.session_state.score >= 80:
            st.balloons()
            st.success(
                "Excellent work!"
            )

        elif st.session_state.score >= 60:
            st.info(
                "Good job. Review the missed concepts."
            )

        else:
            st.warning(
                "Review the flashcards and try the quiz again."
            )


if st.session_state.source:
    st.divider()

    st.caption(
        f"Current study session: "
        f"{st.session_state.source}"
    )
