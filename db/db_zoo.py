import importlib

class DatabaseRouter:
    def create(self, config):
        try:
            db_type = config["db"]["dbtype"]
            class_name = f'{db_type.capitalize()}DB'
            module = importlib.import_module(
                f'db.{db_type}_db')
            class_ = getattr(module, class_name)
            instance = class_(config)
            return instance
        except (ImportError, AttributeError):
            raise NotImplementedError(
                f'Database Backend {db_type} is not supported')