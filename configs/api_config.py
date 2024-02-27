from pydantic import BaseModel

class Event(BaseModel):
    name: str
    description: str

class UploadImage(BaseModel):
    event_id: str