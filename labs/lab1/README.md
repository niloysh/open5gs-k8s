---
marp: true
theme: default
paginate: true
# size: 4:3
---

# Lab 1: Understanding the core deployment

In this lab, you will learn how the 5G Core network is deployed in a Kubernetes environment. This will involve examining Kubernetes manifests, exploring how network functions are configured and deployed, and understanding communication and configuration across network functions.

---

# Review the AMF ConfigMap
- Open the `configmap` file in the amf directory. This file contains the main configuration for the AMF.
- Look for settings related to Public Land Mobile Network (`PLMN`) and Single Network Slice Selection Assistance Information (`SNSSAI`). Note these settings as they specify which networks and slices the AMF supports.

**Question**: Which `PLMN` and `SNSSAI` values are set in this file? What do you think will happen if we connect a UE with `SNSSAI=3-000003`?

---

# Analyze the AMF Deployment
- Open the `deployment` file in the amf directory. This file is responsible for deploying the AMF as a pod within the Kubernetes cluster.
- Notice the exposed ports, such as `38412` for `SCTP` communication, which is critical for 5G signaling.
- Observe the Multus configuration for secondary interfaces, which allows the AMF to interact with other 5G components through its `N2` interface.

**Exercise**: 
- Identify and document which ports are exposed and their purposes. A
- Locate the Multus configuration and identify the IP address of the `N2` interface. 
- Verify that the IP matches the gNodeB configuration.

---

# Examine the AMF Service
- Open the `service` file for the AMF. This file exposes port `80` to other pods, using the `amf-namf` service allowing the AMF to communicate with other 5G core components through the service-based interface.

**Question**: Which NF depends on this service being available?
**Hint**: Check the `initContainers` in the `deployment.yaml` files, which control the order of function startup by making some network functions wait for others.

---
# Next Steps

**Congratulations!**
You now have a better understanding of the core network configuration.
Once done, proceed to [Lab2](https://niloysh.github.io/open5gs-k8s/labs/lab2/README.pdf).


