from ruamel.yaml import YAML
from open5gs import Open5GS
from port_forwarding import run_with_port_forwarding
from logger import log

MONGO_URI = "localhost"
MONGO_PORT = 27017
DATA_DIR = "data"

yaml = YAML()


def list_subscriber():
    Open5GS_1 = Open5GS(MONGO_URI, MONGO_PORT)
    subscriber_list = Open5GS_1.get_subscribers()

    with open(DATA_DIR + "/subscribers.yaml", "r") as file:
        subscribers = yaml.load(file.read())

    for subscriber_info in subscriber_list:
        imsi = subscriber_info["imsi"]
        subscriber_name = None

        # Search for the IMSI in the subscriber_data dictionary
        for name, data in subscribers.items():
            if data.get("imsi") == imsi:
                subscriber_name = name
                break

        if subscriber_name:
            log.info(subscriber_name)
        else:
            log.warning(f"Subscriber not found for IMSI {imsi}")


if __name__ == "__main__":
    run_with_port_forwarding(list_subscriber)
