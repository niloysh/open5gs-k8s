---
marp: true
theme: default
paginate: true
# size: 4:3
---


# Lab 2: Deploying a 3rd UE
In this lab, participants will deploy a third User Equipment (UE) that connects to an existing 5G slice. This exercise focuses on configuring slice-related parameters and verifying connectivity. By the end of this lab, participants will understand how to add a new UE, configure it for a specific slice, and observe its connectivity through the 5G core components.

---

# Background - Understanding SNSSAI

Single Network Slice Selection Assistance Information (S-NSSAI) is used to identify and select the appropriate network slice for a session. It consists of two key components:
- Slice/Service Type (SST)
- Slice Differentiator (SD)

**How S-NSSAI Works**

- When a UE initiates a connection, it includes S-NSSAI information in the initial signaling message (e.g., registration request).
- The network processes the provided S-NSSAI, matches it to available slice instances, and selects the most suitable slice based on the UE's requirements.
---

# Configure Slice Information for the 3rd UE

**Exercise: Define slice parameters for UE3**
Based on your understanding of the core, fill out the details such as `SST`, `SD` and `DNN/APN` below for the 3rd subscriber to connect to `Slice 1`.

### Subscriber 3 
    IMSI: 001010000000003
    Key: 465B5CE8B199B49FAA5F0A2EE238A6BD
    OPC: E8ED289DEBA952E4283B54E88E6183CB
    SST: ?
    SD: ?
    DNN/APN: ?
    Type: ipv4

Next, open the Open5GS WebUI (http://localhost:30300) and add a new subscriber with the details specified above.

---

# Deploy UE3 using UERANSIM (1/2)

Deploy UE3 using UERANSIM. We will start by uncommenting UE3 in the UERANSIM configuration files to enable its deployment.

**Exercise: Enable UE3 in UERANSIM Deployment**

1. Open the `kustomization.yaml` file located in `ueransim/ueransim-ue/`.
2. Uncomment the ue3 entry in the resources section to enable its deployment.

```yaml
resources:
  - ue1
  - ue2
  # - ue3
```
3. Don't forget to save the file after this change.

---

# Deploy UE3 using UERANSIM (2/2)

Open the `configmap.yaml` for UE3 (located in `ueransim/ueransim-ue/ue3`), and check that the `Key` and `OPC` match the values used when adding UE3 to the core in the WebUI.

Redeploy `ueransim-ue` as shown below.

```bash
kubectl apply -k ueransim/ueransim-ue -n open5gs
```

Ensure that UE3 is deployed using the `kubectl get pods -n open5gs` command.

---

# Check Deployment and Connectivity

**1. Verify UE3 Deployment:** Confirm that a PDU session is established by checking UE3 logs.
**2. Test connectivity:** Ping `google.ca` from UE1 and UE3 and observe if both UEs' traffic appears in UPF1 logs.

**Question**: Do you see pings from both UE1 and UE3 reaching UPF1?

---
# Next Steps
**Congratulations! This concludes the morning session of Day 1!**
You've successfully done the following:
- Learned how the core is configured.
- Learned how to add subscribers to specific slices.

**What's Next?**
In the afternoon session, we will dive into **network slice monitoring** with [Monarch](https://niloysh.github.io/5g-monarch/slides.pdf).