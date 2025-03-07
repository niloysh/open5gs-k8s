from open5gs import Open5GS
from collections import defaultdict
from logger import log
from ruamel.yaml import YAML
import argparse

yaml = YAML()

######################### CONFIGURATION ###################################
DEFAULT_CONFIG = {
    "NUM_SLICES": 2,  # Number of network slices to create
    "NUM_COTS_SUBSCRIBERS": 0,  # Number of COTS subscribers
    "NUM_SAMPLE_SUBSCRIBERS": 2,  # Number of simulated subscribers
    "NUM_AUTO_GENERATED_SUBSCRIBERS": 0,  # Number of auto-generated subscribers (for MSD deployment only)
    "DEFAULT_UPLINK_SPEED": {"value": 1, "unit": Open5GS.Unit.Gbps},
    "DEFAULT_DOWNLINK_SPEED": {"value": 1, "unit": Open5GS.Unit.Gbps},
    "DEFAULT_QOS_INDEX": 9,
    "DEFAULT_ARP_VALUES": {
        "priority_level": 8,
        "pre_emption_capability": Open5GS.Status.DISABLED,
        "pre_emption_vulnerability": Open5GS.Status.DISABLED,
    },
    "DEFAULT_KEY": "465B5CE8B199B49FAA5F0A2EE238A6BC",
    "DEFAULT_OPC": "E8ED289DEBA952E4283B54E88E6183CA",
    "DATA_DIR": "data",
    "SLICE_FILE_PATH": "data/slices.yaml",
    "SUBSCRIBER_FILE_PATH": "data/subscribers.yaml"
}

