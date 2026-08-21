# Architecture

## Overview

Lecture Notes to Flashcards is a Streamlit-based AI application that converts lecture audio or written notes into structured study material using Google Gemini.

The application follows a simple flow:

User Input → Content Processing → Gemini AI → Study Material → Streamlit UI

## Main Components

### 1. Streamlit Frontend

The Streamlit interface allows users to:

- Record or upload lecture audio
- Paste lecture notes
- Generate a cleaned transcript
- Generate flashcards
- Generate multiple-choice questions
- View generated study material

### 2. Input Processing

The application accepts two types of input:

- Text lecture notes
- Audio recordings

Text input is sent directly for processing.

Audio input is passed to Gemini for transcription and content understanding.

### 3. Gemini AI

Google Gemini is responsible for the main AI operations.

It is used to:

- Convert lecture audio into a clean transcript
- Clean and organize lecture notes
- Generate question-answer flashcards
- Generate multiple-choice questions

The application sends structured prompts to Gemini and displays the generated results.

### 4. Flashcard Generation

The lecture content is provided to Gemini with instructions to generate useful study questions and answers.

Example output:

Question:
What is supervised learning?

Answer:
Supervised learning is a machine learning approach where a model learns from labeled training data.

### 5. MCQ Generation

Gemini generates multiple-choice questions containing:

- Question
- Four options
- Correct answer
- Optional explanation

This helps students practice the lecture material.

## Application Flow

```text
                    ┌─────────────────────┐
                    │       Student       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Streamlit UI      │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
             Lecture Notes          Audio Recording
                    │                     │
                    │                     ▼
                    │              Gemini Audio
                    │              Transcription
                    │                     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Lecture Content   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Google Gemini    │
                    │      AI Model       │
                    └──────────┬──────────┘
                               │
                    ┌──────────┼──────────┐
                    │          │          │
                    ▼          ▼          ▼
               Transcript  Flashcards    MCQs
                    │          │          │
                    └──────────┴──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Streamlit Output  │
                    └─────────────────────┘
