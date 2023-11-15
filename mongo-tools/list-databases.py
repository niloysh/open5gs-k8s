from pymongo import MongoClient
from port_forwarding import run_with_port_forwarding
from logger import log


def get_available_databases():
    client = MongoClient("localhost")
    database_names = client.list_database_names()
    log.info("Available databases:")
    for db_name in database_names:
        log.info(db_name)
    client.close()


if __name__ == "__main__":
    run_with_port_forwarding(get_available_databases)
