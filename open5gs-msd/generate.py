from ruamel.yaml import YAML
from pathlib import Path
import json
from logger import log
import argparse
import shutil

yaml = YAML()

BASE_DIR = "base"
PATCH_DIR = "patches"
SLICE_DIR = "slices"
DATA_DIR = "../data"

existing_slices = 2  # in open5gs directory, created manually


def patch_amf():
    log.info("Patching amfcfg to add s_nssai ...")
    Path(PATCH_DIR).mkdir(parents=True, exist_ok=True)

    with open(BASE_DIR + "/amfcfg.yaml", "r") as file:
        config = yaml.load(file)

        plmn_support = config["amf"]["plmn_support"]
        s_nssai = plmn_support[0]["s_nssai"]

        s_nssai_list = []
        for slice_index in range(1, num_slices + 1):
            sst = slice_index
            sd = f"{slice_index:06}"
            d = {"sst": sst, "sd": sd}
            s_nssai_list.append(d)

        plmn_support[0]["s_nssai"] = s_nssai_list

    with open(PATCH_DIR + "/amfcfg.yaml", "w") as file:
        yaml.dump(config, file)


def patch_nssf():
    log.info("Patching nssfcfg to add nsi ...")
    with open(BASE_DIR + "/nssfcfg.yaml", "r") as file:
        config = yaml.load(file)

        nsi = config["nssf"]["sbi"]["client"]["nsi"]

        nsi_list = []
        for slice_index in range(1, num_slices + 1):
            sst = slice_index
            sd = f"{slice_index:06}"
            d = {"sst": sst, "sd": sd}
            nsi_item = {"uri": "http://nrf-nnrf:80", "s_nssai": d}
            nsi_list.append(nsi_item)

        config["nssf"]["sbi"]["client"]["nsi"] = nsi_list

    with open(PATCH_DIR + "/nssfcfg.yaml", "w") as file:
        yaml.dump(config, file)


def patch_pcf():
    log.info("Patching pcf deployment to add init containers for smf ... ")
    with open(BASE_DIR + "/pcf-deployment.yaml", "r") as file:
        config = yaml.load(file)

        init_container_list = []
        for slice_index in range(1, num_slices + 1):
            init_container = {
                "name": f"wait-smf{slice_index}",
                "image": "busybox:1.32.0",
                "env": [{"name": "DEPENDENCIES", "value": f"smf{slice_index}-nsmf:80"}],
                "command": [
                    "sh",
                    "-c",
                    "until nc -z $DEPENDENCIES; do echo waiting for the SMF; sleep 2; done;",
                ],
            }

            init_container_list.append(init_container)

        config["spec"]["template"]["spec"]["initContainers"] = init_container_list

    with open(PATCH_DIR + "/pcf-deployment.yaml", "w") as file:
        yaml.dump(config, file)


