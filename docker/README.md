# docker

- `Dockerfile`: Builds mainline Open5GS with the latest stable release.
- `Dockerfile.metrics`: Builds custom metrics branch which spits out slice specific metrics from the UPF.

# build

Build mainline Open5GS.
```bash
docker build --no-cache -t ghcr.io/niloysh/open5gs:v2.7.0 .
```

Build metrics branch.
```bash
docker build --no-cache -t ghcr.io/niloysh/open5gs:v2.7.0-upf-metrics -f Dockerfile.metrics .
```