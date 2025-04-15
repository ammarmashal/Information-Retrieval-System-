import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  
os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY


def get_text_from_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch the URL: {url}")
    
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove script and style tags
    for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    return text


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
