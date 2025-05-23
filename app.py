import streamlit as st
from src.helper import get_pdf_text, get_text_chunks, get_vector_store, get_conversational_chain
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

            # Display conversation with improved styling
            for i, message in enumerate(st.session_state.chatHistory):
                if i % 2 == 0:
                    # User question styling
                    st.markdown(
                        f"""
                        <div style='background-color: #e8f4ff; padding: 15px; border-radius: 10px; margin: 10px 0; border: 1px solid #cce7ff;'>
                            <strong>👤 User:</strong> {message.content}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    # Assistant answer styling
                    st.markdown(
                        f"""
                        <div style='background-color: #f6ffed; padding: 15px; border-radius: 10px; margin: 10px 0; border: 1px solid #b7eb8f;'>
                            <strong>🤖 Assistant:</strong> {message.content}
                        </div>
                        """,
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

        if 'question_count' in st.session_state:
            st.progress(st.session_state.question_count / MAX_QUESTIONS)
            st.caption(f"Used: {st.session_state.question_count}/{MAX_QUESTIONS}")

        st.subheader("Upload Documents")
        pdf_docs = st.file_uploader(
            "Upload PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload one or more PDF files to analyze"
        )

        process_btn = st.button("Process Documents", type="primary")

        if st.button("🗑️ Reset Chat", type="secondary"):
            for key in ["conversation", "chatHistory", "question_count", "quota_exceeded_time", "last_user_question", "last_ai_answer"]:
                st.session_state.pop(key, None)
            st.success("Conversation reset successfully!")
            st.rerun()

    if process_btn:
        if pdf_docs:
            with st.status("Processing documents...", expanded=True) as status:
                st.write("Extracting text...")
                raw_text, pdf_info = get_pdf_text(pdf_docs)
                for info in pdf_info:
                    st.write(f"📄 **{info['name']}** - {info['pages']} pages")

                st.write("Chunking content...")
                text_chunks = get_text_chunks(raw_text)

                st.write("Generating document summary...")
                summary_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.3)
                summary_prompt = f"Summarize the following text in less than 150 words:\n{text_chunks[0][:4000]}"
                summary = summary_llm.invoke(summary_prompt)
                st.info("📄 **Document Summary:**\n" + summary.content)

                st.write("Creating knowledge base...")
                vector_store = get_vector_store(text_chunks)

                st.write("Initializing AI engine...")
                st.session_state.conversation = get_conversational_chain(vector_store)

                status.update(label="Processing complete!", state="complete")
                st.success("Ready for questions!")

        else:
            st.warning("Please upload PDF files first")

    if "conversation" not in st.session_state or st.session_state.conversation is None:
        st.info("👆 Upload and process PDF files to begin.")
    else:
        if prompt := st.chat_input("Ask about your documents..."):
            user_input(prompt)

        if st.session_state.last_user_question and st.session_state.last_ai_answer:
            st.markdown("### Last Q&A")
            st.markdown(f"**🧑‍💻 Question:** {st.session_state.last_user_question}")
            st.markdown(f"**🤖 Answer:** {st.session_state.last_ai_answer}")

if __name__ == "__main__":
    main()
