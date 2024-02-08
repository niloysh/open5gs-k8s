from ruamel.yaml import YAML
from pathlib import Path
from logger import log
from collections import defaultdict
import json
import argparse
import shutil

yaml = YAML()

BASE_DIR = "base/"
UE_DIR = "ueransim-ue/ues"
GNB_DIR = "ueransim-gnb"
DATA_DIR = "../data"

with open(DATA_DIR + "/config.json", "r") as file:
    config = json.loads(file.read())
    num_slices = config["NUM_SLICES"]
    num_subscribers = config["NUM_SUBSCRIBERS"]


def patch_gnb():
    log.info("Patching gNB ...")
    Path(GNB_DIR).mkdir(parents=True, exist_ok=True)

    kustomization = {
        "apiVersion": "kustomize.config.k8s.io/v1beta1",
        "kind": "Kustomization",
        "resources": ["gnb-deployment.yaml", "gnb-service.yaml"],
        "configMapGenerator": [
            {
                "name": f"gnb-configmap",
                "files": [f"open5gs-gnb.yaml", "wrapper.sh"],
            }
        ],
    }

    with open(GNB_DIR + "/kustomization.yaml", "w+") as file:
        yaml.dump(kustomization, file)

    with open(BASE_DIR + "/gnb-deployment.yaml", "r") as file:
        config = yaml.load(file)

    with open(GNB_DIR + "/gnb-deployment.yaml", "w+") as file:
        yaml.dump(config, file)

    with open(BASE_DIR + "/gnb-service.yaml", "r") as file:
        config = yaml.load(file)

    with open(GNB_DIR + "/gnb-service.yaml", "w+") as file:
        yaml.dump(config, file)

    wrapper = """#!/bin/bash 
/ueransim/nr-gnb --config /ueransim/config/open5gs-gnb.yaml
"""
    with open(GNB_DIR + "/wrapper.sh", "w+") as file:
        file.write(wrapper)

    with open(BASE_DIR + "/open5gs-gnb.yaml", "r") as file:
        config = yaml.load(file)

        with open(DATA_DIR + "/slices.json", "r") as file:
            slice_data = json.loads(file.read())

        snssai_list = []
        for slice_index in range(1, num_slices + 1):
            slice_name = f"slice_{slice_index}"
            slice_info = slice_data[slice_name]
            snssai = {"sst": slice_info["sst"], "sd": slice_info["sd"]}
            snssai_list.append(snssai)

        config["slices"] = snssai_list

    with open(GNB_DIR + "/open5gs-gnb.yaml", "w+") as file:
        yaml.dump(config, file)


