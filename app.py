import streamlit as st
from src.helper import (
    get_pdf_text,
    get_text_chunks,
    get_vector_store,
    get_conversational_chain
)
import time
from datetime import datetime, timedelta

# إعدادات الحصة
MAX_QUESTIONS = 10
QUOTA_RESET_MINUTES = 60

# تهيئة session state
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
if 'quota_exceeded_time' not in st.session_state:
    st.session_state.quota_exceeded_time = None
if 'conversation' not in st.session_state:
    st.session_state.conversation = None
if 'chatHistory' not in st.session_state:
    st.session_state.chatHistory = []

def display_countdown():
    remaining_time = st.session_state.quota_exceeded_time + timedelta(minutes=QUOTA_RESET_MINUTES) - datetime.now()
    if remaining_time.total_seconds() > 0:
        mins, secs = divmod(int(remaining_time.total_seconds()), 60)
        st.error(f"⚠️ Quota exceeded! Try again in {mins:02d}:{secs:02d}")
        time.sleep(1)
        st.rerun()
    else:
        st.session_state.question_count = 0
        st.session_state.quota_exceeded_time = None
        st.rerun()

def user_input(user_question):
    if st.session_state.quota_exceeded_time:
        display_countdown()
        return
    
    if st.session_state.question_count >= MAX_QUESTIONS:
        st.session_state.quota_exceeded_time = datetime.now()
        st.error(f"⚠️ You've reached your limit of {MAX_QUESTIONS} questions.")
        return
    
    try:
        with st.spinner("Analyzing documents..."):
            response = st.session_state.conversation({'question': user_question})
            st.session_state.chatHistory = response['chat_history']
            st.session_state.question_count += 1

            for i, message in enumerate(st.session_state.chatHistory):
                if i % 2 == 0:
                    st.markdown(
                        f"<div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin: 5px 0;'>"
                        f"<strong>👤 User:</strong> {message.content}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<div style='background-color: #e6f7ff; padding: 10px; border-radius: 5px; margin: 5px 0;'>"
                        f"<strong>🤖 Assistant:</strong> {message.content}</div>",
                        unsafe_allow_html=True
                    )

            st.sidebar.progress(st.session_state.question_count / MAX_QUESTIONS)
            st.sidebar.caption(f"Questions used: {st.session_state.question_count}/{MAX_QUESTIONS}")

    except Exception as e:
        st.error(f"Error processing your question: {str(e)}")

def main():
    st.set_page_config(page_title="PDF Insight Pro", page_icon="📚", layout="centered")
    st.title("📚 PDF Insight Pro")
    st.caption("Extract precise answers from your documents using AI")

    with st.sidebar:
        st.header("Settings")
        st.metric("Question Quota", f"{MAX_QUESTIONS} per hour")
        st.progress(st.session_state.question_count / MAX_QUESTIONS)
        st.caption(f"Used: {st.session_state.question_count}/{MAX_QUESTIONS}")

        pdf_docs = st.file_uploader(
            "Upload PDF files", 
            type=["pdf"], 
            accept_multiple_files=True,
            help="Upload one or more PDF files to analyze"
        )

        if st.button("Process Documents", type="primary"):
            if pdf_docs:
                with st.spinner("Processing documents..."):
                    st.write("Extracting text...")
                    raw_text = get_pdf_text(pdf_docs)

                    st.write("Splitting into chunks...")
                    text_chunks = get_text_chunks(raw_text)

                    st.write("Creating knowledge base...")
                    vector_store = get_vector_store(text_chunks)

                    st.write("Initializing AI assistant...")
                    st.session_state.conversation = get_conversational_chain(vector_store)

                st.success("✅ Ready! Start asking questions below.")
            else:
                st.warning("Please upload PDF files first.")

    if prompt := st.chat_input("Ask about your documents..."):
        if not st.session_state.conversation:
            st.warning("Please upload and process documents first.")
        else:
            user_input(prompt)

if __name__ == "__main__":
    main()
