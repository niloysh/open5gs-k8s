#!/bin/bash

# Script to Ping a Target Address from UERANSIM UE Pods in the Open5GS Namespace

NAMESPACE="open5gs"
PING_ADDRESS="www.google.ca"

# Function to print in color
print_header() {
    echo -e "\n\e[1;34m############################### $1 ###############################\e[0m"
}

print_success() {
    echo -e "\e[1;32m$1\e[0m"
}

print_error() {
    echo -e "\e[1;31mERROR: $1\e[0m"
}

# Function to print script usage
usage() {
    echo "Usage: $0"
    echo "This script pings $PING_ADDRESS from all pods containing 'ueransim-ue' in the '$NAMESPACE' namespace."
}

# Retrieve the list of UE pods
print_header "Checking for UERANSIM UE Pods in Namespace '$NAMESPACE'"
PODS=$(kubectl get pods -n $NAMESPACE | grep "ueransim-ue" | awk '{print $1}')

if [ -z "$PODS" ]; then
    print_error "No pods found containing 'ueransim-ue' in namespace: $NAMESPACE"
    exit 1
fi

print_success "Found the following UE Pods:"
echo "$PODS"

print_header "Initiating Ping Test"
echo "Pinging $PING_ADDRESS from each UE pod..."

# Arrays to store ping results
SUCCESSFUL_PODS=()
FAILED_PODS=()

# Loop through each pod and ping
for POD in $PODS; do
    CONTAINER=$(kubectl get pod $POD -n $NAMESPACE -o jsonpath='{.spec.containers[0].name}')
    echo "Pinging from pod: $POD, container: $CONTAINER"

    # Perform ping and check result
    if kubectl exec $POD -n $NAMESPACE -c $CONTAINER -- ping -I uesimtun0 -c 5 $PING_ADDRESS > /dev/null 2>&1; then
        print_success "$POD: Ping successful"
        SUCCESSFUL_PODS+=("$POD")
    else
        print_error "$POD: Ping failed"
        FAILED_PODS+=("$POD")
    fi
done

# Display summary of ping results
print_header "Ping Test Summary"
if [ ${#SUCCESSFUL_PODS[@]} -gt 0 ]; then
    echo -e "\e[1;32mSuccessful Pods:\e[0m"
    for POD in "${SUCCESSFUL_PODS[@]}"; do
        echo "  - $POD"
    done
else
    print_error "No pods were successful."
fi

if [ ${#FAILED_PODS[@]} -gt 0 ]; then
    echo -e "\e[1;31mFailed Pods:\e[0m"
    for POD in "${FAILED_PODS[@]}"; do
        echo "  - $POD"
    done
else
    print_success "All pods were successful."
fi