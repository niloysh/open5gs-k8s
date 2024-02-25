from src.logger import log
from pathlib import Path
from ruamel.yaml import YAML
from src.utils import assign_subscribers_to_slices
import json
import src.config as cfg

yaml = YAML()

def patch_amf(num_slices: int):
    log.info(f"Patching amfcfg to add s_nssais for {num_slices} slices ...")
    Path(cfg.OPEN5GS_PATCH_DIR).mkdir(parents=True, exist_ok=True)

    with open(cfg.DATA_DIR + "/slices.yaml", "r") as file:
        slice_config = yaml.load(file)

    with open(cfg.OPEN5GS_BASE + "/amf/amfcfg.yaml", "r") as file:
        config = yaml.load(file)

        plmn_support = config["amf"]["plmn_support"]
        s_nssai = plmn_support[0]["s_nssai"]

        s_nssai_list = []
        for slice_index in range(1, num_slices + 1):
            slice_name = f"slice_{slice_index}"
            sst = slice_config[slice_name]["sst"]
            sd = slice_config[slice_name]["sd"]
            d = {"sst": sst, "sd": sd}
            s_nssai_list.append(d)

        plmn_support[0]["s_nssai"] = s_nssai_list

    with open(cfg.OPEN5GS_PATCH_DIR + "/amfcfg.yaml", "w") as file:
        yaml.dump(config, file)

def patch_nssf(num_slices: int):
    log.info(f"Patching nssfcfg to add nsi for {num_slices} slices...")

    with open(cfg.DATA_DIR + "/slices.yaml", "r") as file:
        slice_config = yaml.load(file)

    with open(cfg.OPEN5GS_BASE + "/nssf/nssfcfg.yaml", "r") as file:
        config = yaml.load(file)

        nsi = config["nssf"]["sbi"]["client"]["nsi"]

        nsi_list = []
        for slice_index in range(1, num_slices + 1):
            slice_name = f"slice_{slice_index}"
            sst = slice_config[slice_name]["sst"]
            sd = slice_config[slice_name]["sd"]
            d = {"sst": sst, "sd": sd}
            nsi_item = {"uri": "http://nrf-nnrf:80", "s_nssai": d}
            nsi_list.append(nsi_item)

        config["nssf"]["sbi"]["client"]["nsi"] = nsi_list

    with open(cfg.OPEN5GS_PATCH_DIR + "/nssfcfg.yaml", "w") as file:
        yaml.dump(config, file)

def patch_pcf(num_slices: int):
    log.info("Patching pcf deployment to add init containers for smf ... ")
    with open(cfg.OPEN5GS_BASE + "/pcf/pcf-deployment.yaml", "r") as file:
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

    with open(cfg.OPEN5GS_PATCH_DIR + "/pcf-deployment.yaml", "w") as file:
        yaml.dump(config, file)


