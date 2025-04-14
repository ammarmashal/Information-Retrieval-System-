import streamlit as st
from src.helper import get_pdf_text, get_text_chunks, get_vector_store, get_conversational_chain
import time
from datetime import datetime, timedelta
import os
# Quota settings
MAX_QUESTIONS = 5  # Set your desired quota limit
QUOTA_RESET_MINUTES = 60  # Reset timer in minutes

# Initialize session state for quota tracking
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
if 'quota_exceeded_time' not in st.session_state:
    st.session_state.quota_exceeded_time = None

def user_input(user_question):
    # Check if quota is exceeded
    if st.session_state.quota_exceeded_time:
        remaining_time = st.session_state.quota_exceeded_time + timedelta(minutes=QUOTA_RESET_MINUTES) - datetime.now()
        if remaining_time.total_seconds() > 0:
            # Create a placeholder for the countdown
            countdown_placeholder = st.empty()
            
            # Update countdown in real-time
            while remaining_time.total_seconds() > 0:
                mins, secs = divmod(int(remaining_time.total_seconds()), 60)
                countdown_placeholder.error(
                    f"⚠️ Question quota exceeded! Please try again in {mins:02d}:{secs:02d}"
                )
                time.sleep(1)
                remaining_time = st.session_state.quota_exceeded_time + timedelta(minutes=QUOTA_RESET_MINUTES) - datetime.now()
            
            # Clear the countdown and reset quota
            countdown_placeholder.empty()
            st.session_state.question_count = 0
            st.session_state.quota_exceeded_time = None
            st.rerun()  # Refresh to enable questions again
        return
    
    # Check current quota
    if st.session_state.question_count >= MAX_QUESTIONS:
        st.session_state.quota_exceeded_time = datetime.now()
        st.error(f"⚠️ You've reached your limit of {MAX_QUESTIONS} questions. Please wait {QUOTA_RESET_MINUTES} minutes before asking more.")
        return
    
    try:
        response = st.session_state.conversation({'question': user_question})
        st.session_state.chatHistory = response['chat_history']
        st.session_state.question_count += 1
        
        # Display conversation
        for i, message in enumerate(st.session_state.chatHistory):
            if i % 2 == 0:
                st.write("User: ", message.content)
            else:
                st.write("Reply: ", message.content)
                
        # Show quota usage
        st.sidebar.write(f"Questions used: {st.session_state.question_count}/{MAX_QUESTIONS}")
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")



def main():
    # Set up the Streamlit app
    # Display quota info in sidebar
    st.set_page_config(page_title="Information Retrieval", page_icon="📑")
    st.title("Information Retrieval System 📑")
    
    # Display quota info in sidebar
    with st.sidebar:
        st.title("Menu:")
        st.write(f"Question quota: {MAX_QUESTIONS} per {QUOTA_RESET_MINUTES} minutes")
        
        # Show animated quota usage
        if 'question_count' in st.session_state:
            quota_meter = st.progress(st.session_state.question_count/MAX_QUESTIONS)
            st.write(f"Used: {st.session_state.question_count}/{MAX_QUESTIONS}")
        
        pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", 
                                    type=["pdf"], accept_multiple_files=True)
        if st.button("Submit & Process"):
            if pdf_docs:
                with st.spinner("Processing..."):
                    raw_text = get_pdf_text(pdf_docs)
                    text_chunks = get_text_chunks(raw_text)
                    vector_store = get_vector_store(text_chunks)
                    st.session_state.conversation = get_conversational_chain(vector_store)
                    st.success("Done")
            else:
                st.error("Please upload at least one PDF file.")
    
    user_question = st.text_input("Ask a Question from the PDF Files only", 
                                placeholder="Type your question here...",
                                key="question_input")    
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chatHistory" not in st.session_state:
        st.session_state.chatHistory = None
        
    if user_question and st.session_state.conversation is not None:
        user_input(user_question)


if __name__ == "__main__":
    main()









