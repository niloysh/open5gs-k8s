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
                    "uplink": {"value": 500, "unit": Open5GS.Unit.Mbps},
                    "downlink": {"value": 1, "unit": Open5GS.Unit.Gbps}
                },
                "qos": {
                    "index": 9,
                    "arp": {
                        "priority_level": 8,
                        "pre_emption_capability": Open5GS.Status.DISABLED,
                        "pre_emption_vulnerability": Open5GS.Status.DISABLED
                    }
                }
            }
        ]
    },
    "slice_2": {
        "sst": 2,
        "sd": "000002",
        "default_indicator": True,
        "session": [
            {
                "name": "internet",
                "type": Open5GS.Type.IPv4,
                "pcc_rule": [],
                "ambr": {
                    "uplink": {"value": 500, "unit": Open5GS.Unit.Mbps},
                    "downlink": {"value": 500, "unit": Open5GS.Unit.Mbps}
                },
                "qos": {
                    "index": 9,
                    "arp": {
                        "priority_level": 8,
                        "pre_emption_capability": Open5GS.Status.DISABLED,
                        "pre_emption_vulnerability": Open5GS.Status.DISABLED
                    }
                }
            }
        ]
    }
}


sub_data = {
    "subscriber_1": {
        "_id": '',
        "imsi": "001010000000001",
        "subscribed_rau_tau_timer": 12,
        "network_access_mode": 0,
        "subscriber_status": 0,
        "access_restriction_data": 32,
        "slice": [slice_data["slice_1"]],
        "ambr": {
            "uplink": {"value": 1, "unit": Open5GS.Unit.Gbps},
            "downlink": {"value": 1, "unit": Open5GS.Unit.Gbps}
        },
        "security": {
            "k": "465B5CE8B199B49FAA5F0A2EE238A6BC",
            "amf": "8000",
            "op": None,
            "opc": "E8ED289DEBA952E4283B54E88E6183CA"
        },
        "schema_version": 1,
        "__v": 0
    },
    "subscriber_2": {
        "_id": '',
        "imsi": "001010000000002",
        "subscribed_rau_tau_timer": 12,
        "network_access_mode": 0,
        "subscriber_status": 0,
        "access_restriction_data": 32,
        "slice": [slice_data["slice_2"]],
        "ambr": {
            "uplink": {"value": 1, "unit": Open5GS.Unit.Gbps},
            "downlink": {"value": 1, "unit": Open5GS.Unit.Gbps}
        },
        "security": {
            "k": "B199B49F465B5CE8E238A6BCAA5F0A2E",
            "amf": "8000",
            "op": None,
            "opc": "283B54E8E8ED289D8E6183CAEBA952E4"
        },
        "schema_version": 1,
        "__v": 0
    }
}
