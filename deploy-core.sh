#!/bin/bash
NAMESPACE="open5gs"
kubectl get namespace $NAMESPACE 2>/dev/null || kubectl create namespace $NAMESPACE
kubectl apply -k mongodb -n $NAMESPACE

wait_for_pod_ready() {
    local label_key=$1
    local label_value=$2

    while [ "$(kubectl get pods -n "$NAMESPACE" -l="$label_key=$label_value" -o jsonpath='{.items[*].status.containerStatuses[0].ready}')" != "true" ]; do
        sleep 5
        echo "Waiting for pod $label_value to be ready in namespace $NAMESPACE ..."
    done
    echo "Pod $label_value is ready in namespace $NAMESPACE."
}

wait_for_pod_ready "app.kubernetes.io/name" "mongodb"

kubectl apply -k networks5g -n $NAMESPACE

check_nad() {
    local network_name=$1

    kubectl get net-attach-def -n "$NAMESPACE" | grep "$network_name"
    if [ $? -ne 0 ]; then
        echo "$network_name NAD not found in $NAMESPACE namespace! Ensure networks5g subdirectory exists!"
        exit 1
    fi
    echo "$network_name NAD found in $NAMESPACE namespace. Good to proceed ..."
}

check_nad "n2network"
check_nad "n3network"
check_nad "n4network"


kubectl apply -k msd/overlays/open5gs-metrics -n open5gs

wait_for_pod_ready "nf" "nrf"
wait_for_pod_ready "nf" "scp"
wait_for_pod_ready "nf" "amf"
wait_for_pod_ready "nf" "udr"
wait_for_pod_ready "nf" "bsf"