
from src.logger import log
import src.patcher as patcher
import src.utils as utils
import src.config as config
from ruamel.yaml import YAML
yaml = YAML()

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Generate k8s manifests for multiple slices")
    parser.add_argument("slices", type=int, help="Number of slices to generate")
    parser.add_argument("--subscribers", type=int, help="Number of subscribers per slice")

    args = parser.parse_args()
    slices = args.slices
    subscribers = args.subscribers
    if not subscribers:
        subscribers = slices

    with open(f"{config.DATA_DIR}" + "/config.yaml", "r") as file:
        config = yaml.load(file)

    if slices > config["NUM_SLICES"]:
        log.error(f"Maximum number of slices configured is {config['NUM_SLICES']}")
        exit(1)

    if subscribers > config["NUM_SUBSCRIBERS"]:
        log.error(f"Maximum number of subscribers configured is {config['NUM_SUBSCRIBERS']}")
        exit(1)

    log.info(f"Generating k8s manifests for {slices} slices and {subscribers} subscribers ...")

    utils.clean_up()
    patcher.patch_amf(slices)
    patcher.patch_nssf(slices)
    patcher.patch_pcf(slices)
    patcher.patch_smf(slices)
    patcher.patch_upf(slices)
    patcher.patch_open5gs_kustomize(slices)

    patcher.patch_gnb(slices)
    patcher.patch_ues(slices, subscribers)