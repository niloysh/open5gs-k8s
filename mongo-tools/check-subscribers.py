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
    imsi_list = []

    for subscriber_info in subscriber_list:
        imsi = subscriber_info["imsi"]
        imsi_list.append(imsi)

    if not imsi_list:
        print("No subscribers found. Please add subscribers.")
    else:
        print(f"Subscribers: {imsi_list}")

if __name__ == "__main__":
    run_with_port_forwarding(list_subscriber)
