import streamlit as st

st.title("Tomorrow's Legal Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is your legal question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add a dummy response for now
    with st.chat_message("assistant"):
        response = "I am a helpful legal assistant. How can I help you?"
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
