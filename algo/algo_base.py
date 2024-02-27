from time import time
from loguru import logger

from db.db_zoo import DatabaseRouter
from storage.storage_zoo import StorageRouter
from src.face_rect import FaceRec

class AlgoBase:
    def __init__(self, config) -> None:
        self.config = config
        self.db = DatabaseRouter().create(self.config)
        self.storage = StorageRouter().create(self.config)
        self.model = FaceRec()

    def create_eventId(self):
        return f"EVT_{int(time()*(10**7))}"

    def register_event(self, event):
        event_id = self.create_eventId()
        if not self.db.is_event_exist(event_id):
            event = dict(event)
            event["event_id"] = event_id
            self.db.add_event(event)
            return {"event_id": event_id}
        else:
            logger.error("Event collision. event_id already exists. Please retry again!!!")
            raise Exception("Event collision. event_id already exists. Please retry again!!!")
