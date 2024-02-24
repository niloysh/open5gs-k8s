import pymongo
from logger import log

class Open5GS:
    def __init__(self, server, port):
        self.server = server
        self.port = port

    class Unit:
        Kbps = 1
        Mbps = 2
        Gbps = 3
        Tbps = 4

    class Type:
        IPv4 = 1
        IPv6 = 2
        IPv4v6 = 3

    class Status:
        DISABLED = 1
        ENABLED = 2
        

    def connect_to_mongodb(self):
        client = pymongo.MongoClient(f"mongodb://{self.server}:{self.port}/")
        return client["open5gs"]

    def get_subscribers(self):
        db = self.connect_to_mongodb()
        subscribers = db["subscribers"].find()
        return list(subscribers)

    def get_subscriber(self, imsi):
        db = self.connect_to_mongodb()
        subscriber = db["subscribers"].find_one({"imsi": str(imsi)})
        return subscriber

    def add_subscriber(self, sub_data):
        db = self.connect_to_mongodb()
        try:
            result = db["subscribers"].insert_one(sub_data)
            log.debug(f"Added subscriber with ID: {result.inserted_id}")
            return result.inserted_id
        except pymongo.errors.DuplicateKeyError:
            log.warning(f"Subscriber imsi:{sub_data['imsi']} already exists!")
        

    def update_subscriber(self, imsi, sub_data):
        db = self.connect_to_mongodb()
        result = db["subscribers"].update_one({"imsi": str(imsi)}, {"$set": sub_data})
        return result.modified_count > 0

    def delete_subscriber(self, imsi):
        db = self.connect_to_mongodb()
        result = db["subscribers"].delete_many({"imsi": str(imsi)})
        return result.deleted_count
