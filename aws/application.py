from flask import Flask, request,jsonify,g
from flask_cors import CORS
import requests
import json
from dotenv import load_dotenv
import os
from utils.embedding import *
from utils.rag_model import *
from functools import wraps
from langchain_community.embeddings import HuggingFaceEmbeddings
import shutil
load_dotenv()

api_key :str = os.getenv("API_KEY")
vectorstore = None

app = Flask(__name__)
CORS(app)

def get_embedding_model():
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        print("Model loaded ✅")
        return embedding_model

    
embedding_model = get_embedding_model()
@app.route("/api/v1/requestLDdata",methods=["POST"])
def main():
    body = request.get_json()

    if not body or "userID" not in body:
        return jsonify({"error": "userID required"}), 400
    user_id = body["userID"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "input": [{"url": f"https://www.linkedin.com/in/{user_id}/"}]
    }
    response = requests.post(
        "https://api.brightdata.com/datasets/v3/scrape?dataset_id=gd_l1viktl72bvl7bjuj0&notify=false&include_errors=true",
        headers=headers,
        json=data
    )
    data = response.json()
    return {"status":"ok","data":data},200

@app.route("/api/v1/createChunks",methods=["POST"])
def createChunks():
    data = request.get_json()
    response = build_chunks(data["data"])
    return response

@app.route("/api/v1/createDB",methods=["POST"])
def createDocuments():
    chunks = request.get_json()["chunks"]
    documents = convert_to_documents(chunks)
    vector_id = create_db(documents=documents,embedding_model=embedding_model)
    print(vector_id)
    return {"status":"ok","vector_id":vector_id},200

@app.route("/api/v1/loadVD",methods=["POST"])
def loadVD():
    global vectorstore
    vector_id = request.get_json()["vector_id"]
    if vector_id == None:
        return {"status":"Vector Id not recieved"},500
    directory = "db/chroma_db/" + vector_id
    vectorstore = load_db(directory,embedding_model)
    if(vectorstore==None):
        return {"status":"Failed","response":"Internal Server Error"},500
    return {"status":"ok"},200
    
@app.route("/api/v1/chat",methods=["POST"])
def chat():
    query = request.get_json()["query"]
    answer = ask_gemini(vectorstore,query) # local llama model replace with gemini   ask_gemini(vectorstore,query) ask_question(vectorstore, query)
    return {"status":"ok","response":answer},200
    
@app.route("/api/v1/exit-chat",methods=["POST"])
def delete_exit():
    vector_id = request.get_json()["vector_id"]
    print(vector_id)
    vectorstore._client._system.stop()
    try:
        shutil.rmtree("db/chroma_db/"+vector_id)
    except Exception as e:
        print(e)
        return {"status":"failed","reason":str(e)},500
    return {"status":"ok"},200
    
@app.route("/",methods=["GET"])
def health():
    return {"status":"OK"},200
if __name__ == "__main__":
    print("App running at http://localhost:5000/")
    app.run(debug=False,host="0.0.0.0")