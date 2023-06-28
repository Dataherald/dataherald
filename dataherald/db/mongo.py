from dataherald.db import DB
from overrides import override
from pymongo import MongoClient
from dataherald.config import System



class MongoDB(DB):
    client: MongoClient

    def __init__(self, system: System):
        #self.client = MongoClient(host, port, user, password, db_name)
        super().__init__(system)
        system.settings.require("db_host")
        system.settings.require("db_port")
        system.settings.require("db_username")
        system.settings.require("db_password")
        system.settings.require("db_name")
        self.data_store = MongoClient(f"mongodb://{system.settings.db_host}:{system.settings.db_port}")[system.settings.db_name]

    