import os
from time import time
import shutil

from .storage_base import StorageBase

class LocalStorage(StorageBase):
    def __init__(self, config) -> None:
        super().__init__(config)
        self.bucketName = os.getenv("BUCKET_NAME", "facerect")
        self.uploadFolderName = os.getenv("FOLDER_NAME", "uploaded_images")
        self.upload_img_path = os.path.join(self.bucketName, self.uploadFolderName)
        os.makedirs(self.upload_img_path, exist_ok=True)
        
    def save_image_to_storage(self, config, files):
        DIRECTORY = os.path.join(self.upload_img_path, config["event_id"])
        os.makedirs(DIRECTORY, exist_ok=True)

        uploaded_images = []
        for file in files:
            file_path = os.path.join(DIRECTORY, f"{int(time()*10**7)}_{file.filename}")
            uploaded_images.append(file_path)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        return uploaded_images
