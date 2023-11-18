import streamlit as st
from openai import OpenAI
import os
import time

# Function to send message to OpenAI and get response
def send_message(message):
    # Assuming OPENAI_KEY and ORG_ID are set in your Streamlit secrets or environment variables
    openai_key = st.secrets['OPENAI_KEY']
    org_ID = st.secrets['ORG_ID']

    client = OpenAI(organization=org_ID, api_key=openai_key)

    # Replace 'asst_W9WhhX3DRDu8e0A5T5TjQMup' with your Assistant's ID
    # This is a placeholder assistant ID and won't work in your code.
    assistant_id = "asst_W9WhhX3DRDu8e0A5T5TjQMup"

    try:
        # Create a new thread
        thread = client.beta.threads.create()

        # Send a message to the thread
        message_response = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
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
        responses = [msg.content for msg in messages if msg.role == 'assistant']

        return "\n".join(responses)

    except Exception as e:
        st.error(f"Error: {e}")
        return "I'm sorry, I couldn't fetch a response. Please check the error message above."

# Initialize session state for conversation history if not already present
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Streamlit app title
st.title('HATA Chat Interface')

# Use a form to handle input and button as a unit
with st.form(key='message_form'):
    user_input = st.text_input("Send a message:")
    submit_button = st.form_submit_button(label='Send')

# On 'Enter' or button press, append the message and get a response
if submit_button and user_input:
    # User's message
    st.session_state.history.append({"sender": "You", "message": user_input})

    # OpenAI's response
    response = send_message(user_input)
    st.session_state.history.append({"sender": "HATA", "message": response})

# Display conversation history
for chat in st.session_state.history:
    # Differentiate between user and HATA's messages
    if chat["sender"] == "You":
        st.text_area("", value=chat["message"], key=str(chat["message"] + "_user"), height=75, disabled=True)
    else:
        st.text_area("", value=chat["message"], key=str(chat["message"] + "_hata"), height=75, disabled=True, style={"text-align": "right", "color": "blue"})

# Scroll to the last message
if st.session_state.history:
    st.session_state.last_message = st.session_state.history[-1]["message"]
    st.text_input("Hidden text input for scrolling", value="", key="scroll_to_bottom", on_change=st.experimental_rerun, args=())
    st.session_state.scroll_to_bottom = st.session_state.last_message  # Trigger scroll

    # JavaScript to scroll to the bottom of the page
    st.markdown("""
        <script>
        const elements = document.getElementsByClassName('stTextInput');
        const lastElement = elements[elements.length - 1];
        lastElement.scrollIntoView(false);
        </script>
        """, unsafe_allow_html=True)
