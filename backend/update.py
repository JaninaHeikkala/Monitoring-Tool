from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import httpx
import asyncio
import threading
import time
import uvicorn
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo import MongoClient
from datetime import datetime

# MongoDB Connection
DATABASE_URL = "mongodb://mongo:27017"
client = MongoClient(DATABASE_URL)
db = client["monitoring-toool"]
collection = db["data"]

# External API base URL
EXTERNAL_API_BASE_URL = "https://uptimedemo.jaspnas.dev"

def fetch_and_store_data_for_all_sites():
    # Fetch the list of sites from the root URL
    root_url = f"{EXTERNAL_API_BASE_URL}/"
    try:
        response = requests.get(root_url)
    except Exception as ex:
        print(ex)
    sites_data = response.json()
    # Fetch and store data for each site
    for site_data in sites_data:
        site_name = site_data.get("site")
        try:
            response = requests.get(f"{root_url}site/{site_name}")
            external_data = response.json()

            if external_data["status"] == "down":
                result = collection.insert_one({
                    "site": external_data["site"],
                    "status": external_data["status"],
                    "responsetime": external_data["responsetime"],
                    "error": external_data["error"],
                    "time": datetime.now()
                })
                print("stored one: ", result)

        except Exception as ex:
            print(ex)
        
    print("stored all")

while True:
    fetch_and_store_data_for_all_sites()
    time.sleep(60)