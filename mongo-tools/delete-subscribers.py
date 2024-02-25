from bson.objectid import ObjectId
from open5gs import Open5GS
from port_forwarding import run_with_port_forwarding
from logger import log
import argparse
from ruamel.yaml import YAML
from functools import partial

MONGO_URI = "localhost"
MONGO_PORT = 27017
DATA_DIR = "../data"

yaml = YAML()


def delete_subscribers(subscriber_names: list):
    with open(DATA_DIR + "/subscribers.yaml", "r") as file:
        configured_subscribers = yaml.load(file.read())

    Open5GS_1 = Open5GS(MONGO_URI, MONGO_PORT)
    subscribers_in_db = Open5GS_1.get_subscribers()
    imsis_in_db = [subscriber["imsi"] for subscriber in subscribers_in_db]

    if not subscriber_names:
        subscriber_imsis = imsis_in_db

    else:
        subscriber_imsis = []
        for subscriber_name in subscriber_names:
            subscriber_info = configured_subscribers.get(subscriber_name)
            if subscriber_info:
                subscriber_imsis.append(subscriber_info["imsi"])
            else:
                log.warning(f"Subscriber {subscriber_name} not found in the configuration file.")


    for imsi in subscriber_imsis:
        if imsi not in imsis_in_db:
            log.warning(f"Subscriber with IMSI {imsi} not found in the database.")
            continue
        Open5GS_1.delete_subscriber(imsi)
        log.info(f"Deleted {imsi}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete subscribers.")
    parser.add_argument("subscriber_names", nargs="*", help="Names of the subscribers to delete.")
    args = parser.parse_args()
    run_with_port_forwarding(partial(delete_subscribers, args.subscriber_names))

    
