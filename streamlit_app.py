import streamlit as st
import os
import time
from openai import OpenAI

def get_openai_client():
    openai_key = os.environ.get('OPENAI_KEY')
    org_id = os.environ.get('ORG_ID')
    return OpenAI(organization=org_id, api_key=openai_key)

def create_thread(client):
    try:
        return client.beta.threads.create()
    except Exception as e:
        st.error(f"Error creating thread: {e}")
        return None

def send_message_to_thread(client, thread_id, message_content):
    try:
        return client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message_content
        )
    except Exception as e:
        st.error(f"Error sending message to thread: {e}")
        return None

def run_assistant(client, thread_id, assistant_id):
    try:
        return client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
    except Exception as e:
        st.error(f"Error running assistant: {e}")
        return None

def wait_for_run_completion(client, thread_id, run_id):
    while True:
        try:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            if run.status == 'completed':
                return run
            else:
                time.sleep(1)
        except Exception as e:
            st.error(f"Error while waiting for run to complete: {e}")
            return None

def display_responses(client, thread_id):
    try:
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        for each in messages:
            if each.role == 'assistant':
                st.write("Assistant: " + str(each.content))
    except Exception as e:
        st.error(f"Error retrieving messages: {e}")

# Streamlit app layout
st.title('OpenAI Assistant Interaction')

# Create OpenAI client
client = get_openai_client()

# Retrieve the assistant ID
assistant_id = "asst_W9WhhX3DRDu8e0A5T5TjQMup"  # Replace with your assistant's ID

# User input for the message
user_message = st.text_input("Enter your message to the assistant:")

if st.button('Send') and user_message:
    with st.spinner('Processing...'):
        # Create a new thread
        thread = create_thread(client)
        if thread:
            # Send message and run the assistant
            message = send_message_to_thread(client, thread.id, user_message)
            if message:
                run = run_assistant(client, thread.id, assistant_id)
                if run:
                    completed_run = wait_for_run_completion(client, thread.id, run.id)
                    if completed_run:
                        # Display responses
                        display_responses(client, thread.id)
