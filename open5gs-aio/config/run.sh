#!/bin/bash

config_path="${CONFIG_PATH:-/open5gs/config}" # Read config path from environment variable, defaulting to "/open5gs/config"
debug_mode="${DEBUG_MODE:-false}" # Read debug mode from environment variable, defaulting to false

declare -a processes=(
  "/open5gs/install/bin/open5gs-nrfd -c $config_path/nrf.yaml"
  "/open5gs/install/bin/open5gs-scpd -c $config_path/scp.yaml"
  "/open5gs/install/bin/open5gs-amfd -c $config_path/amf.yaml"
  "/open5gs/install/bin/open5gs-smfd -c $config_path/smf.yaml"
  "/open5gs/install/bin/open5gs-ausfd -c $config_path/ausf.yaml"
  "/open5gs/install/bin/open5gs-udmd -c $config_path/udm.yaml"
  "/open5gs/install/bin/open5gs-udrd -c $config_path/udr.yaml"
  "/open5gs/install/bin/open5gs-pcfd -c $config_path/pcf.yaml"
  "/open5gs/install/bin/open5gs-nssfd -c $config_path/nssf.yaml"
  "/open5gs/install/bin/open5gs-bsfd -c $config_path/bsf.yaml"
  "/open5gs/install/bin/open5gs-upfd -c $config_path/upf.yaml"
)

start_processes() {
  for process in "${processes[@]}"; do
    $process &
    sleep 2
    echo "Started process: $process"
  done
  echo "All processes started successfully."
}

stop_processes() {
  for process in "${processes[@]}"; do
    pid=$(pgrep -f "$process")
    if [ -n "$pid" ]; then
      kill "$pid"
      echo "Stopped process: $process (PID: $pid)"
    else
      echo "Process $process is already stopped"
    fi
  done
  echo "All processes stopped."
  exit 0
}

echo "Starting Open5GS processes..."

start_processes

if [ "$debug_mode" = true ]; then
  echo "Press CTRL+C to stop all processes."

  # Wait for CTRL+C signal
  while true; do
    sleep 1
  done
else
  echo "Running processes in non-debug mode. The script will run indefinitely."

  # Keep the script running indefinitely
  while true; do
    sleep 1
  done
fi
