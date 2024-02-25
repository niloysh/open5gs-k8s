# dockerfiles

Dockerfiles for containers used in this project.

- `open5gs`: Builds mainline Open5GS with the latest stable release.
- `open5gs-metrics`: Builds custom metrics branch which spits out slice specific metrics from the UPF.
- `ueransim`: Builds UERANSIM with the latest stable release.

# build

Images are hosted on GitHub Container Registry. 
Example build and push commands are given below.

```bash
cd open5gs
docker build --no-cache -t ghcr.io/niloysh/open5gs:v2.7.0 .

# Push to GitHub Container Registry
docker push ghcr.io/niloysh/open5gs:v2.7.0
```
