import os
import json
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.llms import Ollama
import google.generativeai as genai
import uuid
from dotenv import load_dotenv
load_dotenv()
GEMINI_KEY :str = os.getenv("GEMINI_KEY")

# -------------------------------
# 1. LOAD CHUNKS (your JSON)
# -------------------------------

def load_chunks(docs_path):
    documents = []

    for root, dirs, files in os.walk(docs_path):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()

                        if content:  # skip empty files
                            documents.append({
                                "text": content,
                                "source": file_path
                            })

                except Exception as e:
                    print(f"❌ Skipping {file_path}: {e}")
    return documents


# -------------------------------
# 2. CONVERT TO LANGCHAIN DOCS
# -------------------------------

def convert_to_documents(chunks):
    documents = []

    for c in chunks:
        metadata = {k: v for k, v in c.items() if k != "text"}

        doc = Document(
            page_content=c["text"],
            metadata=metadata
        )

        documents.append(doc)
    return documents


# -------------------------------
# 3. CREATE / LOAD CHROMA DB
# -------------------------------

def load_db(persist_directory,embedding_model):

    if os.path.exists(persist_directory):
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model
        )
        count = vectorstore._collection.count()
        if count > 0:
            return vectorstore


def create_db(documents,embedding_model ,persist_directory="db/chroma_db/"):


    # 🚀 Create fresh DB
    unique_id = str(uuid.uuid4())

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=persist_directory+unique_id
    )
    return unique_id

# -------------------------------
# 4. QUERY FUNCTION (RAG)
# -------------------------------
def ask_gemini(vectorstore,query):
    # 🔥 Retriever with optional filters
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 5
        }
    )

    docs = retriever.invoke(query)
    # Build context
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"""
    You are an assistant answering questions about a person's profile.
     ONLY use the context below. Do not hallucinate.
     Context:
     {context}
     Question:
     {query}
     Answer:
    """
    genai.configure(api_key=GEMINI_KEY)
    # Gemini 1.5 Flash is great for RAG due to speed/cost 
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text
    



llm = Ollama(model="llama3")
def ask_question(vectorstore, query):

    # 🔥 Retriever with optional filters
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 5
        }
    )

    docs = retriever.invoke(query)


    # Build context
    context = "\n\n".join([doc.page_content for doc in docs])

    # Local LLM (Ollama)

    prompt = f"""
    You are an assistant answering questions about a person's profile.

    ONLY use the context below. Do not hallucinate.

    Context:
    {context}

    Question:
    {query}

    Answer:
"""

    response = llm.invoke(prompt)
    return response


