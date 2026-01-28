import os
import pandas as pd
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA

load_dotenv('keys.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def setup_rag_pipeline():
    print("Loading data...")
    df = pd.read_csv('all_subtitles.csv')
    df['text'] = df['text'].fillna('') # Fill NaN values in 'text' column

    # Combine date, timestamp, and text for context
    df['full_content'] = "Date: " + df['date'].astype(str) + "\nTimestamp: " + df['timestamp'].astype(str) + "\nContent: " + df['text'].astype(str)

    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=400,
        length_function=len,
    )

    # Split documents
    print("Splitting documents...")
    texts = text_splitter.create_documents(df['text'].tolist())

    # Initialize OpenAI embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    if os.path.exists("./chroma_db"):
        print("Loading existing vector store...")
        vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
        print("Vector store loaded successfully.")
    else:
        print("Creating new vector store and embeddings. This may take a while...")
        vectorstore = Chroma.from_documents(texts, embeddings, persist_directory="./chroma_db")
        print("Persisting vector store...")
        vectorstore.persist()
        print("Vector store created successfully.")

    # Initialize the LLM
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0, openai_api_key=OPENAI_API_KEY)
    
    # Create the RAG chain
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vectorstore.as_retriever(),
        return_source_documents=True
    )

    return qa_chain

def ask_question(qa_chain, question):
    result = qa_chain.invoke({"query": question})
    return result


