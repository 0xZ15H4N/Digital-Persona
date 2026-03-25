import os
import json
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.llms import Ollama
import uuid
from flask import Flask,request
from flask_cors import CORS
import shutil
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)


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

    print(f"✅ Loaded {len(documents)} files")
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

    print(f"✅ Converted to {len(documents)} documents")
    return documents


# -------------------------------
# 3. CREATE / LOAD CHROMA DB
# -------------------------------

def load_db(persist_directory):
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    if os.path.exists(persist_directory):
        print("🔍 Checking existing DB...")
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model
        )

        count = vectorstore._collection.count()
        print(f"📦 Existing DB has {count} documents")

        if count > 0:
            print("✅ Using existing DB")
            return vectorstore
        else:
            print("⚠️ Empty DB found → rebuilding...")


def create_db(documents, persist_directory="db/chroma_db/"):

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # 🚀 Create fresh DB
    unique_id = str(uuid.uuid4())
    print("🚀 Creating new Chroma DB...")
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=persist_directory+unique_id
    )

    print(f"✅ DB created with {len(documents)} documents")
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

    print("\n🔎 Retrieved Chunks:\n")
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
    GEMINI_KEY :str = os.getenv("GEMINI_KEY")
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

    print("\n🔎 Retrieved Chunks:\n")
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


# -------------------------------
# 5. MAIN
# -------------------------------
vectorstore = None
@app.route("/model/v1/loadVD",methods=["POST"])
def loadVD():
    print("=== LOCAL RAG SYSTEM ===\n")
    data = request.get_json()
    directory = "db/chroma_db/" + data["userID"]
    global vectorstore 
    vectorstore = load_db(directory)
    if(vectorstore!=None):
        return {"status":"ok","response":"vectore DB loaded successfully"},200
    else:
        return {"status":"Failed","response":"Internal Server Error"},500

@app.route("/model/v1/query",methods=["POST"])
def ask():
        query = request.get_json()["query"]
        answer = ask_gemini(vectorstore,query) # ask_question(vectorstore, query) local llama model replace with gemini
        return {"status":"ok","response":answer},200


@app.route("/model/v1/exit-chat",methods=["POST"])
def delete_exit():
    vector_id = request.get_json()["vector_id"]
    shutil.rmtree("db/chroma_db/"+vector_id)
    return {"status":"ok"},200
    

if __name__ == "__main__":
    app.run(port=5001)