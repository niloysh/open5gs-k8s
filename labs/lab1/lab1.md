# Lab 1: Understanding the core deployment

In this lab, participants will learn how the 5G core network is deployed in a Kubernetes environment. This will involve examining Kubernetes manifests, exploring how network functions (NFs) are configured and deployed, and understanding communication and configuration across network functions.

### Prerequisites
Before starting, review Kubernetes concepts such as Deployment, Service, ConfigMap, and Multus network attachment, as covered in the [testbed-automator labs](https://github.com/niloysh/testbed-automator/blob/main/labs/lab1/lab1.md).

## Overview

The Open5GS setup is organized into two main directories: common and slices. The common directory includes a sub-directory for each NF, containing Kubernetes manifests that define each NF’s configuration, deployment, and service structure. 

## 1. Review the AMF ConfigMap
- Open the ConfigMap file in the amf directory. This file contains the main configuration for the AMF.
- Look for settings related to PLMN (Public Land Mobile Network) and SNSSAIs (Single Network Slice Selection Assistance Information). Note these settings as they specify which networks and slices the AMF supports.

**Question**: Which PLMN and SNSSAI values are set in this file? How does this configuration affect network access?

## 2. Analyze the AMF Deployment
- Open the Deployment file in the amf directory. This file is responsible for deploying the AMF as a pod within the Kubernetes cluster.
- Notice the exposed ports, such as 38412 for SCTP communication, which is critical for 5G signaling.
- Observe the Multus configuration for secondary interfaces, which allows the AMF to interact with other 5G components through its N2 interface.

**Exercise**: Exercise: Identify and document which ports are exposed and their purposes. Also, locate where Multus is configured in the file and explain how it supports multi-interface connectivity for the AMF.

## 3. Examine the AMF Service
- Open the Service file for the AMF. This file exposes port 80 to other pods, allowing the AMF to communicate with other 5G core components through the service-based interface.

**Question**: Why is port 80 exposed, and what role does the service-based interface play in the AMF’s operation?


Once done, proceed to [Lab2](../lab2/lab2.md).


