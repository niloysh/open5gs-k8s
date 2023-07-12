from bson.objectid import ObjectId
from open5gs import Open5GS
from port_forwarding import run_with_port_forwarding
from data import sub_data

MONGO_URI = "localhost"
MONGO_PORT = 27017

def add_subscriber():
    subscribers = ["subscriber_1", "subscriber_2"]
    for subscriber in subscribers:
        Open5GS_1 = Open5GS(MONGO_URI, MONGO_PORT)
        sub_data[subscriber]["_id"] = ObjectId()
        Open5GS_1.add_subscriber(sub_data[subscriber])

if __name__ == "__main__":
    run_with_port_forwarding(add_subscriber)
