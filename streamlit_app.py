import streamlit as st
import os
import time
from openai import OpenAI

# Initialize session state for conversation history if not already present
if 'history' not in st.session_state:
    st.session_state.history = []

# Streamlit app title
st.title('HATA Chat Interface')

# Function to interact with OpenAI API
def interact_with_openai(user_message):
    try:
        openai_key = os.environ['OPENAI_KEY']
        org_ID = os.environ['ORG_ID']

        client = OpenAI(organization=org_ID, api_key=openai_key)
        assistant = client.beta.assistants.retrieve("asst_W9WhhX3DRDu8e0A5T5TjQMup")
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_message)
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)

        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status == 'completed':
                break
            else:
                time.sleep(1)

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        responses = []
        for each in messages:
            if each.role == 'assistant':
                responses.append(each.content[0].text.value if isinstance(each.content, list) and hasattr(each.content[0], 'text') else str(each.content))
        return responses

    except Exception as e:
        st.error(f"Error: {e}")
        return []

# Display conversation history in a more chat-like format
st.write("Chat:")
for index, chat in enumerate(st.session_state.history):
    sender = chat["sender"]
    message = chat["message"]
    if sender == "You":
        st.text_area(f"You: {message}", key=f"user_{index}", height=50, disabled=True)
    else:
        st.text_area(f"HATA: {message}", key=f"hata_{index}", height=50, disabled=True)

# User input form at the bottom
with st.form(key='user_input_form'):
    user_input = st.text_input("Send a message:", key="input")
    submit_button = st.form_submit_button(label='Send')

# On form submission, append the message and get a response
if submit_button and user_input:
    st.session_state.history.append({"sender": "You", "message": user_input})
    with st.spinner('Talking to HATA...'):
        responses = interact_with_openai(user_input)
        for response in responses:
            st.session_state.history.append({"sender": "HATA", "message": response})
    st.experimental_rerun()
