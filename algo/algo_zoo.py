import importlib

class AlgoRouter:
    def create(self,config):
        try:
            algo_name = config["algo"]["algo_name"]
            class_name = f'{algo_name.capitalize()}Algo'
            module = importlib.import_module(
                f'algo.{algo_name}_algo')
            class_ = getattr(module, class_name)
            instance = class_(config)
            return instance
        except (ImportError, AttributeError):
            raise NotImplementedError(
                f'Algo Backend {algo_name} is not supported')