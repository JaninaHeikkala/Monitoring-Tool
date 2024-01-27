import asyncio
import threading
import time
import uvicorn
import httpx
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from bson.json_util import dumps
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from update import fetch_and_store_data_for_all_sites

app = FastAPI()


# MongoDB Connection
DATABASE_URL = "mongodb://mongo:27017"
client = MongoClient(DATABASE_URL)
db = client["monitoring-tool"]
collection = db["data"]

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# External API base URL
EXTERNAL_API_BASE_URL = "https://uptimedemo.jaspnas.dev"

@app.get("/")
async def read_root():
    external_api_url = f"{EXTERNAL_API_BASE_URL}/"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(external_api_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            external_data = response.json()  # Parse JSON response
            print(external_data)
        return external_data
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from {external_api_url}: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error from {external_api_url}: {str(e)}")


@app.get("/fetch_store_site/{site_name}")
async def fetch_store_site(site_name: str):
    external_api_url = f"{EXTERNAL_API_BASE_URL}/site/{site_name}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(external_api_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            external_data = response.json()  # Parse JSON response
            print(external_data)

            result = await collection.insert_one({
                "site": external_data["site"],
                "status": external_data["status"],
                "responsetime": external_data["responsetime"],
                "error": external_data["error"]
            })

        return external_data, {"message": "Data stored in MongoDB", "id": str(result.inserted_id)}
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from {external_api_url}: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error from {external_api_url}: {str(e)}")
    
async def get_mongo_collection():
    return collection

@app.get("/fetch_data_from_db")
async def fetch_data_from_db():
    collection = await get_mongo_collection()

    # Fetch data from the MongoDB collection
    data = collection.find()
    data_json = dumps(data)  # Convert the cursor to JSON format

    return {"data_from_mongo": data_json}

@app.get("/fetch_newest")
async def fetch_newest():
    try:
        all_data = fetch_and_store_data_for_all_sites()
        # Exclude ObjectId from serialization
        serialized_data = [
            {key: value for key, value in item.items() if key != "_id"}
            for item in all_data
        ]
        return JSONResponse(content={"all_data": serialized_data})
    except Exception as e:
        # Catch any exception and return details in the response
        return JSONResponse(content={"error": str(e)}, status_code=500)


uvicorn.run(app, host="0.0.0.0", port=8000, use_colors=False)