#!/bin/bash

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

NAMESPACE="open5gs"

# Check if the namespace exists
print_header "Checking if namespace '$NAMESPACE' exists"
kubectl get namespace $NAMESPACE 2>/dev/null
if [ $? -ne 0 ]; then
    print_error "Namespace '$NAMESPACE' not found. Exiting removal process."
    exit 1
fi

# Delete MongoDB configurations
print_header "Deleting MongoDB configurations"
kubectl delete -k mongodb -n $NAMESPACE
print_success "MongoDB configurations deleted."

# Delete 5G network configurations
print_header "Deleting 5G Network Configurations"
kubectl delete -k networks5g -n $NAMESPACE
print_success "5G network configurations deleted."

# Delete Open5GS configurations (including all its components)
print_header "Deleting Open5GS Configurations"
kubectl delete --wait=true -k open5gs -n $NAMESPACE
print_success "Open5GS configurations deleted."

# Remove Open5GS webui
print_header "Deleting Open5GS WebUI"
kubectl delete --wait=true -k open5gs-webui -n $NAMESPACE
print_success "Open5GS webui deleted."

# Wait until all Open5GS pods are deleted
print_header "Waiting for all Open5GS pods to be deleted"
while [ "$(kubectl get pods -n "$NAMESPACE" -l="app=open5gs" -o jsonpath='{.items[*].metadata.name}')" != "" ]; do
    sleep 5
    echo "Waiting for all pods to be deleted in namespace $NAMESPACE..."
done
print_success "All Open5GS pods deleted in namespace $NAMESPACE."

# Optionally, delete the namespace
# Uncomment the following lines if you want to delete the namespace
# print_header "Deleting namespace $NAMESPACE"
# kubectl delete namespace $NAMESPACE
# print_success "Namespace '$NAMESPACE' deleted."

# Final success message
print_header "Removal Complete"
print_success "Open5GS core removed successfully."