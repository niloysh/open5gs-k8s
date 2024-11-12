#!/bin/bash

# Function to print in color for better visibility
print_header() {
    echo -e "\n\e[1;34m############################### $1 ###############################\e[0m"
}

print_success() {
    echo -e "\e[1;32m$1\e[0m"
}

print_error() {
    echo -e "\e[1;31mERROR: $1\e[0m"
}

print_subheader() {
    echo -e "\e[1;36m--- $1 ---\e[0m"
}

# Set the namespace for Open5GS
NAMESPACE="open5gs"
TIMEOUT_DURATION=10  # Set the timeout duration in seconds

print_header "Preparing cluster for RAN deployment"
print_subheader "Checking if namespace '$NAMESPACE' exists"
kubectl get namespace $NAMESPACE 2>/dev/null || {
    print_error "Namespace '$NAMESPACE' not found. Creating it now..."
    kubectl create namespace $NAMESPACE
    print_success "Namespace '$NAMESPACE' created."
}

# Function to wait for a pod to be ready based on its label
wait_for_pod_ready() {
    local label_key=$1
    local label_value=$2
    echo "Waiting for pod with label $label_key=$label_value to be ready in namespace $NAMESPACE..."

    while [ "$(kubectl get pods -n "$NAMESPACE" -l="$label_key=$label_value" -o jsonpath='{.items[*].status.containerStatuses[0].ready}')" != "true" ]; do
        sleep 5
        echo "Still waiting for pod $label_value to be ready..."
    done
    print_success "Pod $label_value is now ready."
}

# Function to wait for a pod to be running based on its label
wait_for_pod_running() {
    local label_key=$1
    local label_value=$2
    echo "Waiting for pod with label $label_key=$label_value to be running in namespace $NAMESPACE..."

    # Check if the pod exists
    pod_count=$(kubectl get pods -n "$NAMESPACE" -l "$label_key=$label_value" --no-headers | wc -l)
    
    if [ "$pod_count" -eq 0 ]; then
        print_error "No pods found with label $label_key=$label_value in namespace $NAMESPACE."
        return 1
    fi

    # Wait for the pod to be in Running state
    while : ; do
        # Get the pod status
        pod_status=$(kubectl get pods -n "$NAMESPACE" -l "$label_key=$label_value" -o jsonpath='{.items[*].status.phase}')
        
        # Check if the pod is in 'Running' state
        if [[ "$pod_status" =~ "Running" ]]; then
            print_success "Pod $label_value is now running."
            break
        else
            echo "Pod $label_value is not running yet. Waiting..."
            sleep 5
        fi
    done
}


print_subheader "Checking if subscribers have been added"
output=$(timeout $TIMEOUT_DURATION python3 mongo-tools/check-subscribers.py)

# Check if the Python script completed successfully or timed out
if [ $? -eq 124 ]; then
    echo "ERROR: The check-subscribers script timed out after ${TIMEOUT_DURATION} seconds."
    echo "Please verify the connection to MongoDB or troubleshoot the script in mongo-tools/check-subscribers.py."
    exit 1
elif echo "$output" | grep -q "No subscribers found"; then
    echo "There are no subscribers. Please add subscribers before deploying the RAN."
    exit 1
else
    echo "$output"  # Print the list of subscribers if found
fi


print_header "Deploying the UERANSIM gNodeB (RAN Deployment [1/2])"
kubectl apply -k ueransim/ueransim-gnb -n $NAMESPACE
wait_for_pod_ready "component" "gnb"
print_success "UERANSIM gNodeB deployed successfully."

# Deploy the UEs
print_header "Deploying UERANSIM UEs (RAN Deployment [2/2])"
kubectl apply -k ueransim/ueransim-ue -n $NAMESPACE
wait_for_pod_running "component" "ue"
print_success "UERANSIM UEs deployed successfully."

# Final message for the user
print_header "Deployment Complete"
echo -e "\e[1;33mUERANSIM RAN deployment is complete and ready to use. Please follow these next steps:\e[0m"
echo "1. Send traffic through the UEs using ping tests."
echo "2. Verify that traffic passes through the correct slice using packet captures on the UPF."