def patch_smf():
    log.info("Patching smf ...")

    def patch_kustomization():
        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "resources": [f"smf-deployment.yaml", f"smf-service.yaml"],
            "configMapGenerator": [
                {
                    "name": f"smf{slice_index}-configmap",
                    "files": ["smfcfg.yaml"],
                    "options": {
                        "labels": {
                            "app": "open5gs",
                            "nf": "smf",
                            "name": f"smf{slice_index}",
                        }
                    },
                }
            ],
        }

        log.debug(f"Patching kustomization.yaml in {smf_dir} ...")
        with open(smf_dir + "/kustomization.yaml", "w+") as file:
            yaml.dump(kustomization, file)

    def patch_configmap():
        with open(BASE_DIR + "/smfcfg.yaml", "r") as file:
            config = yaml.load(file)

            pfcp = config["smf"]["pfcp"]
            pfcp["client"]["upf"][0] = {
                "address": f"10.10.4.{slice_index}",
                "dnn": f"dnn{slice_index}",
            }

            info = config["smf"]["info"]
            info[0]["s_nssai"] = {
                "sst": slice_index,
                "sd": f"{slice_index:06}",
                "dnn": [f"dnn{slice_index}"],
            }

            session = config["smf"]["session"]
            session[0] = {"subnet": f"10.{40 + slice_index}.0.1/16"}

            config["smf"]["sbi"]["server"][0]["advertise"] = f"smf{slice_index}-nsmf"

        log.debug(f"Patching smfcfg.yaml in {smf_dir} ...")
        with open(smf_dir + "/smfcfg.yaml", "w") as file:
            yaml.dump(config, file)

    def patch_deployment():
        with open(BASE_DIR + "/smf-deployment.yaml", "r") as file:
            config = yaml.load(file)

            config["metadata"]["name"] = f"open5gs-smf{slice_index}"
            config["metadata"]["labels"]["name"] = f"smf{slice_index}"
            config["spec"]["selector"]["matchLabels"]["name"] = f"smf{slice_index}"
            config["spec"]["template"]["metadata"]["labels"][
                "name"
            ] = f"smf{slice_index}"
            config["spec"]["template"]["spec"]["volumes"][0]["projected"]["sources"][0][
                "configMap"
            ]["name"] = f"smf{slice_index}-configmap"

            networks = yaml.load(
                config["spec"]["template"]["metadata"]["annotations"][
                    "k8s.v1.cni.cncf.io/networks"
                ]
            )

            for network in networks:
                if network["name"] == "n4network":
                    network["ips"] = [f"10.10.4.{100 + slice_index}/24"]
                if network["name"] == "n3network":
                    network["ips"] = [f"10.10.3.{100 + slice_index}/24"]

            config["spec"]["template"]["metadata"]["annotations"][
                "k8s.v1.cni.cncf.io/networks"
            ] = json.dumps(networks)

        log.debug(f"Patching smf-deployment.yaml in {smf_dir} ...")
        with open(smf_dir + "/smf-deployment.yaml", "w") as file:
            yaml.dump(config, file)

    def patch_service():
        with open(BASE_DIR + "/smf-service.yaml", "r") as file:
            config = yaml.load(file)
            config["metadata"]["name"] = f"smf{slice_index}-nsmf"
            config["metadata"]["labels"]["name"] = f"smf{slice_index}"

            config["spec"]["selector"]["name"] = f"smf{slice_index}"

        log.debug(f"Patching smf-service.yaml in {smf_dir} ...")
        with open(smf_dir + "/smf-service.yaml", "w") as file:
            yaml.dump(config, file)

    for slice_index in range(existing_slices + 1, num_slices + 1):
        smf_dir = f"{SLICE_DIR}/slice{slice_index}/smf{slice_index}"
        Path(smf_dir).mkdir(parents=True, exist_ok=True)
        patch_kustomization()
        patch_configmap()
        patch_deployment()
        patch_service()


