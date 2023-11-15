# open5gs-k8s

This repository contains the necessary files and resources to deploy and operate Open5GS, an open-source 5G core network implementation. It provides Kubernetes manifest files for deploying Open5GS using microservices, an all-in-one deployment variant, and Open5GS WebUI. Additionally, there are manifest files for deploying the MongoDB database and network attachment definitions for Open5GS.

For more information about Open5GS, please visit the [Open5GS GitHub repository](https://github.com/open5gs/open5gs).

## Directory Structure

The repository is organized as follows:

- `open5gs/`: Contains Kubernetes manifest files for deploying Open5GS using a microservices architecture.
- `open5gs-aio/`: Contains Kubernetes manifest files for deploying Open5GS as an all-in-one deployment variant.
- `open5gs-webui/`: Contains Kubernetes manifest files for deploying the Open5GS WebUI.
- `mongodb/`: Contains Kubernetes manifest files for deploying the MongoDB database, which is a prerequisite for deploying Open5GS.
- `mongo-tools`: Contains scripts for adding and listing subscribers to Open5GS mongodb database using python. Also contains sample subscriber information.
- `networks5g/`: Contains network attachment definitions for Open5GS. Two variants are provided: one using Macvlan and the other using Open vSwitch (OVS).
- `ueransim/`: Contains Kubernetes files for running UERANSIM-based simulated gNB and UEs.

## Deployment

To deploy Open5GS and its components, follow the deployment steps below:

0. Set up OVS bridges. On each K8s cluster node, add the OVS bridges: n2br, n3br, and n4br. Connect nodes using these bridges and OVS-based VXLAN tunnels.
1. Deploy the MongoDB database using the Kubernetes manifest files provided in the `mongodb/` directory.
2. Deploy the network attachment definitions using the appropriate variant from the `networks5g/` directory (either Macvlan or OVS).
3. Choose one of the following deployment options:
   - For a microservices-based deployment, use the Kubernetes manifest files in the `open5gs/` directory.
   - For an all-in-one deployment variant, use the Kubernetes manifest files in the `open5gs-aio/` directory.
   - To deploy the Open5GS WebUI, use the Kubernetes manifest files in the `open5gs-webui/` directory.

4. The `ueransim` directory contains Kubernetes manifest files for both gNB and UEs. First, deploy UERANSIM gNB and wait for NGAP connection to succeed.
5. Ensure correct UE subscriber information is inserted via the web UI. Subscriber details are found in UE config files.
6. Deploy UERANSIM UEs.

Please refer to the specific directories for more detailed instructions and usage examples.

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
