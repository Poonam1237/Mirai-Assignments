# Lecture Notes to Flashcards

Lecture Notes to Flashcards is a Streamlit application that uses Google Gemini to convert lecture recordings or written lecture notes into useful study material.

The application can create a cleaned transcript, flashcards and multiple-choice questions from the provided lecture content.

## Features

- Record lecture audio using the microphone
- Paste lecture notes manually
- Convert lecture content into a clean transcript
- Generate AI-based flashcards
- Generate multiple-choice questions
- Choose the subject and number of flashcards
- Edit generated flashcards
- View flashcard difficulty using a chart
- Take an automatically generated quiz
- Calculate quiz score
- Download flashcards as a CSV file
- Store generated results using Streamlit session state

## Technologies Used

- Python
- Streamlit
- Google Gemini API
- Pandas
- Plotly

## Project Structure

```text
Lecture-Notes-to-Flashcards/
│
├── app.py
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
├── .gitignore

