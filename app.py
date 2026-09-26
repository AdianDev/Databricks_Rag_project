import streamlit as st

st.set_page_config(
    page_title="Microcontroller RAG Assistant",
    page_icon="🔧",
    layout="centered"
)

st.title("🔧 Microcontroller RAG Assistant")

st.caption(
    "Ask questions about RP2040, RP2350 and related Raspberry Pi documentation."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask a question...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    response = (
        "This is a test response. "
        "The RAG backend will be connected next."
    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):
        st.markdown(response)

if st.button("🗑️ New Chat"):
    st.session_state.messages = []
    st.rerun()
