import streamlit as st
import os
import time
from openai import OpenAI

# Set up the page configuration and title
st.set_page_config(page_title="HATA Chat Interface", layout="wide")
st.title('HATA Chat Interface')

# Function to interact with OpenAI API
def interact_with_openai(user_message):
    # Placeholder for API interaction code
    # Simulate a response for demonstration purposes
    return ["This is a simulated response."]

# Initialize session state for conversation history if not already present
if 'history' not in st.session_state:
    st.session_state.history = []

if 'translation' not in st.session_state:
    st.session_state.translation = []

if 'phonetics' not in st.session_state:
    st.session_state.phonetics = []

if 'additional_info' not in st.session_state:
    st.session_state.additional_info = []

# Layout with fixed columns
col1, col2, col3, col4 = st.columns(4)

# Chat input and history
with col1:
    st.subheader("Chat input:")
    user_input = st.text_input("Enter your message:", key="chat_input")
    if st.button('Send', key="send_button"):
        st.session_state.history.append(user_input)  # Add to chat history
        responses = interact_with_openai(user_input)  # Get the response
        st.session_state.translation.append(responses[0])  # Add to translation
        st.session_state.phonetics.append("Phonetic representation")  # Placeholder
        st.session_state.additional_info.append("Additional information")  # Placeholder

    st.subheader("Chat history:")
    for message in reversed(st.session_state.history):  # Display from the bottom up
        st.text(message)

# Translation column
with col2:
    st.subheader("Translation:")
    for translation in st.session_state.translation:
        st.text(translation)

# Phonetics column
with col3:
    st.subheader("Phonetics:")
    for phonetic in st.session_state.phonetics:
        st.text(phonetic)

# Additional information column
with col4:
    st.subheader("Additional information:")
    for info in st.session_state.additional_info:
        st.text(info)

# Clear the input box by rerunning the app to update the conversation history
if 'rerun' in st.session_state:
    st.session_state.rerun = False
    st.experimental_rerun()

# Handle message submission at the end to allow for rerun to clear the input box
if st.session_state.get('rerun', False):
    user_input = st.session_state.get('chat_input', '')
    if user_input:
        st.session_state.history.append({"role": "user", "content": user_input})
        responses = interact_with_openai(user_input)
        for response in responses:
            st.session_state.history.append({"role": "assistant", "content": response})
        st.session_state['rerun'] = True  # Set the flag to rerun the app
