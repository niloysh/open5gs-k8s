from src.logger import log
from collections import defaultdict
import src.config as cfg
import shutil


def clean_up():
    log.info("Cleaning up files from previous run ...")

    shutil.rmtree(cfg.OPEN5GS_PATCH_DIR, ignore_errors=True)
    shutil.rmtree(cfg.OPEN5GS_BUILD_DIR, ignore_errors=True)
    shutil.rmtree(cfg.GNB_BUILD_DIR, ignore_errors=True)
    shutil.rmtree(cfg.UE_BUILD_DIR, ignore_errors=True)


def assign_subscribers_to_slices(num_subscribers, num_slices):
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