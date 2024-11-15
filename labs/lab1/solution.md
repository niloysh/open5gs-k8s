---
marp: true
theme: default
paginate: true
# size: 4:3
---
# AMF Configmap

If a UE attempts to connect with `SNSSAI=3-000003` - an unsupported SNSSAI, in the AMF, you might see messages like:
```bash
[WARN] Requested SNSSAI (SST=3, SD=000003) is not supported by the AMF
[ERROR] No suitable slice found for UE with SNSSAI: SST=3, SD=000003
```

---
# AMF Deployment

- **Service-based Interface (SBI):** Port 80 allows the AMF to interact with the Network Repository Function (NRF), enabling service discovery and registration.

- **N2 Interface:** Port 38412 is used to establish connectivity with the gNodeB, managing signaling and control information over SCTP.

- **Metrics Collection:** Port 9000 provides a dedicated endpoint for monitoring and gathering metrics, aiding in network performance management.

The IP address assigned to the `N2` interface on the AMF is `10.10.3.200`.

---
# AMF Service

```yaml
template:
    metadata:
      labels:
        app: open5gs
        nf: ausf   <===== the AUSF function
    spec:
      initContainers:
      - name: wait-amf    <===== waits for AMF to be running
        image: busybox:1.32.0
        env:
        - name: DEPENDENCIES
          value: amf-namf:80    <==== the amf service
```

- When a UE tries to connect, it sends a registration request to the AMF. The AMF is the primary point of contact for the UE in the 5G core network.
- Upon receiving the registration request, the AMF sends an authentication request to the AUSF.