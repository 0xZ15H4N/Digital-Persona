import requests
import json
from dotenv import load_dotenv
import os
import time
load_dotenv()

api_key :str = os.getenv("api_key")

def LinkedIn_scrapper(id:str):

    headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    }

    data = json.dumps({
        "input": [{"url":f"https://www.linkedin.com/in/{id}/"}]
    })

    response = requests.post(
        "https://api.brightdata.com/datasets/v3/scrape?dataset_id=gd_l1viktl72bvl7bjuj0&notify=false&include_errors=true",
        headers=headers,
        data=data
    )

    with open("response.txt", "w") as f:
        json.dump(response.json(), f, indent=4)


def xIdProgress(snapshot_id):
    url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    response = requests.get(url, headers=headers)
    return (response.json())


def requestSnapshot(snapshot_id):

    url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    params = {
        "format": "json",
    }

    response = requests.get(url, headers=headers, params=params)

    return response.json()


def Xcom_scrapper(id:str):
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
    with open("response_x.txt", "a") as f:
        data = json.load(f)

        json.dump(response.json(), f, indent=4)

    with open("snapshot_id.txt","r+") as f:
        data = json.load(f)
        data[id] = snapshot_id
        json.dump(data, f, indent=4)
    
LinkedIn_scrapper("zishan-ansari-307a58189")


