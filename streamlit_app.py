import streamlit as st
import os
import time
from openai import OpenAI

# Set up the page configuration and title
st.set_page_config(page_title="HATA")
st.title('Asisten Penerjemah Indonesia Simalungun')

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

# Initialize session state for conversation history if not already present
if 'history' not in st.session_state:
    st.session_state.history = [{"role": "assistant", "content": "kata yang ingin diterjemahkan?"}]
if 'reset_flag' not in st.session_state:
    st.session_state.reset_flag = False

# Display chat messages
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Input form for user message
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Send a message:", key="input")
    submit_button = st.form_submit_button(label='Send')
    reset_button = st.form_submit_button(label='Reset Conversation')

# Handle message submission
if submit_button and user_input:
    if st.session_state.reset_flag:
        # Reset history if the flag is set
        st.session_state.history = [{"role": "assistant", "content": "kata yang ingin diterjemahkan?"}]
        st.session_state.reset_flag = False

    st.session_state.history.append({"role": "user", "content": user_input})
    responses = interact_with_openai(user_input)
    for response in responses:
        st.session_state.history.append({"role": "assistant", "content": response})

    # Set flag to reset history on next input
    st.session_state.reset_flag = True

    # Clear the input box by rerunning the app to update the conversation history
    st.experimental_rerun()

# Handle reset button
if reset_button:
    st.session_state.history = [{"role": "assistant", "content": "kata yang ingin diterjemahkan?"}]
    st.session_state.reset_flag = False
    st.experimental_rerun()