def patch_smf(num_slices: int):
    log.info("Patching smf ...")

    with open(cfg.DATA_DIR + "/slices.yaml", "r") as file:
        slice_config = yaml.load(file)

    def _patch_kustomization(smf_dir: str, slice_index: int):
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
            "generatorOptions": {
                "disableNameSuffixHash": True
            }
        }

        log.debug(f"Patching kustomization.yaml in {smf_dir} ...")
        with open(smf_dir + "/kustomization.yaml", "w+") as file:
            yaml.dump(kustomization, file)

    def _patch_configmap(smf_dir: str, slice_index: int):
        with open(cfg.OPEN5GS_BASE + "/smf1/smfcfg.yaml", "r") as file:
            config = yaml.load(file)

            pfcp = config["smf"]["pfcp"]
            pfcp["client"]["upf"][0] = {
                "address": f"10.10.4.{slice_index}",
                "dnn": "streaming" if slice_index==2 else f"dnn{slice_index}",
            }

            slice_name = f"slice_{slice_index}"
            sst = slice_config[slice_name]["sst"]
            sd = slice_config[slice_name]["sd"]

            info = config["smf"]["info"]
            info[0]["s_nssai"] = {
                "sst": sst,
                "sd": sd,
                "dnn": ["streaming" if slice_index==2 else f"dnn{slice_index}"],
            }

            session = config["smf"]["session"]
            session[0] = {"subnet": f"10.{40 + slice_index}.0.1/16"}

            config["smf"]["sbi"]["server"][0]["advertise"] = f"smf{slice_index}-nsmf"

        log.debug(f"Patching smfcfg.yaml in {smf_dir} ...")
        with open(smf_dir + "/smfcfg.yaml", "w") as file:
            yaml.dump(config, file)

    def _patch_deployment(smf_dir: str, slice_index: int):
        with open(cfg.OPEN5GS_BASE + "/smf1/smf-deployment.yaml", "r") as file:
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

    def _patch_service(smf_dir: str, slice_index: int):
        with open(cfg.OPEN5GS_BASE + "/smf1/smf-service.yaml", "r") as file:
            config = yaml.load(file)
            config["metadata"]["name"] = f"smf{slice_index}-nsmf"
            config["metadata"]["labels"]["name"] = f"smf{slice_index}"

            config["spec"]["selector"]["name"] = f"smf{slice_index}"

        log.debug(f"Patching smf-service.yaml in {smf_dir} ...")
        with open(smf_dir + "/smf-service.yaml", "w") as file:
            yaml.dump(config, file)

    for slice_index in range(2, num_slices + 1):
        smf_dir = f"{cfg.OPEN5GS_BUILD_DIR}/smf{slice_index}"
        Path(smf_dir).mkdir(parents=True, exist_ok=True)
        _patch_kustomization(smf_dir, slice_index)
        _patch_configmap(smf_dir, slice_index)
        _patch_deployment(smf_dir, slice_index)
        _patch_service(smf_dir, slice_index)


def patch_upf(num_slices: int):
    log.info("Patching upf ...")

    def _patch_kustomization(upf_dir: str, slice_index: int):
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

    def _patch_configmap(upf_dir: str, slice_index: int):
        with open(cfg.OPEN5GS_BASE + "/upf1/upfcfg.yaml", "r") as file:
            config = yaml.load(file)

        config["upf"]["session"][0]["subnet"] = f"10.{40 + slice_index}.0.1/16"
        config["upf"]["session"][0]["dnn"] = "streaming" if slice_index==2 else f"dnn{slice_index}"

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

    def _patch_deployment(upf_dir: str, slice_index: int):
        with open(cfg.OPEN5GS_BASE + "/upf1/upf-deployment.yaml", "r") as file:
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

    for slice_index in range(2, num_slices + 1):
        upf_dir = f"{cfg.OPEN5GS_BUILD_DIR}/upf{slice_index}"
        Path(upf_dir).mkdir(parents=True, exist_ok=True)

        _patch_kustomization(upf_dir, slice_index)
        _patch_configmap(upf_dir, slice_index)
        _patch_deployment(upf_dir, slice_index)

def patch_open5gs_kustomize(num_slices: int):
    log.info("Patching open5gs kustomization.yaml ...")
    kustomization = {
        "apiVersion": "kustomize.config.k8s.io/v1beta1",
        "kind": "Kustomization",
        "namespace": "open5gs",
        "resources": [ f"../{cfg.OPEN5GS_BASE}"] +
        [f"smf{slice_index}" for slice_index in range(2, num_slices + 1)] + 
        [f"upf{slice_index}" for slice_index in range(2, num_slices + 1)],
        "patches": [
            {"path": "patches/pcf-deployment.yaml"}
        ],
        "configMapGenerator": [
            {
                "name": "amf-configmap",
                "behavior": "replace",
                "files": [
                    "patches/amfcfg.yaml"
                ]
            },
            {
                "name": "nssf-configmap",
                "behavior": "replace",
                "files": [
                    "patches/nssfcfg.yaml"
                ]
            }
        ],
        "images": [
            {
                "name": "ghcr.io/niloysh/open5gs",
                "newTag": "v2.7.0"
            }
        ]
    }

    with open(f"{cfg.OPEN5GS_BUILD_DIR}"+ "/kustomization.yaml", "w+") as file:
        yaml.dump(kustomization, file)

