import importlib

class StorageRouter:
    @staticmethod
    def create(config):
        try:
            storage_type = config["storage"]["storagetype"]
            class_name = f'{storage_type.capitalize()}Storage'
            module = importlib.import_module(
                f'storage.{storage_type}_storage')
            class_ = getattr(module, class_name)
            instance = class_(config)
            return instance
        except (ImportError, AttributeError):
            raise NotImplementedError(
                f'Storage Backend {storage_type} is not supported')