import streamlit as st
import requests


import uuid
import os

API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

st.title("Analytics Agent")
st.write("For better experience mention the table table name from which you want to query.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(""):
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role":"user","content":prompt})

    with st.chat_message("Assistant"):
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "query":prompt,
                "thread_id": st.session_state.thread_id
            }
        )
        data = response.json()
        st.markdown(data["answer"])

        st.session_state.messages.append({"role":"Assistant","content":data["answer"]})