######################### DATA STRUCTURES #################################
# Example slice and subscriber data for testing.
slice_data = {
    "slice_1": {
        "sst": 1,
        "sd": "000001",
        "default_indicator": True,
        "session": [
            {
                "name": "internet",
                "type": Open5GS.Type.IPv4,
                "pcc_rule": [],
                "ambr": {
                    "uplink": {"value": 1, "unit": Open5GS.Unit.Gbps},
                    "downlink": {"value": 1, "unit": Open5GS.Unit.Gbps},
                },
                "qos": {
                    "index": 9,
                    "arp": {
                        "priority_level": 8,
                        "pre_emption_capability": Open5GS.Status.DISABLED,
                        "pre_emption_vulnerability": Open5GS.Status.DISABLED,
                    },
                },
            }
        ],
    },
    "slice_2": {
        "sst": 2,
        "sd": "000002",
        "default_indicator": True,
        "session": [
            {
                "name": "streaming",
                "type": Open5GS.Type.IPv4,
                "pcc_rule": [],
                "ambr": {
                    "uplink": {"value": 1, "unit": Open5GS.Unit.Gbps},
                    "downlink": {"value": 1, "unit": Open5GS.Unit.Gbps},
                },
                "qos": {
                    "index": 7,
                    "arp": {
                        "priority_level": 8,
                        "pre_emption_capability": Open5GS.Status.DISABLED,
                        "pre_emption_vulnerability": Open5GS.Status.DISABLED,
                    },
                },
            }
        ],
    },
}
simulated_subscriber_data = {
    "subscriber_1": {
        "_id": "",
        "imsi": "001010000000001",
        "subscribed_rau_tau_timer": 12,
        "network_access_mode": 0,
        "subscriber_status": 0,
        "access_restriction_data": 32,
        "slice": [slice_data["slice_1"]],
        "ambr": {
            "uplink": {"value": 1, "unit": Open5GS.Unit.Gbps},
            "downlink": {"value": 1, "unit": Open5GS.Unit.Gbps},
        },
        "security": {
            "k": "465B5CE8B199B49FAA5F0A2EE238A6BC",
            "amf": "8000",
            "op": None,
            "opc": "E8ED289DEBA952E4283B54E88E6183CA",
        },
        "schema_version": 1,
        "__v": 0,
    },
    "subscriber_2": {
        "_id": "",
        "imsi": "001010000000002",
        "subscribed_rau_tau_timer": 12,
        "network_access_mode": 0,
        "subscriber_status": 0,
        "access_restriction_data": 32,
        "slice": [slice_data["slice_2"]],
        "ambr": {
            "uplink": {"value": 1, "unit": Open5GS.Unit.Gbps},
            "downlink": {"value": 1, "unit": Open5GS.Unit.Gbps},
        },
        "security": {
            "k": "B199B49F465B5CE8E238A6BCAA5F0A2E",
            "amf": "8000",
            "op": None,
            "opc": "283B54E8E8ED289D8E6183CAEBA952E4",
        },
        "schema_version": 1,
        "__v": 0,
    },
    "subscriber_3": {
        "_id": "",
        "imsi": "001010000000003",
        "subscribed_rau_tau_timer": 12,
        "network_access_mode": 0,
        "subscriber_status": 0,
        "access_restriction_data": 32,
        "slice": [slice_data["slice_1"]],
        "ambr": {
            "uplink": {"value": 1, "unit": Open5GS.Unit.Gbps},
            "downlink": {"value": 1, "unit": Open5GS.Unit.Gbps},
        },
        "security": {
            "k": "465B5CE8B199B49FAA5F0A2EE238A6BD",
            "amf": "8000",
            "op": None,
            "opc": "E8ED289DEBA952E4283B54E88E6183CB",
        },
        "schema_version": 1,
        "__v": 0,
    },
}
cots_subscriber_data = {
    "pixel_1": {
        "_id": "",
        "imsi": "001010000060592",
        "subscribed_rau_tau_timer": 12,
        "network_access_mode": 0,
        "subscriber_status": 0,
        "access_restriction_data": 32,
        "slice": [slice_data["slice_1"]],
        "ambr": {
            "uplink": {"value": 1, "unit": Open5GS.Unit.Gbps},
            "downlink": {"value": 1, "unit": Open5GS.Unit.Gbps},
        },
        "security": {
            "k": "1B9DC14B6E16A8FE83AA0E8A0AB56FCB",
            "amf": "8000",
            "op": None,
            "opc": "8CD505786285C50FEC35AD9D328816EA",
        },
        "schema_version": 1,
        "__v": 0,
    },
    "pixel_2": {
        "_id": "",
        "imsi": "001010000060594",
        "subscribed_rau_tau_timer": 12,
        "network_access_mode": 0,
        "subscriber_status": 0,
        "access_restriction_data": 32,
        "slice": [slice_data["slice_2"]],
        "ambr": {
            "uplink": {"value": 1, "unit": Open5GS.Unit.Gbps},
            "downlink": {"value": 1, "unit": Open5GS.Unit.Gbps},
        },
        "security": {
            "k": "6526B07605B6D5663FD947C5BA65D141",
            "amf": "8000",
            "op": None,
            "opc": "FA25065FAC14E0EB5196BAD382B72C09",
        },
        "schema_version": 1,
        "__v": 0,
    },
    "sim_97": {
        "_id": "",
        "imsi": "001010000060597",
        "subscribed_rau_tau_timer": 12,
        "network_access_mode": 0,
        "subscriber_status": 0,
        "access_restriction_data": 32,
        "slice": [slice_data["slice_1"]],
        "ambr": {
            "uplink": {"value": 1, "unit": Open5GS.Unit.Gbps},
            "downlink": {"value": 1, "unit": Open5GS.Unit.Gbps},
        },
        "security": {
            "k": "E8CD15760B3C91F85E750E66EC6688EC",
            "amf": "8000",
            "op": None,
            "opc": "86BA674F840472143F0B06B070F42234",
        },
        "schema_version": 1,
        "__v": 0,
    },
    "sim_99": {
        "_id": "",
        "imsi": "001010000060599",
        "subscribed_rau_tau_timer": 12,
        "network_access_mode": 0,
        "subscriber_status": 0,
        "access_restriction_data": 32,
        "slice": [slice_data["slice_2"]],
        "ambr": {
            "uplink": {"value": 1, "unit": Open5GS.Unit.Gbps},
            "downlink": {"value": 1, "unit": Open5GS.Unit.Gbps},
        },
        "security": {
            "k": "2F6E0B8F5C329503497A816D813FCB5C",
            "amf": "8000",
            "op": None,
            "opc": "85DCACDF39894DAA5D8A6BD18A44EB7D",
        },
        "schema_version": 1,
        "__v": 0,
    },
    "sim_92_rogers": {
        "_id": "",
        "imsi": "302721090020181",
        "subscribed_rau_tau_timer": 12,
        "network_access_mode": 0,
        "subscriber_status": 0,
        "access_restriction_data": 32,
        "slice": [slice_data["slice_1"]],
        "ambr": {
            "uplink": {"value": 1, "unit": Open5GS.Unit.Gbps},
            "downlink": {"value": 1, "unit": Open5GS.Unit.Gbps},
        },
        "security": {
            "k": "1B9DC14B6E16A8FE83AA0E8A0AB56FCB",
            "amf": "8000",
            "op": None,
            "opc": "8CD505786285C50FEC35AD9D328816EA",
        },
        "schema_version": 1,
        "__v": 0,
    },
    "sim_94_rogers": {
        "_id": "",
        "imsi": "302721000060594",
        "subscribed_rau_tau_timer": 12,
        "network_access_mode": 0,
        "subscriber_status": 0,
        "access_restriction_data": 32,
        "slice": [slice_data["slice_2"]],
        "ambr": {
            "uplink": {"value": 1, "unit": Open5GS.Unit.Gbps},
            "downlink": {"value": 1, "unit": Open5GS.Unit.Gbps},
        },
        "security": {
            "k": "6526B07605B6D5663FD947C5BA65D141",
            "amf": "8000",
            "op": None,
            "opc": "FA25065FAC14E0EB5196BAD382B72C09",
        },
        "schema_version": 1,
        "__v": 0,
    },
}

