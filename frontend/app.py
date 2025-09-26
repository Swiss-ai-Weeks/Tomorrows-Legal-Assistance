import streamlit as st
import time
import os
import sys
import re
import textwrap
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apertus.apertus import LangchainApertus

st.set_page_config(
    layout="wide",
    page_title="Tomorrow's Legal Assistance",
    page_icon="frontend/media/favicon.ico"
)

# Custom CSS to make font smaller
st.markdown("""
<style>
.stApp {
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

def format_chat_history_for_markdown(messages):
    markdown_string = ""
    for message in messages:
        role = "User" if message["role"] == "user" else "Assistant"
        markdown_string += f"**{role}:**\n"
        markdown_string += message["content"] + "\n\n"
        markdown_string += "---\n\n"
    return markdown_string

def sanitize_filename(filename):
    return re.sub(r'[^\w\s-]', '', filename).strip()

# Sidebar for chat management
with st.sidebar:
    st.image("frontend/media/AXA_Versicherungen_Logo.svg.png", width=150)
    if st.button("New Chat"):
        st.session_state.clear()
        st.rerun()

    if st.session_state.get("messages"):
        if st.button("Delete Chat"):
            st.session_state.clear()
            st.rerun()

        chat_history_md = format_chat_history_for_markdown(st.session_state.messages)
        
        file_name = "chat_history.md"
        if "chat_title" in st.session_state:
            sanitized_title = sanitize_filename(st.session_state.chat_title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{sanitized_title}_{timestamp}.md"
        
        st.download_button(
            label="Save Chat",
            data=chat_history_md,
            file_name=file_name,
            mime="text/markdown",
        )

st.title("Tomorrow's Legal Assistant")

if "chat_title" in st.session_state:
    st.subheader(st.session_state.chat_title)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display initial message if chat is empty
if not st.session_state.messages:
    st.info("Welcome! Please describe your legal situation in the chat below.")

# Display chat messages from history
for message in st.session_state.messages:
    avatar_path = "frontend/media/Gemini_Generated_Image_wl26p8wl26p8wl26_zoomin.png" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar_path):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is your legal question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Main logic for processing user input
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    prompt = st.session_state.messages[-1]["content"]

    # Step 1: Generate Title (if not exists) and rerun
    if "chat_title" not in st.session_state:
        api_key = os.environ.get("APERTUS_API_KEY")
        if api_key:
            with st.spinner("Generating title..."):
                try:
                    llm = LangchainApertus(api_key=api_key)
                    title_prompt = f"""You are an expert title generator. Your mission is to create a concise, filename-safe title from a user's query.

                    ### Your Instructions
                    1.  **Word Count:** The title MUST be 5 words or less.
                    2.  **Content:** Your response MUST contain ONLY the words of the title.
                    3.  **Formatting:** The title MUST be plain text, free of quotation marks or any prefixes like "Title:".
                    4.  **No Commentary:** You MUST NOT add any notes or explanations. Your entire response is the title.
                    5.  **Punctuation:** The title MUST end with a word, not with any punctuation like a question mark or period.

                    ### Example
                    Query: "I received a speeding ticket for 500 CHF, can I fight it?"
                    Title: Contesting a 500 CHF Speeding Ticket

                    ### Task
                    Query: '{prompt}'
                    Title:"""
                    response = llm.invoke(title_prompt)
                    clean_title = response.content.strip().split('\n')[0]

                    st.session_state.chat_title = clean_title
                    st.rerun() # Rerun to display title and move to analysis step
                except Exception as e:
                    st.error(f"Could not generate title: {e}")
        else:
            st.warning("APERTUS_API_KEY not set. Cannot generate title.")
    
    # Step 2: Generate and display assistant response
    with st.chat_message("assistant", avatar="frontend/media/Gemini_Generated_Image_wl26p8wl26p8wl26_zoomin.png"):
        message_placeholder = st.empty()
        full_response = ""
        
        api_key = os.environ.get("APERTUS_API_KEY")
        if not api_key:
            st.warning("APERTUS_API_KEY not set. Cannot get analysis.")
            st.stop()

        with st.spinner("Analyzing your situation..."):
            try:
                # Prepare the input for the backend agent
                case_input = {
                    "text": prompt,
                    "metadata": {
                        "language": "en",
                        "court_level": "cantonal",
                        "preferred_units": "months"
                    }
                }

                # Make a POST request to the backend endpoint
                response = requests.post("http://localhost:8000/api/agent_with_tools", json=case_input)
                response.raise_for_status()  # Raise an exception for bad status codes

                # The response from the agent is a JSON object.
                # We need to format it nicely for display.
                analysis_result = response.json()

                # Handle the cost field, which could be a dictionary
                cost = analysis_result.get('estimated_cost', 'N/A')
                if isinstance(cost, dict):
                    total_cost = cost.get('total_chf', 'N/A')
                    cost_str = f"{total_cost:.2f} CHF" if isinstance(total_cost, (int, float)) else 'N/A'
                else:
                    cost_str = f"{cost} CHF" if isinstance(cost, (int, float)) else 'N/A'

                # Format the response into a markdown string
                processed_text = f"""
**Case Category:** {analysis_result.get('category', 'N/A')}

**Likelihood of Winning:** {analysis_result.get('likelihood_win', 'N/A')}%

**Estimated Cost:** {cost_str}

**Estimated Timeframe:** {analysis_result.get('estimated_time', 'N/A')}
"""

            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to the backend: {e}")
                st.stop()
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                st.stop()

        # Use the processed_text for streaming
        lines = processed_text.split('\n')
        for line in lines:
            full_response += line + "\n"
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()
    
