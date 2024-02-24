from bson.objectid import ObjectId
from open5gs import Open5GS
from port_forwarding import run_with_port_forwarding
from logger import log
import argparse
import json
from functools import partial

MONGO_URI = "localhost"
MONGO_PORT = 27017
DATA_DIR = "../data"


def add_subscribers(subscriber_names: list):
    with open(DATA_DIR + "/subscribers.json", "r") as file:
        configured_subscribers = json.loads(file.read())

    Open5GS_1 = Open5GS(MONGO_URI, MONGO_PORT)
    subscribers_in_db = Open5GS_1.get_subscribers()
    subscriber_imsis = [subscriber["imsi"] for subscriber in subscribers_in_db]

    if not subscriber_names:
        subscriber_names = configured_subscribers.keys()

    for subscriber_name in subscriber_names:
        subscriber_info = configured_subscribers.get(subscriber_name)
        if not subscriber_info:
            log.warning(f"Subscriber {subscriber_name} not found in the configuration file.")
            continue

        imsi = subscriber_info["imsi"]
        if imsi in subscriber_imsis:
            log.warning(f"Subscriber {subscriber_name} already exists in the database.")
            continue
        
        subscriber_info["_id"] = ObjectId()
        Open5GS_1.add_subscriber(subscriber_info)
        log.info(f"Added {subscriber_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add or delete subscribers.")
    parser.add_argument("subscriber_names", nargs="*", help="Names of the subscribers to add.")
    args = parser.parse_args()
    run_with_port_forwarding(partial(add_subscribers, args.subscriber_names))
    