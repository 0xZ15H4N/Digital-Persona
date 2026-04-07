import os
import json
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.llms import Ollama
import google as genai
import uuid
from dotenv import load_dotenv
load_dotenv()
GEMINI_KEY :str = os.getenv("GEMINI_KEY")

# -------------------------------
# 2. CONVERT TO LANGCHAIN DOCS
# -------------------------------

def convert_to_documents(user_info):
    documents = []

    # 🔹 Single text fields
    if "about_user" in user_info:
        documents.append(Document(
            page_content=user_info["about_user"],
            metadata={"type": "about"}
        ))

    if "exp_user" in user_info:
        documents.append(Document(
            page_content=user_info["exp_user"],
            metadata={"type": "experience"}
        ))

    for edu in user_info.get("edu_user",[]):
        documents.append(Document(
            page_content=edu,
            metadata={"type": "education"}
        ))

    for cert in user_info.get("cert_user", []):
        documents.append(Document(
            page_content=cert,
            metadata={"type": "certification"}
        ))

    for act in user_info.get("act_user", []):
        documents.append(Document(
            page_content=act,
            metadata={"type": "activity"}
        ))

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
def ask_gemini(vectorstore, query):
    # 1. Setup Retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    docs = retriever.invoke(query)
    client = genai.Client(api_key=GEMINI_KEY)
    # 2. Build Context (with a fallback if docs is empty)
    if not docs:
        return "I'm sorry, I couldn't find any relevant information in the profile."

    context = "\n\n".join([doc.page_content for doc in docs])

    # 3. Build Prompt safely
    prompt = f"""
    You are an assistant answering questions about a person's profile.
    ONLY use the context below. Do not hallucinate.

    Context:
    {context}

    Question:
    {query}

    Answer:
    """

    # 4. Call Model
    response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=prompt
    )

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


