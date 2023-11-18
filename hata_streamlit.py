import streamlit as st
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize global variables
openai_key = os.getenv('OPENAI_KEY')
org_ID = os.getenv('ORG_ID')
client = None

def initialize_openai_client():
    global client
    client = OpenAI(
        organization=org_ID,
        api_key=openai_key
    )

def list_assistants():
    try:
        return client.beta.assistants.list(order="desc", limit="5")
    except Exception as e:
        st.error(f"Error listing assistants: {e}")

def retrieve_assistant(assistant_id):
    try:
        return client.beta.assistants.retrieve(assistant_id)
    except Exception as e:
        st.error(f"Error retrieving assistant: {e}")

def create_thread():
    try:
        return client.beta.threads.create()
    except Exception as e:
        st.error(f"Error creating thread: {e}")

def send_message(thread_id, content):
    try:
        return client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=content
        )
    except Exception as e:
        st.error(f"Error sending message to thread: {e}")

def run_assistant(thread_id, assistant_id):
    try:
        return client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
    except Exception as e:
        st.error(f"Error running assistant: {e}")

def wait_for_run_completion(thread_id, run_id):
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
            break

def display_responses(thread_id):
    try:
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        for each in messages:
            if each.role == 'assistant':
                if isinstance(each.content, list) and hasattr(each.content[0], 'text'):
                    st.write("Assistant: " + each.content[0].text.value)
                else:
                    st.write("Assistant message content: " + str(each.content))
    except Exception as e:
        st.error(f"Error retrieving messages: {e}")

def main():
    st.title("OpenAI Assistant Manager")

    initialize_openai_client()

    if st.button("List Last 5 Assistants"):
        assistants = list_assistants()
        st.json(assistants)

    assistant_id = st.text_input("Enter Assistant ID")
    if st.button("Retrieve Assistant"):
        assistant = retrieve_assistant(assistant_id)
        st.json(assistant)

    # Additional Streamlit interactions can be added here as needed.

if __name__ == "__main__":
    main()
