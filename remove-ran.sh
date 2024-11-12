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

# Delete the UERANSIM UEs
print_header "Removing UERANSIM UEs (RAN Deployment [1/2])"
kubectl delete --wait=true -k ueransim/ueransim-ue -n $NAMESPACE
print_success "UERANSIM UEs removed."


# Delete the UERANSIM gNodeB
print_header "Removing UERANSIM gNodeB (RAN Deployment [2/2])"
kubectl delete --wait=true -k ueransim/ueransim-gnb -n $NAMESPACE
print_success "UERANSIM gNodeB removed."

# Final message for the user
print_header "Cleanup Complete"
echo -e "\e[1;33mAll RAN components have been removed successfully.\e[0m"
echo "The namespace '$NAMESPACE' is still available. You may delete it manually if no other resources are needed in this namespace."