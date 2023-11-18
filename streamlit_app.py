import streamlit as st
import os
import time
from openai import OpenAI

# Streamlit app title
st.title('OpenAI GPT-3 Assistant')

# User input
user_input = st.text_input("Enter your message for the GPT-3 Assistant:")

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
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run.status == 'completed':
                break
            else:
                time.sleep(1)

        # Retrieve and return responses
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        responses = []
        for each in messages:
            if each.role == 'assistant':
                if isinstance(each.content, list) and hasattr(each.content[0], 'text'):
                    responses.append(each.content[0].text.value)
                else:
                    responses.append(str(each.content))
        return responses

    except Exception as e:
        st.error(f"Error: {e}")
        return []

# Displaying the results
if user_input:
    with st.spinner('Talking to GPT-3...'):
        responses = interact_with_openai(user_input)
    for response in responses:
        st.write(response)

# Footer or additional information
st.markdown("### Note")
st.markdown("This is a simple Streamlit app to interact with OpenAI's GPT-3 Assistant.")
