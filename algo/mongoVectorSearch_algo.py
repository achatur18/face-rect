from time import time
import numpy as np
import importlib
from loguru import logger

from algo.algo_base import AlgoBase

class MongovectorsearchAlgo(AlgoBase):
    def __init__(self, config) -> None:
        super().__init__(config)
        self.index_folder_name = "mongoVectorSearch_indexes"
        self.embeding_dimensions = int(config["algo"]["embedding_dimensions"])
        self.index_name = config["algo"]["index_name"]

    def save_image_to_local(self, config, files):
        local_uploaded_files = self.storage.save_image_to_local(config, files)
        logger.info(f"uploaded_files : {local_uploaded_files}")
        return local_uploaded_files

    def delete_images_from_local(self, local_uploaded_files):
        self.storage.delete_images_from_local(local_uploaded_files)
        logger.info("LOCAL CLEARED!!!")

    def save_embeddings(self, final_embeddings):
        try:
            logger.info("Saving embeddings to DB.")
            self.db.add_embeddings(final_embeddings)
            logger.info("SAVING COMPLETE!!!")
            return True
        except Exception as e:
            logger.info("Couldn't save embeddings!!!")
            return False

    def search_embeddings(self, embedding, config):
        return self.db.search_vector_embeddings(queryVector = embedding, config=config)
    
    def upload_image(self, local_file, config):
        return self.storage.upload_image(local_file, config)
    
    def get_embeddings(self, local_file):
        return self.model.get_embeddings(local_file)

    def get_results_list(self, config, local_uploaded_files):
        results = []
        for file in local_uploaded_files:
            embeddings = self.get_embeddings(file)
            for embedding in embeddings:
                result = self.search_embeddings(embedding, config)
                results.extend(result)
        final_results = list(set(results))
        if config["s3_download"]:
            s3_uris = self.storage.make_s3_uris(final_results)
            final_results = [self.storage.get_image_download_link(key)["response"] for key in final_results]
        return final_results
    
    def get_embeddings_list(self, config, local_uploaded_files):
        logger.info("Getting embeddings.")
        final_embeddings = []
        for local_file in local_uploaded_files:
            embeddings = self.get_embeddings(local_file)
            storage_uploaded_files = self.upload_image(local_file, config)
            for embedding in embeddings:
                embedding = dict(embedding)
                embedding["event_id"] = config["event_id"]
                embedding["file_name"] = storage_uploaded_files
                embedding["timestamp"] = int(time()*(10**7))
                final_embeddings.append(embedding)
        return final_embeddings

    
    async def download(self, config, files):
        config["index_name"] = self.index_name
        local_uploaded_files = self.save_image_to_local({"event_id": "search"}, files)
        results = self.get_results_list(config, local_uploaded_files)
        self.delete_images_from_local(local_uploaded_files)
        return {
            "results": results,
            "total_images": len(local_uploaded_files)
        }

    async def upload(self, config, files):
        local_uploaded_files = self.save_image_to_local(config, files)
        final_embeddings = self.get_embeddings_list(config, local_uploaded_files)
        save_embeddings = self.save_embeddings(final_embeddings)
        self.delete_images_from_local(local_uploaded_files)
        return {
            "save_embeddings": save_embeddings,
            "total_embeddings": len(final_embeddings)
        }
                