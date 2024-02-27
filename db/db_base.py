

class DBBase:
    def __init__(self, config) -> None:
        self.db_name = config["db"]["dbname"]
        self.embedding_table_name = config["db"]["embedding_table"]
        self.config_table_name = config['db']["config_table"]
        self.events_table_name = config['db']["events_table"]