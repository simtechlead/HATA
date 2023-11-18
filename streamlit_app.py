import streamlit as st
import os
import time
from openai import OpenAI

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

# Initialize session state for conversation history if not already present
if 'history' not in st.session_state:
    st.session_state.history = []

# Streamlit app title
st.title('HATA Chat Interface')

# Display conversation history
def display_history():
    # Using a container to control the layout
    with st.container():
        for chat in st.session_state.history:
            # Differentiate the sender of the message
            if chat["sender"] == "You":
                st.text_area(f"You: {chat['message']}", height=3, disabled=True, key=f"msg_{chat['message']}_user")
                st.markdown("---")  # Simple line separator
            else:
                st.text_area(f"HATA: {chat['message']}", height=3, disabled=True, key=f"msg_{chat['message']}_hata")
                st.markdown("---")  # Simple line separator

display_history() # Display the conversation history

# User input form at the bottom
with st.form(key='user_input_form'):
    # Using columns to create a layout with the input box and the button side by side
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("", key="input", placeholder="Send a message...")
    with col2:
        submit_button = st.form_submit_button('Send')

    if submit_button and user_input:
        # User's message
        st.session_state.history.append({"sender": "You", "message": user_input})
        # OpenAI's response
        with st.spinner('Talking to HATA...'):
            responses = interact_with_openai(user_input)
            for response in responses:
                st.session_state.history.append({"sender": "HATA", "message": response})
        # Clear the input box by rerunning the app to update the conversation history
        st.experimental_rerun()
