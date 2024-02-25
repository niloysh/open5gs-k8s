#!/bin/bash
#
# Monitor overall Kubernetes cluster utilization and capacity.
#
# Original source:
# https://github.com/kubernetes/kubernetes/issues/17512#issuecomment-367212930
#
# Tested with:
#   - AWS EKS v1.11.5
#
# Does not require any other dependencies to be installed in the cluster.
# Source: https://www.jeffgeerling.com/blog/2019/monitoring-kubernetes-cluster-utilization-and-capacity-poor-mans-way

set -e

KUBECTL="kubectl"
NODES=$($KUBECTL get nodes --no-headers -o custom-columns=NAME:.metadata.name)

function usage() {
  local node_count=0
  local total_percent_cpu=0
  local total_percent_mem=0
  local readonly nodes=$@

  for n in $nodes; do
    local requests=$($KUBECTL describe node $n | grep -A3 -E "\\s\sRequests" | tail -n2)
    local percent_cpu=$(echo $requests | awk -F "[()%]" '{print $2}')
    local percent_mem=$(echo $requests | awk -F "[()%]" '{print $8}')
    echo "$n: ${percent_cpu}% CPU, ${percent_mem}% memory"

    node_count=$((node_count + 1))
    total_percent_cpu=$((total_percent_cpu + percent_cpu))
    total_percent_mem=$((total_percent_mem + percent_mem))
  done

  local readonly avg_percent_cpu=$((total_percent_cpu / node_count))
  local readonly avg_percent_mem=$((total_percent_mem / node_count))

  echo "Average usage: ${avg_percent_cpu}% CPU, ${avg_percent_mem}% memory."
}

usage $NODES
