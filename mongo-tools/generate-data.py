from open5gs import Open5GS
from collections import defaultdict
from logger import log
from ruamel.yaml import YAML
import argparse
from pathlib import Path
from itertools import islice

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


def load_existing_data(slice_file_path: Path) -> None:
    """Load existing slice and subscriber data if available."""
    global slice_data
    try:
        with open(slice_file_path, "r") as file:
            loaded_data = yaml.load(file)
            if loaded_data:
                slice_data = loaded_data
                log.info(f"Loaded {len(slice_data)} existing slices from {slice_file_path}")
    except FileNotFoundError:
        log.warning(f"No existing slice data found at {slice_file_path}")


def generate_slice_data(slice_number: int, qos_index: int = None) -> dict:
    """Generate a single slice configuration."""
    if qos_index is None:
        qos_index = DEFAULT_CONFIG["DEFAULT_QOS_INDEX"]
    
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


def create_slices(num_slices: int) -> None:
    """Create slices based on the number specified and add to slice_data."""
    if num_slices <= 0:
        return
    
    last_slice_number = max(
        (int(x.split("_")[1]) for x in slice_data.keys() if x.startswith("slice_")),
        default=0
    )
    starting_slice_number = last_slice_number + 1

    for i in range(starting_slice_number, starting_slice_number + num_slices):
        slice_data.update(generate_slice_data(i))


def generate_subscriber_data(slice_name: str, subscriber_index: int) -> dict:
    """Generate a single subscriber configuration."""
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


def create_auto_generated_subscribers(num_slices: int, num_auto_generated_subscribers: int) -> dict:
    """Create subscribers and assign them to slices in a round-robin fashion."""
    subscribers = {}

    if num_auto_generated_subscribers > 0:
        log.info(f"Generating {num_auto_generated_subscribers} auto generated subscribers ...")
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


def create_cots_subscribers(subscribers: dict, num_cots_subscribers: int) -> None:
    """Add COTS subscribers to the subscribers dictionary."""
    if num_cots_subscribers <= 0:
        return
    
    max_available = len(cots_subscriber_data)
    if num_cots_subscribers > max_available:
        log.warning(
            f"Requested {num_cots_subscribers} COTS subscribers but only "
            f"{max_available} available. Using {max_available}."
        )
        num_cots_subscribers = max_available
    
    log.info(f"Adding {num_cots_subscribers} COTS subscribers ...")
    for key, value in islice(cots_subscriber_data.items(), num_cots_subscribers):
        subscribers[key] = value


def create_simulated_subscribers(subscribers: dict, num_simulated_subscribers: int) -> None:
    """Add simulated/sample subscribers to the subscribers dictionary."""
    if num_simulated_subscribers <= 0:
        return
    
    max_available = len(simulated_subscriber_data)
    if num_simulated_subscribers > max_available:
        log.warning(
            f"Requested {num_simulated_subscribers} sample subscribers but only "
            f"{max_available} available. Using {max_available}."
        )
        num_simulated_subscribers = max_available
    
    log.info(f"Adding {num_simulated_subscribers} sample subscribers ...")
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
    parser.add_argument(
        "--num-slices",
        type=int,
        default=DEFAULT_CONFIG["NUM_SLICES"],
        help="Number of network slices (default: %(default)s)"
    )
    parser.add_argument(
        "--num-sample-subscribers",
        type=int,
        default=DEFAULT_CONFIG["NUM_SAMPLE_SUBSCRIBERS"],
        help="Number of sample/simulated subscribers (default: %(default)s)"
    )
    parser.add_argument(
        "--num-auto-generated-subscribers",
        type=int,
        default=DEFAULT_CONFIG["NUM_AUTO_GENERATED_SUBSCRIBERS"],
        help="Number of auto-generated subscribers (default: %(default)s)"
    )
    parser.add_argument(
        "--slices-file",
        type=Path,
        default=DEFAULT_CONFIG["SLICE_FILE_PATH"],
        help="Path to the slices YAML file (default: %(default)s)"
    )
    parser.add_argument(
        "--subscribers-file",
        type=Path,
        default=DEFAULT_CONFIG["SUBSCRIBER_FILE_PATH"],
        help="Path to the subscribers YAML file (default: %(default)s)"
    )
    args = parser.parse_args()

    # Create data directory if it doesn't exist
    Path(DEFAULT_CONFIG["DATA_DIR"]).mkdir(parents=True, exist_ok=True)

    # Load existing data
    log.info("Loading existing data...")
    load_existing_data(args.slices_file)

    # Create slices
    log.info(f"Target: {args.num_slices} total slices")
    slices_to_generate = max(0, args.num_slices - len(slice_data))
    
    if slices_to_generate > 0:
        log.info(f"Generating {slices_to_generate} new slices...")
        create_slices(slices_to_generate)
    else:
        log.info(f"Already have {len(slice_data)} slices, no new slices needed.")

    # Save slices
    log.info(f"Saving {len(slice_data)} slices to {args.slices_file}")
    with open(args.slices_file, "w") as file:
        yaml.dump(slice_data, file)

    # Create subscribers
    subscribers = create_auto_generated_subscribers(
        num_slices=args.num_slices,
        num_auto_generated_subscribers=args.num_auto_generated_subscribers
    )
    create_cots_subscribers(subscribers, args.num_cots_subscribers)
    create_simulated_subscribers(subscribers, args.num_sample_subscribers)

    # Save subscribers
    if subscribers:
        log.info(f"Saving {len(subscribers)} subscribers to {args.subscribers_file}")
        with open(args.subscribers_file, "w") as file:
            yaml.dump(subscribers, file)
    else:
        log.warning("No subscribers to save.")

    log.info("Slice and subscriber creation complete.")


if __name__ == "__main__":
    main()