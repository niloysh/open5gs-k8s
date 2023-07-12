import bson
from open5gs import Open5GS
from port_forwarding import run_with_port_forwarding

MONGO_URI = "localhost"
MONGO_PORT = 27017

def list_subscriber():

    Open5GS_1 = Open5GS(MONGO_URI, MONGO_PORT)
    subscriber_list = Open5GS_1.get_subscribers()
    for subscribers in subscriber_list:
        print(subscribers['imsi'])

if __name__ == "__main__":
    run_with_port_forwarding(list_subscriber)
