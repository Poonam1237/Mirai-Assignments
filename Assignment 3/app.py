import os
from dotenv import load_dotenv
from google import genai
import streamlit as st

load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

st.title("🌌 AI Multiverse Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_message := st.chat_input("Say something..."):
    st.session_state.messages.append({"role": "user", "content": user_message})

    with st.chat_message("user"):
        st.markdown(user_message)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message
    )

    assistant_reply = response.text

    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_reply}
    )
