# Lab 2: Deploying a 3rd UE
In this lab, participants will deploy a third User Equipment (UE) that connects to an existing 5G slice. This exercise focuses on configuring slice-related parameters and verifying connectivity. By the end of this lab, participants will understand how to add a new UE, configure it for a specific slice, and observe its connectivity through the 5G core components.

### Objectives
1. Configure and deploy a new UE to connect to an existing slice.
2. Understand key parameters, such as SST, SD, and DNN/APN, required for slice association.
3. Verify the deployment and connectivity of the new UE.

### Prerequisites
Familiarity with:
- Kubernetes ConfigMaps, Deployments, and using kubectl.
- UERANSIM for simulating UEs and its integration with the 5G core.
- Basic concepts around 5G slices, including SST (Slice/Service Type), SD (Slice Differentiator), and DNN/APN (Data Network Name/Access Point Name).

## Step 1: Configuring Slice Information for the 3rd UE
We will configure a third subscriber (UE3) that connects to Slice 1. 

**Exercise 1: Define slice parameters for UE3**
Based on your understanding of the core, fill out the details such as SST, SD and DNN/APN below for the 3rd subscriber to connect to the first slice.

> [!TIP]
> Check out the configmaps for SMF1 and UPF1

### Subscriber 3 
    IMSI: 001010000000003
    Key: 465B5CE8B199B49FAA5F0A2EE238A6BD
    OPC: E8ED289DEBA952E4283B54E88E6183CB
    SST: ?
    SD: ?
    DNN/APN: ?
    Type: ipv4

Once the details are filled out, add Subscriber 3 using the WebUI:

1.	Open the Open5GS WebUI.
2.	Add a new subscriber with the details specified above.

## Step 2: Deploying UE3 using UERANSIM

After adding UE3 to the core, we will deploy its configuration using UERANSIM. We will start by uncommenting UE3 in the UERANSIM configuration files to enable its deployment.

**Exercise 2: Enable UE3 in UERANSIM Deployment**

1. Open the [kustomization file inside ueransim/ueransim-ue](../../ueransim/ueransim-ue/kustomization.yaml). 
2. Uncomment the ue3 in the resources part and save the file.

```yaml
resources:
  - ue1
  - ue2
  # - ue3
```

## Step 3: Verify Configuration for UE3

Open the ConfigMap for UE3 (located in ueransim/ueransim-ue/ue3), and check that the Key and OPC match the values used when adding UE3 to the core in the WebUI.

Redeploy the ueransim-ue.

```bash
kubectl apply -k ueransim/ueransim-ue -n open5gs
```

## Step 4: Check Deployment and Connectivity

1. Verify that UE3 is deployed and confirm that a PDU session is established.
   - Check the status of UE3 in the UERANSIM logs.
2. Test connectivity:
   - Ping from UE1 and UE3 and observe if both UEs' traffic appears in UPF1 logs.

**Question**: Do you see pings from both UE1 and UE3 reaching UPF1? Is that expected?