######################### HELPER FUNCTIONS #################################

def convert_defaultdict_to_dict(obj):
    """Recursively converts defaultdict to dict."""
    if isinstance(obj, defaultdict):
        obj = dict(obj)  # Convert the defaultdict to a regular dict
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = convert_defaultdict_to_dict(value)  # Recursively convert nested defaultdicts
    return obj

def load_existing_data():
    """Load existing slice and subscriber data if available."""
    global slice_data, simulated_subscriber_data, cots_subscriber_data
    try:
        with open(DEFAULT_CONFIG["SLICE_FILE_PATH"], "r") as file:
            slice_data = yaml.load(file)
    except FileNotFoundError:
        log.warning(f"No existing slice data found at {DEFAULT_CONFIG['SLICE_FILE_PATH']}")

    try:
        with open(DEFAULT_CONFIG["SUBSCRIBER_FILE_PATH"], "r") as file:
            subscribers = yaml.load(file)
    except FileNotFoundError:
        log.warning(f"No existing subscriber data found at {DEFAULT_CONFIG['SUBSCRIBER_FILE_PATH']}")

def generate_slice_data(slice_number, qos_index=DEFAULT_CONFIG["DEFAULT_QOS_INDEX"]):
    slice_name = f"slice_{slice_number}"
    sd = f"{slice_number:06x}"
    session_name = f"dnn{slice_number}"

    return {
        slice_name: {
            "sst": slice_number,
            "sd": sd,
            "default_indicator": True,
            "session": [
                {
                    "name": session_name,
                    "type": Open5GS.Type.IPv4,
                    "pcc_rule": [],
                    "ambr": {
                        "uplink": DEFAULT_CONFIG["DEFAULT_UPLINK_SPEED"],
                        "downlink": DEFAULT_CONFIG["DEFAULT_DOWNLINK_SPEED"],
                    },
                    "qos": {"index": qos_index, "arp": DEFAULT_CONFIG["DEFAULT_ARP_VALUES"]},
                }
            ],
        }
    }

def create_slices(num_slices):
    """Create slices based on the number specified and add to slice_data."""
    last_slice_number = max(slice_data.keys(), key=lambda x: int(x.split("_")[1]), default="slice_0")
    starting_slice_number = int(last_slice_number.split("_")[1]) + 1

    for i in range(starting_slice_number, starting_slice_number + num_slices):
        slice_data.update(generate_slice_data(i))

