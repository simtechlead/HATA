import streamlit as st
import os
import time
from openai import OpenAI

# Set up the page configuration with a custom primary color
st.set_page_config(page_title="Penerjemah Indonesia Simalungun", page_icon=":book:")

# Define a color theme
primary_color = "#6c5ce7"  # A vibrant shade of purple
background_color = "#ffffff"  # A clean white background
text_color = "#333333"  # A dark gray for text that ensures good readability
button_color = "#1e88e5"  # A cheerful blue for buttons
info_color = "#e1bee7"  # A light purple for info messages

# Inject custom CSS with st.markdown
custom_css = f"""
<style>
    /* Main interface colors */
    :root {{
        --primary: {primary_color};
        --btn-primary-bg: {button_color};
        --info-background: {info_color};
    }}

    /* Background color for the main content area */
    .stApp {{
        background-color: {background_color};
    }}

    /* Streamlit's native elements and widgets colors */
    .st-bb {{
        background-color: var(--btn-primary-bg);
        border-color: var(--btn-primary-bg);
    }}
    
    .st-at {{
        background-color: var(--info-background);
    }}

    /* Button colors */
    button.primary {{
        background-color: var(--btn-primary-bg);
        border-color: var(--btn-primary-bg);
    }}

    /* Info color */
    .stAlert {{
        background-color: var(--info-background);
    }}

    /* Text color */
    body {{
        color: {text_color};
    }}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Set up the page configuration and title
st.set_page_config(page_title="Hata")
st.title('Penerjemah Indonesia Simalungun')

# Add user guide
st.info("""
    **Instruksi Penggunaan:**
    Masukkan kata dalam bahasa Indonesia yang ingin Anda terjemahkan ke bahasa Simalungun di kolom chat di bawah ini. contoh: kata belajar
""")

# Function to interact with OpenAI API
def interact_with_openai(user_message):
    try:
        # Prepend a directive to respond in Indonesian
        user_message = "Respond in Indonesian: " + user_message
        
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

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if user_input := st.chat_input("Kata yang ingin diterjemahkan:"):
    # Display user message in chat message container
    st.chat_message("user").markdown(user_input)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get responses from OpenAI
    responses = interact_with_openai(user_input)
    for response in responses:
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
