import faiss
from time import time
import numpy as np
import importlib
from loguru import logger

from algo.algo_base import AlgoBase

class FaissAlgo(AlgoBase):
    def __init__(self, config) -> None:
        super().__init__(config)
        self.index_folder_name = "faiss_indexes"
        self.embeding_dimensions = int(config["algo"]["embedding_dimensions"])
        self.index_name = config["algo"]["index_name"]
        self.index = None

    def _create_faiss_index(self, dims):
        module = importlib.import_module(
            f'faiss')
        class_ = getattr(module, self.index_name)
        instance = class_(dims)
        return instance
    
    def initialise_index(self, config):
        try:
            self.index = self._create_faiss_index(dims = self.embeding_dimensions)
            data = self.db.get_embeddings(config["event_id"])
            self.add_embeddings(data)
        except Exception as e:
            logger.error(f"Index creation failed : {e}")

    def filter_by_threshold(self, distances, indices, threshold):
        filtered_indices=[]
        filered_distances = []
        for dist, ids in zip(distances[0], indices[0]):
            if dist<threshold:
                filtered_indices.append(ids)
                filered_distances.append(dist)
        return [filered_distances], [filtered_indices]
    
    def search_index(self, query_vector, k, threshold):
        query_vector = np.array(query_vector["embedding"], dtype='float32').reshape(1, -1)

        distances, indices = self.index.search(query_vector, k)
        distances, indices = self.filter_by_threshold(distances, indices, threshold)

        unique_img_ids = [self.img_ids[i] for i in indices[0] if i!=-1]

        return unique_img_ids

    
    def add_embeddings(self, data):
        embeddings = np.array([item['embedding'] for item in data]).astype('float32')
        self.img_ids = [item['file_name'] for item in data]

        assert embeddings.shape[1]==self.embeding_dimensions

        self.index.add(embeddings)

        return {"STATUS": "DONE"}
    
    def download(self, config, files):
        uploaded_files = self.storage.save_image_to_storage({"event_id": "search"}, files)

        self.initialise_index(config)

        results = []
        for file in uploaded_files:
            embeddings = self.model.get_embeddings(file)
            for embedding in embeddings:
                result = self.search_index(embedding, k=config["limit"], threshold=config["threshold"])
                results.extend(result)

        return results


    def upload(self, config, files):
        logger.info("Saving files locally.")
        uploaded_files = self.storage.save_image_to_storage(config, files)
        logger.info("Saving files locally: DONE!!!")

        logger.info("Getting embeddings.")
        final_embeddings = []
        for file in uploaded_files:
            embeddings = self.model.get_embeddings(file)
            for embedding in embeddings:
                embedding = dict(embedding)
                embedding["event_id"] = config["event_id"]
                embedding["file_name"] = file
                embedding["timestamp"] = int(time()*(10**7))
                final_embeddings.append(embedding)
        logger.info("Getting embeddings: DONE!!!")

        self.db.add_embeddings(final_embeddings)
                