def generate_subscriber_data(slice_name, subscriber_index):
    slice_info = slice_data[slice_name]
    slice_number = int(slice_name.split("_")[1])
    subscriber_name = f"subscriber_{slice_number}{subscriber_index:02d}"

    padding_length = 15 - len(f"00101{slice_name.split('_')[1]}{subscriber_index:02d}")
    imsi = f"00101{'0' * padding_length}{slice_name.split('_')[1]}{subscriber_index:02d}"

    return {
        subscriber_name: {
            "_id": "",
            "imsi": imsi,
            "subscribed_rau_tau_timer": 12,
            "network_access_mode": 0,
            "subscriber_status": 0,
            "access_restriction_data": 32,
            "slice": [slice_info],
            "ambr": {
                "uplink": DEFAULT_CONFIG["DEFAULT_UPLINK_SPEED"],
                "downlink": DEFAULT_CONFIG["DEFAULT_DOWNLINK_SPEED"],
            },
            "security": {
                "k": DEFAULT_CONFIG["DEFAULT_KEY"],
                "amf": "8000",
                "op": None,
                "opc": DEFAULT_CONFIG["DEFAULT_OPC"],
            },
            "schema_version": 1,
            "__v": 0,
        }
    }

def create_auto_generated_subscribers():
    """Create subscribers and assign them to slices in a round-robin fashion."""
    subscribers = {}

    num_auto_generated_subscribers = DEFAULT_CONFIG["NUM_AUTO_GENERATED_SUBSCRIBERS"]

    if num_auto_generated_subscribers > 0:
        log.info(f"Generating {num_auto_generated_subscribers} auto generated subscribers ...")

        num_slices = DEFAULT_CONFIG["NUM_SLICES"]
        slice_counter = 0
        subscriber_assignments = defaultdict(list)
        for i in range(1, num_auto_generated_subscribers + 1):
            slice_index = slice_counter % num_slices + 1
            slice_name = f"slice_{slice_index}"
            subscriber_index = len(subscriber_assignments[slice_name]) + 1
            subscriber_assignments[slice_name].append(subscriber_index)
            subscriber = generate_subscriber_data(slice_name, subscriber_index)
            subscribers.update(subscriber)
            slice_counter += 1

    return subscribers

def create_cots_subscribers(subscribers):
    num_cots_subscribers = DEFAULT_CONFIG["NUM_COTS_SUBSCRIBERS"]
    if num_cots_subscribers > 0:
        log.info(f"Adding {num_cots_subscribers} COTS subscribers ...")
        from itertools import islice
        for key, value in islice(cots_subscriber_data.items(), num_cots_subscribers):
            subscribers[key] = value

def create_simulated_subscribers(subscribers):
    num_simulated_subscribers = DEFAULT_CONFIG["NUM_SAMPLE_SUBSCRIBERS"]
    if  num_simulated_subscribers > 0:
        log.info(f"Adding {num_simulated_subscribers} sample subscribers ...")
        from itertools import islice
        for key, value in islice(simulated_subscriber_data.items(), num_simulated_subscribers):
            subscribers[key] = value



######################### MAIN SCRIPT ###################################

def main():

    parser = argparse.ArgumentParser(description="Generate Open5GS subscriber information.")
    parser.add_argument(
        "--num-cots-subscribers",
        type=int,
        default=DEFAULT_CONFIG["NUM_COTS_SUBSCRIBERS"],
        help="Number of COTS subscribers (default: %(default)s)"
    )
    args = parser.parse_args()

    DEFAULT_CONFIG["NUM_COTS_SUBSCRIBERS"] = args.num_cots_subscribers

    log.info("Loading existing data...")
    load_existing_data()

    log.info(f"Creating {DEFAULT_CONFIG['NUM_SLICES']} slices ...")
    slices_to_generate = DEFAULT_CONFIG["NUM_SLICES"] - len(slice_data)
    log.info(f"Generating {slices_to_generate} new slices...")
    create_slices(slices_to_generate)

    log.info(f"Saving slices to {DEFAULT_CONFIG['SLICE_FILE_PATH']}")
    with open(DEFAULT_CONFIG["SLICE_FILE_PATH"], "w") as file:
        yaml.dump(slice_data, file)

    subscribers = create_auto_generated_subscribers()
    create_cots_subscribers(subscribers)
    create_simulated_subscribers(subscribers)

    log.info(f"Saving subscribers to {DEFAULT_CONFIG['SUBSCRIBER_FILE_PATH']}")
    with open(DEFAULT_CONFIG["SUBSCRIBER_FILE_PATH"], "w") as file:
        yaml.dump(subscribers, file)

    log.info("Slice and subscriber creation complete.")

if __name__ == "__main__":
    main()
