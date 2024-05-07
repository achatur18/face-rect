import os
import uuid
from time import time
from typing import List
from fastapi import FastAPI, File, UploadFile, Query
from loguru import logger
import json

from src.config import load_config
from algo.algo_zoo import AlgoRouter
from configs.api_config import *

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
config=load_config(CURRENT_DIR)
logger.info(f"Config: {config}")

algorithm = AlgoRouter().create(config)

app = FastAPI()

@app.post("/registerEvent/")
async def registerEvent(event: Event):
    try:
        response = algorithm.register_event(event)
        return {"status": "DONE", "event_id": response["event_id"]}
    except Exception as e:
        return {"status": "FAILURE", "reason": str(e)}

@app.post("/upload/")
async def create_upload_files(event_id: str = Query(...), files: List[UploadFile] = File(...)):
    try:
        config = {"event_id": event_id}
        response = await algorithm.upload(config, files)
        response["status"] = "DONE"
        return response
    except Exception as e:
        return {"status": "FAILURE", "reason": str(e)}

@app.post("/download/")
async def create_download_files(event_id: str = Query(...), files: List[UploadFile] = File(...), limit: int = 2, threshold: float = 0.4, s3_download=True):
    try:
        config = {"event_id": event_id, "limit": limit, "threshold": threshold, "s3_download": s3_download}
        response = await algorithm.download(config, files)
        response["status"] = "DONE"
        return response
    except Exception as e:
        return {"status": "FAILURE", "reason": str(e)}
    

@app.post("/get_download_link/")
def get_download_link(s3_uri: str = Query(...), expiration: int = 3600):
    try:
        response = algorithm.storage.get_image_download_link(s3_uri, expiration)
        response["status"] = "DONE"
        return response
    except Exception as e:
        return {"status": "FAILURE", "reason": str(e)}
