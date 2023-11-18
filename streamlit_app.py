import streamlit as st
import os
import time
from openai import OpenAI

# Set up the page configuration and title
st.set_page_config(page_title="HATA Chat Interface", layout="wide")
st.title('HATA Chat Interface')

# Function to interact with OpenAI API
def interact_with_openai(user_message):
    # Placeholder for the actual OpenAI API interaction
    # ...

# Initialize session state for conversation history if not already present
if 'history' not in st.session_state:
    st.session_state.history = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display chat messages
def display_messages():
    # Create a container for messages and use st.expander to make it scrollable
    with st.container():
        for message in reversed(st.session_state.history):  # Display from the bottom up
            role = "You" if message["role"] == "user" else "HATA"
            st.markdown(f"**{role}:**")
            st.text_area("", value=message["content"], height=3, disabled=True, key=f"{role}_{time.time()}")
            st.markdown("<hr>", unsafe_allow_html=True)  # Horizontal line

# User input form at the bottom
def chat_input():
    with st.container():
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("Send a message:", key="input")
            submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:
            st.session_state.history.append({"role": "user", "content": user_input})
            responses = interact_with_openai(user_input)
            for response in responses:
                st.session_state.history.append({"role": "assistant", "content": response})
            st.experimental_rerun()

# Layout the chat history and the input area
display_messages()
chat_input()

# To make sure the latest message is visible, we can use an anchor (a placeholder)
# and scroll to its location after a new message is added
if 'anchor' not in st.session_state:
    st.session_state.anchor = st.empty()

st.session_state.anchor.markdown(" ")  # This space will serve as an anchor
st.script_request_queue.enqueue("scrollTo", {"id": st.session_state.anchor._anchor_id})
