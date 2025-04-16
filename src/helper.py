
import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  
os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY

def get_pdf_text(pdf_docs):    
    text = ""
    pdf_info = []
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        file_text = ""
        for page in pdf_reader.pages:
            file_text += page.extract_text()
        text += file_text
        pdf_info.append({"name": pdf.name, "pages": len(pdf_reader.pages)})
    return text, pdf_info

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    return vector_store

def get_conversational_chain(vector_store):
    prompt_template = """
    You are an expert document analysis assistant. Follow these guidelines:

    1. Answer strictly based on the provided context
    2. If unsure, say "يا عم اسأل سؤال في الفايل مش عاوزين وجع دماغ "
    3. Structure your response:
        - Direct answer first
        - Supporting evidence from document
        - Page reference if available

    Context: {context}
    Question: {question}

    Provide a concise, accurate response:
    """
    
    QA_PROMPT = PromptTemplate.from_template(prompt_template)
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",
        temperature=0.2,
        convert_system_message_to_human=True
    )
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key='answer'
    )
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
        return_source_documents=True,
        verbose=False
    )
    return conversation_chain

def summarize_content(text):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
    prompt = f"Summarize the following document:\n{text[:4000]}"
    response = llm.invoke(prompt)
    return response.content

def extract_keywords(text):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
    prompt = f"Extract the top 10 keywords from the following text:\n{text[:4000]}"
    response = llm.invoke(prompt)
    return response.content

def get_agent_with_tools(vector_store, full_text):
    tools = [
        Tool.from_function(
            name="summarize_document",
            func=lambda q: summarize_content(full_text),
            description="Use this tool to generate a summary of the document"
        ),
        Tool.from_function(
            name="extract_keywords",
            func=lambda q: extract_keywords(full_text),
            description="Use this tool to extract important keywords from the document"
        ),
        Tool.from_function(
            name="ask_question_from_vectorstore",
            func=lambda q: get_conversational_chain(vector_store).invoke({'question': q})['answer'],
            description="Use this tool to answer questions from document context"
        )
    ]

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.2)
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )
    return agent