def patch_ues(subscriber_assignments):
    log.info("Patching UEs ...")
    assign_subscribers_to_slices()

    Path(UE_DIR).mkdir(parents=True, exist_ok=True)

    parent_dir = str(Path(UE_DIR).parents[0])

    kustomization = {
        "apiVersion": "kustomize.config.k8s.io/v1beta1",
        "kind": "Kustomization",
        "resources": ["ues"],
    }

    with open(parent_dir + "/kustomization.yaml", "w+") as file:
        yaml.dump(kustomization, file)

    for slice_index in range(1, num_slices + 1):
        ue_list = subscriber_assignments[slice_index]
        for ue_name in ue_list:
            ue_dir = f"{UE_DIR}/ue{ue_name}"
            Path(ue_dir).mkdir(parents=True, exist_ok=True)

            kustomization = {
                "apiVersion": "kustomize.config.k8s.io/v1beta1",
                "kind": "Kustomization",
                "resources": [f"ue-deployment.yaml"],
                "configMapGenerator": [
                    {
                        "name": f"ue{ue_name}-configmap",
                        "files": [f"ue{ue_name}.yaml", "wrapper.sh"],
                    }
                ],
            }

            with open(ue_dir + "/kustomization.yaml", "w+") as file:
                yaml.dump(kustomization, file)

            with open(BASE_DIR + "/ue-deployment.yaml", "r") as file:
                config = yaml.load(file)
                config["metadata"]["name"] = f"ueransim-ue{ue_name}"
                config["metadata"]["labels"]["name"] = f"ue{ue_name}"

                config["spec"]["selector"]["matchLabels"]["name"] = f"ue{ue_name}"
                config["spec"]["template"]["metadata"]["labels"][
                    "name"
                ] = f"ue{ue_name}"

                config["spec"]["template"]["spec"]["volumes"][0]["configMap"][
                    "name"
                ] = f"ue{ue_name}-configmap"

                config["spec"]["template"]["spec"]["volumes"][0]["configMap"]["items"][
                    0
                ]["key"] = f"ue{ue_name}.yaml"
                config["spec"]["template"]["spec"]["volumes"][0]["configMap"]["items"][
                    0
                ]["path"] = f"ue{ue_name}.yaml"

            with open(ue_dir + "/ue-deployment.yaml", "w+") as file:
                yaml.dump(config, file)

            wrapper = f"""#!/bin/bash

mkdir /dev/net
mknod /dev/net/tun c 10 200

/ueransim/nr-ue -c /ueransim/config/ue{ue_name}.yaml 
"""
            with open(ue_dir + "/wrapper.sh", "w+") as file:
                file.write(wrapper)

            with open(BASE_DIR + "/ue1.yaml", "r") as file:
                config = yaml.load(file)

                with open(DATA_DIR + "/subscribers.json", "r") as file:
                    subscribers = json.loads(file.read())

                ue_info = subscribers[f"subscriber_{ue_name}"]

                imsi = ue_info["imsi"]
                key = ue_info["security"]["k"]
                opc = ue_info["security"]["opc"]

                sst = ue_info["slice"][0]["sst"]
                sd = ue_info["slice"][0]["sd"]
                dnn = ue_info["slice"][0]["session"][0]["name"]

                config["supi"] = f"imsi-{imsi}"
                config["key"] = key
                config["op"] = opc

                config["sessions"][0]["apn"] = dnn
                config["sessions"][0]["slice"]["sst"] = sst
                config["sessions"][0]["slice"]["sd"] = sd

                config["configured-nssai"][0]["sst"] = sst
                config["configured-nssai"][0]["sd"] = sd

                config["default-nssai"][0]["sst"] = sst
                config["default-nssai"][0]["sd"] = sd

            with open(ue_dir + f"/ue{ue_name}.yaml", "w+") as file:
                yaml.dump(config, file)

    all_ues = sorted(
        [value for ue_list in subscriber_assignments.values() for value in ue_list]
    )
    kustomization = {
        "apiVersion": "kustomize.config.k8s.io/v1beta1",
        "kind": "Kustomization",
        "resources": [f"ue{ue_name}" for ue_name in all_ues],
    }

    with open(UE_DIR + "/kustomization.yaml", "w+") as file:
        yaml.dump(kustomization, file)


def assign_subscribers_to_slices():
    slice_counter = 0
    subscriber_assignments = defaultdict(list)
    for _ in range(1, num_subscribers + 1):
        slice_index = slice_counter % num_slices + 1
        subscriber_index = len(subscriber_assignments[slice_index]) + 1
        subscriber_assignments[slice_index].append(
            f"{slice_index}{subscriber_index:02d}"
        )
        slice_counter += 1

    return subscriber_assignments


def clean_up():
    log.info("Cleaning up files from previous run ...")
    shutil.rmtree(GNB_DIR, ignore_errors=True)
    shutil.rmtree(UE_DIR, ignore_errors=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate open5gs-msd manifests for multiple slices"
    )
    parser.add_argument(
        "--slices",
        default="2",
        help='Number of slices to generate. Default (and min) is "2"',
    )

    parser.add_argument(
        "--subscribers",
        default="2",
        help='Number of slices to generate. Default (and min) is "2"',
    )

    args = parser.parse_args()
    num_slices = int(args.slices)
    num_subscribers = num_slices  # 1 subscriber per slice

    clean_up()
    log.info(
        f"Patching ueransim-msd for {num_slices} slices and {num_subscribers} subscribers ..."
    )
    patch_gnb()
    subscriber_assignments = assign_subscribers_to_slices()
    patch_ues(subscriber_assignments)
