# multi-slice deployment

Deploy multiple slices, with one UPF and SMF per slice. The number of slices and subscribers can be configured in `data/config.yaml`, followed by running `mongo-tools/generate-data.py` to generate the configuration files.

## usage

1. Generate the k8s manifest files using `msd/generate.py`. This will create `open5gs`, `ueransim-gnb` and `ueransim-ue` directories with the manifest files.
2. Deploy the components using kustomize. See [deploying components](../README.md#deploying-components).