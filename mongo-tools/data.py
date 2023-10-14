from open5gs import Open5GS

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


sub_data = {
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
    "subscriber_4": {
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
