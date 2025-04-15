import streamlit as st
from src.helper import get_pdf_text, get_text_chunks, get_vector_store, get_conversational_chain, get_text_from_url
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime, timedelta
import time

# Quota settings
MAX_QUESTIONS = 10
QUOTA_RESET_MINUTES = 60

# Session state
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
if 'quota_exceeded_time' not in st.session_state:
    st.session_state.quota_exceeded_time = None
if 'last_user_question' not in st.session_state:
    st.session_state.last_user_question = None
if 'last_ai_answer' not in st.session_state:
    st.session_state.last_ai_answer = None

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
        with st.spinner("Analyzing your question..."):
            response = st.session_state.conversation({'question': user_question})
            st.session_state.chatHistory = response['chat_history']
            st.session_state.question_count += 1
            st.session_state.last_user_question = user_question
            st.session_state.last_ai_answer = response['answer']

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
    st.set_page_config(
        page_title="PDF & Web Insight Pro",
        page_icon="🌐",
        layout="centered"
    )

    st.title("📚 Web & PDF Insight Pro")
    st.caption("Ask AI about your PDFs or webpages!")

    with st.sidebar:
        st.header("Settings")
        st.metric("Question Quota", f"{MAX_QUESTIONS} per hour")

        if 'question_count' in st.session_state:
            st.progress(st.session_state.question_count / MAX_QUESTIONS)
            st.caption(f"Used: {st.session_state.question_count}/{MAX_QUESTIONS}")

        # === ✅ PDF Upload ===
        pdf_docs = st.file_uploader(
            "Upload PDFs", 
            type=["pdf"], 
            accept_multiple_files=True,
            help="Upload one or more PDF files to analyze"
        )
        if st.button("Process PDF", type="primary"):
            if pdf_docs:
                with st.status("Processing PDF...", expanded=True) as status:
                    st.write("Extracting text...")
                    raw_text = get_pdf_text(pdf_docs)

                    st.write("Splitting into chunks...")
                    text_chunks = get_text_chunks(raw_text)

                    st.write("Creating knowledge base...")
                    vector_store = get_vector_store(text_chunks)

                    st.write("Initializing AI engine...")
                    st.session_state.conversation = get_conversational_chain(vector_store)

                    status.update(label="PDF processing complete!", state="complete")
                    st.success("Ready for questions!")
            else:
                st.warning("Please upload PDF files first.")

        # === ✅ Webpage Analysis ===
        st.divider()
        st.markdown("### 🌐 Analyze a Webpage")
        web_url = st.text_input("Enter a webpage URL (e.g. https://...)")
        if st.button("Process Webpage", type="primary", key="web_process"):
            if web_url:
                with st.status("Processing webpage...", expanded=True) as status:
                    st.write("Fetching content...")
                    web_text = get_text_from_url(web_url)

                    st.write("Splitting into chunks...")
                    text_chunks = get_text_chunks(web_text)

                    st.write("Creating knowledge base...")
                    vector_store = get_vector_store(text_chunks)

                    st.write("Initializing AI engine...")
                    st.session_state.conversation = get_conversational_chain(vector_store)

                    status.update(label="Webpage processing complete!", state="complete")
                    st.success("Ready to ask questions!")
            else:
                st.warning("Please enter a valid URL.")

    # === Main Chat Interface ===
    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    if prompt := st.chat_input("Ask about your documents or webpage..."):
        if not st.session_state.conversation:
            st.warning("Please process a PDF or webpage first.")
        else:
            user_input(prompt)

if __name__ == "__main__":
    main()
