"""
Write data to an InfluxDB instance
"""
from pymongo import MongoClient
from openpipe.pipeline.engine import ActionRuntime


class Action(ActionRuntime):

    required_config = """
    db_name:                # DB Name
    collection:             # Collection name
    """

    optional_config = """
    url: localhost:27017    # URL of the mongodb instance
    buffer_size: 100        # How many request to batch for inserts
    item: $_$               # The item to be inserted
    """

    def on_start(self, config):
        self.client = client = MongoClient('mongodb://%s/' % config['url'])
        db = client[config['db_name']]
        self._collection = db[config['collection']]
        self.buffer_size = config["buffer_size"]
        self.data_buffer = []

    def on_input(self, item):
        data_buffer = self.data_buffer
        data_buffer.append(item)
        if len(data_buffer) == self.buffer_size:
            self.flush_buffer()

    def on_finish(self, reason):
        self.flush_buffer()

    def flush_buffer(self):
        self._collection.insert(self.data_buffer)
        self.data_buffer = []