def patch_upf():
    log.info("Patching upf ...")

    def patch_kustomization():
        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "resources": [f"upf-deployment.yaml"],
            "configMapGenerator": [
                {
                    "name": f"upf{slice_index}-configmap",
                    "files": ["upfcfg.yaml", "wrapper.sh"],
                    "options": {
                        "labels": {
                            "app": "open5gs",
                            "nf": "upf",
                            "name": f"upf{slice_index}",
                        }
                    },
                }
            ],
        }

        log.debug(f"Patching kustomization.yaml in {upf_dir} ...")
        with open(upf_dir + "/kustomization.yaml", "w+") as file:
            yaml.dump(kustomization, file)

    def patch_configmap():
        with open(BASE_DIR + "/upfcfg.yaml", "r") as file:
            config = yaml.load(file)

        config["upf"]["session"][0]["subnet"] = f"10.{40 + slice_index}.0.1/16"
        config["upf"]["session"][0]["dnn"] = f"dnn{slice_index}"

        log.debug(f"Patching upfcfg.yaml in {upf_dir} ...")
        with open(upf_dir + "/upfcfg.yaml", "w+") as file:
            yaml.dump(config, file)

        wrapper = f"""#!/bin/bash
ip tuntap add name ogstun mode tun
ip addr add 10.{40 + slice_index}.0.1/16 dev ogstun
sysctl -w net.ipv6.conf.all.disable_ipv6=1
ip link set ogstun up
sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
iptables -t nat -A POSTROUTING -s 10.{40 + slice_index}.0.0/16 ! -o ogstun -j MASQUERADE

/open5gs/install/bin/open5gs-upfd -c /open5gs/config/upfcfg.yaml
"""
        log.debug(f"Patching wrapper.sh in {upf_dir} ...")
        with open(upf_dir + "/wrapper.sh", "w+") as file:
            file.write(wrapper)

    def patch_deployment():
        with open(BASE_DIR + "/upf-deployment.yaml", "r") as file:
            config = yaml.load(file)

            config["metadata"]["name"] = f"open5gs-upf{slice_index}"
            config["metadata"]["labels"]["name"] = f"upf{slice_index}"
            config["spec"]["selector"]["matchLabels"]["name"] = f"upf{slice_index}"
            config["spec"]["template"]["metadata"]["labels"][
                "name"
            ] = f"upf{slice_index}"

            config["spec"]["template"]["spec"]["volumes"][0]["configMap"][
                "name"
            ] = f"upf{slice_index}-configmap"

            config["spec"]["template"]["spec"]["initContainers"][0]["env"][0][
                "value"
            ] = f"smf{slice_index}-nsmf:80"

            networks = yaml.load(
                config["spec"]["template"]["metadata"]["annotations"][
                    "k8s.v1.cni.cncf.io/networks"
                ]
            )

            for network in networks:
                if network["name"] == "n4network":
                    network["ips"] = [f"10.10.4.{slice_index}/24"]
                if network["name"] == "n3network":
                    network["ips"] = [f"10.10.3.{slice_index}/24"]

            config["spec"]["template"]["metadata"]["annotations"][
                "k8s.v1.cni.cncf.io/networks"
            ] = json.dumps(networks)

        log.debug(f"Patching upf-deployment.yaml in {upf_dir} ...")
        with open(upf_dir + "/upf-deployment.yaml", "w+") as file:
            yaml.dump(config, file)

    for slice_index in range(existing_slices + 1, num_slices + 1):
        upf_dir = f"{SLICE_DIR}/slice{slice_index}/upf{slice_index}"
        Path(upf_dir).mkdir(parents=True, exist_ok=True)

        patch_kustomization()
        patch_configmap()
        patch_deployment()


def patch_kustomize():
    for slice_index in range(existing_slices + 1, num_slices + 1):
        output_dir = f"{SLICE_DIR}/slice{slice_index}"
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "resources": [f"smf{slice_index}", f"upf{slice_index}"],
        }

        log.debug(f"Patching kustomization.yaml in {output_dir} ...")
        with open(output_dir + "/kustomization.yaml", "w+") as file:
            yaml.dump(kustomization, file)

    kustomization = {
        "apiVersion": "kustomize.config.k8s.io/v1beta1",
        "kind": "Kustomization",
        "resources": [
            f"slice{slice_idx}"
            for slice_idx in range(existing_slices + 1, num_slices + 1)
        ],
    }

    output_dir = f"{SLICE_DIR}"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log.debug(f"Patching kustomization.yaml in {SLICE_DIR} ...")
    with open(SLICE_DIR + "/kustomization.yaml", "w+") as file:
        yaml.dump(kustomization, file)


def clean_up():
    log.info("Cleaning up files from previous run ...")
    shutil.rmtree(PATCH_DIR, ignore_errors=True)
    shutil.rmtree(SLICE_DIR, ignore_errors=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate open5gs-msd manifests for multiple slices"
    )
    parser.add_argument(
        "--slices",
        default="2",
        help='Number of slices to generate. Default (and min) is "2"',
    )

    args = parser.parse_args()
    num_slices = int(args.slices)

    if num_slices < 2:
        log.error("Minimum number of slices is 2")
        exit(1)

    with open(DATA_DIR + "/config.json", "r") as file:
        config = json.loads(file.read())
        # slices configured in config.json
        num_slices_configured = config["NUM_SLICES"]

    if num_slices > num_slices_configured:
        log.error(
            f"Maximum number of slices configured in config.json is {num_slices_configured}"
        )
        exit(1)

    clean_up()
    log.info(f"Patching open5gs-msd for {num_slices} slices ...")
    patch_amf()
    patch_nssf()
    patch_pcf()
    patch_kustomize()
    patch_smf()
    patch_upf()
