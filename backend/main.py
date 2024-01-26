import asyncio
import threading
import time
import uvicorn
import httpx
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()


# MongoDB Connection
DATABASE_URL = "mongodb://mongo:27017"
client = AsyncIOMotorClient(DATABASE_URL)
db = client["monitoring-toool"]
collection = db["data"]


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

loop = asyncio.get_event_loop()

uvicorn.run(app, host="127.0.0.1", port=8000, use_colors=False)