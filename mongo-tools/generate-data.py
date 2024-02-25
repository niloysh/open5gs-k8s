from open5gs import Open5GS
from collections import defaultdict
from logger import log
from ruamel.yaml import YAML

yaml = YAML()

DEFAULT_UPLINK_SPEED = {"value": 1, "unit": Open5GS.Unit.Gbps}
DEFAULT_DOWNLINK_SPEED = {"value": 1, "unit": Open5GS.Unit.Gbps}
DEFAULT_QOS_INDEX = 9
DEFAULT_ARP_VALUES = {
    "priority_level": 8,
    "pre_emption_capability": Open5GS.Status.DISABLED,
    "pre_emption_vulnerability": Open5GS.Status.DISABLED,
}


DEFAULT_KEY = "465B5CE8B199B49FAA5F0A2EE238A6BC"
DEFAULT_OPC = "E8ED289DEBA952E4283B54E88E6183CA"
DATA_DIR = "../data"

SLICE_FILE_PATH = f"{DATA_DIR}/slices.yaml"
SUBSCRIBER_FILE_PATH = f"{DATA_DIR}/subscribers.yaml"

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

subscriber_data = {
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

cots_ue_data = {
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
}


def generate_slice_data(slice_number, qos_index):
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
                        "uplink": DEFAULT_UPLINK_SPEED,
                        "downlink": DEFAULT_DOWNLINK_SPEED,
                    },
                    "qos": {"index": qos_index, "arp": DEFAULT_ARP_VALUES},
                }
            ],
        }
    }


def create_slices(num_slices):
    last_slice_number = max(slice_data.keys(), key=lambda x: int(x.split("_")[1]))
    starting_slice_number = int(last_slice_number.split("_")[1]) + 1

    for i in range(starting_slice_number, starting_slice_number + num_slices):
        qos_index = DEFAULT_QOS_INDEX
        slice_data.update(generate_slice_data(i, qos_index))


def generate_subscriber_data(slice_name, subscriber_index):
    slice_info = slice_data[slice_name]
    slice_number = int(slice_name.split("_")[1])
    subscriber_name = f"subscriber_{slice_number}{subscriber_index:02d}"

    padding_length = 15 - len(f"00101{slice_name.split('_')[1]}{subscriber_index:02d}")
    imsi = (
        f"00101{'0' * padding_length}{slice_name.split('_')[1]}{subscriber_index:02d}"
    )

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
                "uplink": DEFAULT_UPLINK_SPEED,
                "downlink": DEFAULT_DOWNLINK_SPEED,
            },
            "security": {
                "k": DEFAULT_KEY,
                "amf": "8000",
                "op": None,
                "opc": DEFAULT_OPC,
            },
            "schema_version": 1,
            "__v": 0,
        }
    }


def create_subscribers(num_subscribers):
    subscribers = {}

    if config["COTS_UE"]:
        subscribers.update(cots_ue_data)

    if config["SIM_UE"]:
        subscribers.update(subscriber_data)
   

    num_slices = len(slice_data)
    slice_counter = 0
    subscriber_assignments = defaultdict(list)
    for _ in range(1, num_subscribers + 1):
        slice_index = slice_counter % num_slices + 1
        slice_name = f"slice_{slice_index}"
        subscriber_index = len(subscriber_assignments[slice_name]) + 1
        subscriber_assignments[slice_name].append(subscriber_index)
        slice_counter += 1
        subscriber = generate_subscriber_data(slice_name, subscriber_index)
        subscribers.update(subscriber)

    return subscribers


if __name__ == "__main__":

    with open(DATA_DIR + "/config.yaml", "r") as file:
        config_file = file.read()
        config = yaml.load(config_file)

    num_slices = config["NUM_SLICES"]
    num_subscribers = config["NUM_SUBSCRIBERS"]
    existing_slices = len(slice_data)

    log.info(f"Creating {num_slices} slices and {num_subscribers} subscribers")

    log.info(f"Creating slices and saving to {SLICE_FILE_PATH}")
    create_slices(num_slices - existing_slices)
    with open(SLICE_FILE_PATH, "w") as file:
        yaml.dump(slice_data, file)

    log.info(f"Creating subscribers and saving to {SUBSCRIBER_FILE_PATH}")
    num_subscribers = config["NUM_SUBSCRIBERS"]
    subscribers = create_subscribers(num_subscribers)
    with open(SUBSCRIBER_FILE_PATH, "w") as file:
        yaml.dump(subscribers, file)
