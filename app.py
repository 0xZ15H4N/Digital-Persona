from flask import Flask, request,jsonify
from flask_cors import CORS
import requests
import json
from dotenv import load_dotenv
import os
import time
from webscapper import xIdProgress , requestSnapshot
from embedding import *
from rag_model import load_chunks,convert_to_documents,create_db
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import uuid
load_dotenv()

api_key :str = os.getenv("api_key")

## create a simple flask application

app = Flask(__name__) ## the argue taken by flask is entry point for flask app
CORS(app)
@app.after_request
def remove_csp(response):
    response.headers.pop("Content-Security-Policy", None)
    return response


@app.route("/api/v1/requestLDdata",methods=["POST"]) # defining a decorator
def getLinkedINdata():
    body = request.get_json()

    if not body or "userID" not in body:
        return jsonify({"error": "userID required"}), 400
 

    id = body["userID"]

    headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    }
    data = json.dumps({
        "input": [{"url":f"https://www.linkedin.com/in/{id}/"}]
    })
    print("going to request data")
    response = requests.post(
        "https://api.brightdata.com/datasets/v3/scrape?dataset_id=gd_l1viktl72bvl7bjuj0&notify=false&include_errors=true",
        headers=headers,
        data=data
    )
    with open("samples/linkedINdata.json","w",encoding="utf-8") as f:
        json.dump(response.json(),f,ensure_ascii=False)
    # Now we will perform chunking on the data recieved
    with open("samples/linkedINdata.json","r",encoding="utf-8") as f:
        data = json.load(f)
    build_chunks(data)
    # chunking
    chunks = load_chunks("userData/")
    # chunks -> documents
    documents = convert_to_documents(chunks)
    # ducuments -> vector DB
    unique_id = create_db(documents)
    return {"status":"ok","userID":unique_id},200








# still under developement
@app.route("/api/v1/requestXcomData",methods=["POST"])
def Xcom_scrapper():

    body = request.get_json()
    if not body or "userID" not in body:
        return jsonify({"error": "userID required"}), 400
 
    id = body["userID"]

    url = "https://api.brightdata.com/datasets/v3/trigger"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    params = {
        "dataset_id": "gd_lwxmeb2u1cniijd7t4",
        "include_errors": "true",
        "type": "discover_new",
        "discover_by": "user_name",
    }
    data = [
        {"user_name":f"{id}"},
    ]

    # request for the data of user and getting snapshot_id as response
    response = requests.post(url, headers=headers, params=params, json=data)
    snapshot_id = response.json()["snapshot_id"]

    # requesting for the status of scraping
    while True:
        status = xIdProgress(snapshot_id)["status"]
        if status == "ready":
            break
        print("Waiting... current status:", status)
        time.sleep(5) 
    # requesting the data Finally!
    response = requestSnapshot(snapshot_id)
    # Storing all the requesting data for later use
    return response



if __name__ == "__main__":
    app.run(debug=True)