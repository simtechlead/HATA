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
        # Retrieve API key and organization ID from Streamlit's settings
        openai_key = os.environ['OPENAI_KEY']
        org_ID = os.environ['ORG_ID']

        client = OpenAI(
            organization=org_ID,
            api_key=openai_key
        )

        # Retrieve a specific assistant
        assistant = client.beta.assistants.retrieve("asst_W9WhhX3DRDu8e0A5T5TjQMup")

        # Create a new thread
        thread = client.beta.threads.create()

        # Send a message to the thread
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Wait for completion
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                break
            else:
                time.sleep(1)

        # Retrieve and return responses
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        responses = []
        for each in messages:
            if each.role == 'assistant':
                responses.append(each.content[0].text.value if isinstance(each.content, list) and hasattr(each.content[0], 'text') else str(each.content))
        return responses

    except Exception as e:
        st.error(f"Error: {e}")
        return []

# Use a form for user input
with st.form(key='user_input_form'):
    user_input = st.text_input("Send a message:")
    submit_button = st.form_submit_button(label='Send')

# On form submission, append the message and get a response
if submit_button and user_input:
    # User's message
    st.session_state.history.append({"sender": "You", "message": user_input})

    # OpenAI's response
    with st.spinner('Talking to HATA...'):
        responses = interact_with_openai(user_input)
        for response in responses:
            st.session_state.history.append({"sender": "HATA", "message": response})

# Display conversation history
for index, chat in enumerate(st.session_state.history):
    sender = chat["sender"]
    message = chat["message"]
    key = f"{sender}_{index}"
    if sender == "You":
        st.text_area("", value=message, key=key, height=75, disabled=True)
    else:
        st.text_area("", value=message, key=key, height=75, disabled=True)

# Ensure the last message is visible
if st.session_state.history:
    st.session_state.last_message = st.session_state.history[-1]["message"]
    st.text_input("Hidden text input for scrolling", value="", key="scroll_to_bottom", on_change=st.experimental_rerun, args=())
    st.session_state.scroll_to_bottom = st.session_state.last_message  # Trigger scroll
