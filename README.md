# open5gs-k8s

This repository contains the necessary files and resources to deploy and operate Open5GS, an open-source 5G core network implementation. It provides Kubernetes manifest files for deploying Open5GS using microservices, an all-in-one deployment variant, and Open5GS WebUI. Additionally, there are manifest files for deploying the MongoDB database and network attachment definitions for Open5GS.

For more information about Open5GS, please visit the [Open5GS GitHub repository](https://github.com/open5gs/open5gs).

![Static Badge](https://img.shields.io/badge/stable-v4.0.0-green)
![Static Badge](https://img.shields.io/badge/open5gs-v2.7.0-green)
![Static Badge](https://img.shields.io/badge/ueransim-v3.2.6-green)
![Static Badge](https://img.shields.io/badge/srsran-5e6f50a-green)
![Static Badge](https://img.shields.io/badge/k8s-v1.28.2-green)

## Directory Structure

The repository is organized as follows:

- `open5gs/`: Contains Kubernetes manifest files for deploying Open5GS using a microservices architecture.
- `open5gs-aio/`: Contains Kubernetes manifest files for deploying Open5GS as an all-in-one deployment variant.
- `open5gs-msd/`: Multi-slice deployment of open5gs; pairs with `ueransim-msd/`. Run `generate.py` to generate the configuration files.
- `open5gs-webui/`: Contains Kubernetes manifest files for deploying the Open5GS WebUI.
- `mongodb/`: Contains Kubernetes manifest files for deploying the MongoDB database, which is a prerequisite for deploying Open5GS.
- `mongo-tools`: Contains scripts for adding open5gs default account, modifying and listing subscribers, and inserting data into mongodb.
- `data/`: Contains information on slices, subscribers and configuration.
- `networks5g/`: Contains network attachment definitions for Open5GS. Two variants are provided: one using Macvlan and the other using Open vSwitch (OVS).
- `ueransim/`: Contains Kubernetes files for running UERANSIM-based simulated gNB and UEs.
- `ueransim-msd/`: Multi-slice deployment of UERANSIM; pairs with `open5gs-msd/`. Run `generate.py` to generate the configuration files.

## Deployment

**Note**: The deployment instructions assume a working kubernetes cluster with OVS CNI installed.

To deploy Open5GS and its components, follow the deployment steps below:

1. Set up OVS bridges. On each K8s cluster node, add the OVS bridges: n2br, n3br, and n4br. Connect nodes using these bridges and OVS-based VXLAN tunnels.
2. Deploy the MongoDB database using the Kubernetes manifest files provided in the `mongodb/` directory.
3. Deploy the network attachment definitions using the appropriate variant from the `networks5g/` directory (either Macvlan or OVS).
4. Choose one of the following deployment options:
   - For a microservices-based deployment, use the Kubernetes manifest files in the `open5gs/` directory.
   - For a microservices-based multi-slice deployment (msd), use the Kubernetes manifest files in the `open5gs-msd/` directory. **Note**: You will have to generate the manifest files for msd. See [multi-slice deployment](#multi-slice-deployment).
   - For an all-in-one deployment variant, use the Kubernetes manifest files in the `open5gs-aio/` directory.
   - To deploy the Open5GS WebUI, use the Kubernetes manifest files in the `open5gs-webui/` directory.

5. The `ueransim` directory contains Kubernetes manifest files for both gNB and UEs. First, deploy UERANSIM gNB and wait for NGAP connection to succeed. If you are using `open5gs-msd`, use `ueransim-msd`. **Note**: You will have to generate the manifest files for msd. See [multi-slice deployment](#multi-slice-deployment).
6. Ensure correct UE subscriber information is inserted. You can enter subscription information either using the CLI (`modify-subscribers.py` script in `mongo-tools`) or the web UI (see [accessing the Open5GS webui](#accessing-the-open5gs-webui)). Subscriber details can be found in `data/subscribers.json`.
7. Deploy UERANSIM UEs.

### Using python scripts
This project uses python scripts for managing subscription data and automating generation of manifests for multi-slice deployments. Use the following steps to setup a virtual environment.

```bash
sudo apt-get install python3-pip
sudo pip3 install virtualenv
virtualenv venv
source venv/bin/activate
pip -r requirements.txt
```

Please refer to the specific directories for more detailed instructions and usage examples.  
**Note**: Please cd into `mongo-tools` before running the python scripts.

### Multi-slice deployment
1. You can change the number of slices and subscribers in `data/config.json`. 
2. Next, run `mongo-tools/generate-data.py` to generate new data and  `mongo-tools/modify-subscribers.py` to insert subscribers into mongodb.
3. After changing the configuration, make sure to run `generate.py` in `open5gs-msd` and `ueransim-msd`.

### Accessing the Open5GS webui
1. We need to add the default admin account before accessing the webui. This can be done using the python scripts (See [Using python scripts](#using-python-scripts)). Use `mongo-tools/add-admin-account.py`
2. The Open5GS webui is configured to run on port 30300. 


### IP Ranges
This project uses overlay IPs for tunnels deployed with the OVS-CNI in Kubernetes. The CNI configuration is outlined in the `networks5g/`. 

- `n2network` as IP `10.10.2.0/24`, `n3network` has IP `10.10.3.0/24`, `n4network` has IP `10.10.4.0/24`.
- Due to constraints in srsRAN, both AMF and gNB currently utilize the `n3network` instead of `n2network`.
- UPF N3 IP range is from `10.10.3.X` from `UPFX`. UPF N4 IP range is from `10.10.4.X` for `UPFX`.
- SMF N4 IP range is from `10.10.4.{100 + X}` from `SMFX`
- AMF IP range is from `10.10.3.200` to `10.10.3.230`.
- gNB IP range is from `10.10.3.231` to `10.10.3.250`.

Please use the above conventions when connecting external gNBs, e.g., srsRAN.


## Scripts
The `bin` directory contains scripts for easily viewing logs and getting a shell on any of the NFs. Usage is as follows.
```bash
   ./k8s-log.sh <nf> <namespace>
   ./k8s-log.sh amf open5gs
```


## License

This repository is licensed under the [MIT License](LICENSE).
