# Open5GS

This repository contains the necessary files and resources to deploy and operate Open5GS, an open-source 5G core network implementation. It provides Kubernetes manifest files for deploying Open5GS using microservices, an all-in-one deployment variant, and Open5GS WebUI. Additionally, there are manifest files for deploying the MongoDB database and network attachment definitions for Open5GS.

For more information about Open5GS, please visit the [Open5GS GitHub repository](https://github.com/open5gs/open5gs).

## Directory Structure

The repository is organized as follows:

- `open5gs/`: Contains Kubernetes manifest files for deploying Open5GS using a microservices architecture.
- `open5gs-aio/`: Contains Kubernetes manifest files for deploying Open5GS as an all-in-one deployment variant.
- `open5gs-webui/`: Contains Kubernetes manifest files for deploying the Open5GS WebUI.
- `mongodb/`: Contains Kubernetes manifest files for deploying the MongoDB database, which is a prerequisite for deploying Open5GS.
- `networks5g/`: Contains network attachment definitions for Open5GS. Two variants are provided: one using Macvlan and the other using Open vSwitch (OVS).

## Deployment

To deploy Open5GS and its components, follow the deployment steps below:

1. Deploy the MongoDB database using the Kubernetes manifest files provided in the `mongodb/` directory.
2. Deploy the network attachment definitions using the appropriate variant from the `networks5g/` directory (either Macvlan or OVS).
3. Choose one of the following deployment options:
   - For a microservices-based deployment, use the Kubernetes manifest files in the `open5gs/` directory.
   - For an all-in-one deployment variant, use the Kubernetes manifest files in the `open5gs-aio/` directory.
   - To deploy the Open5GS WebUI, use the Kubernetes manifest files in the `open5gs-webui/` directory.

Please refer to the specific directories for more detailed instructions and usage examples.

## Documentation

For more detailed information about Open5GS and its usage, please consult the official Open5GS documentation. You can find additional resources, tutorials, and community support on the Open5GS website.

## Contributing

Contributions to this repository are welcome! If you have any improvements, bug fixes, or new features to contribute, please follow the guidelines outlined in the CONTRIBUTING.md file.

## License

This repository is licensed under the [MIT License](LICENSE).