def patch_gnb(num_slices: int):
    log.info("Patching gNB ...")
    Path(cfg.GNB_BUILD_DIR).mkdir(parents=True, exist_ok=True)

    with open(cfg.DATA_DIR + "/slices.yaml", "r") as file:
        slice_config = yaml.load(file)

    kustomization = {
        "apiVersion": "kustomize.config.k8s.io/v1beta1",
        "kind": "Kustomization",
        "namespace": "open5gs",
        "resources": [f"../{cfg.UERANSIM_GNB_BASE}"],
        "configMapGenerator": [
            {
                "name": f"gnb-configmap",
                "behavior": "merge",
                "files": [f"open5gs-gnb.yaml"],
            }
        ],
    }

    with open(cfg.GNB_BUILD_DIR + "/kustomization.yaml", "w+") as file:
        yaml.dump(kustomization, file)

    with open(cfg.UERANSIM_GNB_BASE + "/open5gs-gnb.yaml", "r") as file:
        config = yaml.load(file)


        snssai_list = []
        for slice_index in range(1, num_slices + 1):
            slice_name = f"slice_{slice_index}"
            sst = slice_config[slice_name]["sst"]
            sd = slice_config[slice_name]["sd"]

            # ueransim only takes decimal values for sd
            # but converts them to hex internally
            sd = int(sd, 16)
            sd = f"{sd:06d}"

            snssai = {"sst": sst, "sd": sd}
            snssai_list.append(snssai)

        config["slices"] = snssai_list

    with open(cfg.GNB_BUILD_DIR + "/open5gs-gnb.yaml", "w+") as file:
        yaml.dump(config, file)

def patch_ues(num_slices: int, num_subscribers: int):
    log.info("Patching UEs ...")
    subscriber_assignments = assign_subscribers_to_slices(num_subscribers, num_slices)

    Path(cfg.UE_BUILD_DIR).mkdir(parents=True, exist_ok=True)

    for slice_index in range(1, num_slices + 1):
        ue_list = subscriber_assignments[slice_index]
        for ue_name in ue_list:
            ue_dir = f"{cfg.UE_BUILD_DIR}/ue{ue_name}"
            Path(ue_dir).mkdir(parents=True, exist_ok=True)

            kustomization = {
                "apiVersion": "kustomize.config.k8s.io/v1beta1",
                "kind": "Kustomization",
                "resources": [f"ue-deployment.yaml"],
                "configMapGenerator": [
                    {
                        "name": f"ue{ue_name}-configmap",
                        "behavior": "create",
                        "files": [f"ue.yaml", f"wrapper.sh"],
                    }
                ],
            }

            with open(ue_dir + "/kustomization.yaml", "w+") as file:
                yaml.dump(kustomization, file)

            with open(cfg.UERANSIM_UE_BASE + "/ue101/ue-deployment.yaml", "r") as file:
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

            with open(ue_dir + "/ue-deployment.yaml", "w+") as file:
                yaml.dump(config, file)

            wrapper = f"""#!/bin/bash

mkdir /dev/net
mknod /dev/net/tun c 10 200

/ueransim/nr-ue -c /ueransim/config/ue.yaml 
"""
            with open(ue_dir + "/wrapper.sh", "w+") as file:
                file.write(wrapper)

            with open(cfg.UERANSIM_UE_BASE + "/ue101/ue.yaml", "r") as file:
                config = yaml.load(file)

                with open(cfg.DATA_DIR + "/subscribers.yaml", "r") as file:
                    subscribers = yaml.load(file.read())

                ue_info = subscribers[f"subscriber_{ue_name}"]

                imsi = ue_info["imsi"]
                key = ue_info["security"]["k"]
                opc = ue_info["security"]["opc"]

                sst = ue_info["slice"][0]["sst"]
                sd = ue_info["slice"][0]["sd"]
                dnn = ue_info["slice"][0]["session"][0]["name"]

                # ueransim only takes decimal values for sd
                # but converts them to hex internally
                sd = int(sd, 16)
                sd = f"{sd:06d}"

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

            with open(ue_dir + f"/ue.yaml", "w+") as file:
                yaml.dump(config, file)

    all_ues = sorted(
        [value for ue_list in subscriber_assignments.values() for value in ue_list]
    )

    kustomization = {
        "apiVersion": "kustomize.config.k8s.io/v1beta1",
        "kind": "Kustomization",
        "namespace": "open5gs",
        "resources": [f"ue{ue_name}" for ue_name in all_ues],
    }

    with open(cfg.UE_BUILD_DIR + "/kustomization.yaml", "w+") as file:
        yaml.dump(kustomization, file)