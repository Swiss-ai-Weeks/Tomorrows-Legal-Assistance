import streamlit as st
import time

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

# Sidebar for chat management
with st.sidebar:
    st.image("frontend/media/AXA_Versicherungen_Logo.svg.png", width=150)
    if st.button("New Chat"):
        st.session_state.messages = []
    if st.button("Delete Chat"):
        st.session_state.messages = []
        st.success("Chat deleted!")

st.title("Tomorrow's Legal Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display initial message if chat is empty
if not st.session_state.messages:
    st.info("Welcome! Please describe your legal situation in the chat below.")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is your legal question?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Mockup of Langchain agent response
        mock_response = {
            "likelihood_of_winning": "75%",
            "cost_range": "CHF 2,000 - CHF 5,000",
            "timeframe": "3-6 months",
            "next_steps": [
                "Consult with a specialized lawyer.",
                "Gather all relevant documentation.",
                "Prepare a detailed timeline of events."
            ],
            "reasoning": "Based on the provided information, the case appears to have a strong foundation. However, the outcome depends on the quality of evidence presented."
        }
        
        response_text = f"""### Legal Analysis Report

Here is a preliminary analysis of your situation:

- **Likelihood of Winning:** {mock_response['likelihood_of_winning']}
- **Estimated Cost Range:** {mock_response['cost_range']}
- **Estimated Timeframe:** {mock_response['timeframe']}

#### Reasoning:
{mock_response['reasoning']}

#### Recommended Next Steps:
"""
        for step in mock_response['next_steps']:
            response_text += f"- {step}\n"

        # Simulate stream of response with milliseconds delay
        lines = response_text.split('\n')
        for line in lines:
            full_response += line + "\n"
            time.sleep(0.1)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})