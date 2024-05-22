# open5gs-aio

All-in-one deployment of open5GS using Docker.

## How to run

Run using docker compose, as follows:

```bash
docker-compose up -d
```

To bring it down, use

```bash
docker-compose down
```

### Web UI
Use the web UI for insterting subscriber information.

- Accessible on `localhost:9999`
- Username: `admin` Password: `1423`

## Logs
To see the logs
```bash
docker logs -f open5gs-aio 
```


## Building custom Open5GS images

1. Fork upstream Open5GS.
2. Make source code changes in your forked version.
3. Edit the [Dockerfile](./Dockerfile#L17) to point to your custom fork.
4. Build the image with updated source code using `docker build -t <image>:<tag>`
5. Edit the [docker-compose](./docker-compose.yaml#L27) file to use the newly built image.

## UERANSIM
You can test with UERANSIM using the configs in [ueransim-config](./ueransim-config/)
