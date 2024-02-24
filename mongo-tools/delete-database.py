from pymongo import MongoClient
from port_forwarding import run_with_port_forwarding
from logger import log
from functools import partial
import argparse


def delete_database(db_name):
    client = MongoClient("localhost")
    try:
        if db_name in client.list_database_names():
            client.drop_database(db_name)
            log.info(f"Database '{db_name}' has been deleted.")
        else:
            log.info(f"Database '{db_name}' does not exist.")
    except Exception as e:
        log.error(f"An error occurred while trying to delete the database '{db_name}': {e}")
    finally:
        client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete a database.")
    parser.add_argument("db_name", help="Name of the database to delete.")
    args = parser.parse_args()
    run_with_port_forwarding(partial(delete_database, args.db_name))