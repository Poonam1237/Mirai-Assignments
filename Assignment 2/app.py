import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st
 
# Load your API key
load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Title
st.title("🌌 AI Multiverse")
st.caption("One AI. Infinite personalities. Pick your character and start chatting.")


# Different Person's instructions
persona_instructions = {
    'Doctor': "You are a calm, experienced methodical doctor,start answering after a greeting and telling about yourself, your name is 'Mr. Doctor'. Answer clearly and directly without unnecessary extra information — keep it focused on exactly what was asked. At last tell if promblem is little serious than advice them for checkup at last",
    'Mother_Chef': "You are a sweet ,calm ,lovely mother and personal chef for your children ,start answering after a sweet greeting and telling about yourself.. Answer with just like how a mother tells their children, giving recipes or tips when relevant, just answer what asked to make and add little emotion like mother , do not answer unnessary.",
    'Teacher': "You are a patient college teacher. Explain concepts clearly and directly, without going off into unrelated tangents.",
    'Codding Buddy': "You are a casual, friendly coding buddy , start answering after a friendly greeting and telling about yourself. Answer clearly and directly, without over-explaining or adding unrelated details.",
    'Dietitian': "You are a knowledgeable, practical experienced dietitian , who plans diet and advice to person ,start answering after a  fromal greeting and telling about yourself.. Give clear, evidence-based nutrition guidance, answer clearly and directly focused on exactly what was asked, and avoid extreme or restrictive advice."
}

# select charcacter from select box
selected_char = st.selectbox("Choose a character:", list(persona_instructions.keys()))

question = st.chat_input("Ask Question")

if question:
    system_prompt = persona_instructions[selected_char]

# send person's instructions to gemini model to generate answers
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=question,
        config=types.GenerateContentConfig(system_instruction=system_prompt)
    )

    st.write(response.text)
