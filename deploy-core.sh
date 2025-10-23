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

print_warning() {
    echo -e "\e[1;33mWARNING: $1\e[0m"
}

print_subheader() {
    echo -e "\e[1;36m--- $1 ---\e[0m"
}

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --demo              Enable demo mode"
    echo "  --with-webui        Deploy WebUI (disabled by default)"
    echo "  --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Core only, no WebUI (default)"
    echo "  $0 --demo            # Demo mode, no WebUI"
    echo "  $0 --with-webui      # Core + WebUI"
    echo "  $0 --demo --with-webui # Demo mode with WebUI"
    exit 1
}

# Default values - WebUI disabled by default
DEPLOYMENT_OPTION="open5gs"
DEPLOY_WEBUI=false
NAMESPACE="open5gs"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --demo)
            DEPLOYMENT_OPTION="msd/overlays/open5gs-demo"
            print_header "Demo mode enabled"
            shift
            ;;
        --with-webui)
            DEPLOY_WEBUI=true
            print_header "WebUI deployment enabled"
            shift
            ;;
        --help)
            usage
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

print_header "Preparing cluster for 5G network deployment"

print_subheader "Checking if namespace '$NAMESPACE' exists"
kubectl get namespace $NAMESPACE 2>/dev/null || {
    print_error "Namespace '$NAMESPACE' not found. Creating it now..."
    kubectl create namespace $NAMESPACE
    print_success "Namespace '$NAMESPACE' created."
}

print_header "Adding Persistent Storage (Core Deployment [1/4])"
print_subheader "Applying MongoDB configurations"
kubectl apply -k mongodb -n $NAMESPACE
print_success "MongoDB configurations applied."

# Function to wait for a pod to be ready based on its label
wait_for_pod_ready() {
    local label_key=$1
    local label_value=$2
    echo "Waiting for pod with label $label_key=$label_value to be ready in namespace $NAMESPACE..."

    while [ "$(kubectl get pods -n "$NAMESPACE" -l="$label_key=$label_value" -o jsonpath='{.items[*].status.containerStatuses[0].ready}')" != "true" ]; do
        sleep 5
        echo "Waiting for pod $label_value to be ready..."
    done
    print_success "Pod $label_value is ready."
}

# Wait for MongoDB pod to be ready
wait_for_pod_ready "app.kubernetes.io/name" "mongodb"

# Apply 5G network configurations
print_header "Applying 5G Network Configuration (Core Deployment [2/4])"
print_subheader "Applying OVS-CNI NADs"
kubectl apply -k networks5g -n $NAMESPACE
print_success "OVS-CNI NADs applied."

# Function to check Network Attachment Definition (NAD)
check_nad() {
    local network_name=$1
    echo "Checking NAD '$network_name' in namespace '$NAMESPACE'..."

    kubectl get net-attach-def -n "$NAMESPACE" | grep "$network_name" > /dev/null
    if [ $? -ne 0 ]; then
        print_error "NAD '$network_name' not found in '$NAMESPACE'. Please check the 'networks5g' subdirectory."
        exit 1
    fi
    print_success "NAD '$network_name' found in $NAMESPACE."
}

print_subheader "Checking required NADs"
check_nad "n2network"
check_nad "n3network"
check_nad "n4network"

print_header "Deploying Open5GS core (Core Deployment [3/4])"
print_subheader "Applying Open5GS deployment option with support for Monarch"
kubectl apply -k $DEPLOYMENT_OPTION -n $NAMESPACE
print_success "Open5GS deployed."

print_subheader "Waiting for Core pods to be ready"
wait_for_pod_ready "nf" "nrf"
wait_for_pod_ready "nf" "scp"
wait_for_pod_ready "nf" "amf"
wait_for_pod_ready "nf" "udr"
wait_for_pod_ready "nf" "bsf"
print_success "Core pods ready."

print_header "Preparing core for adding subscribers (Core Deployment [4/4])"
print_subheader "Installing Python dependencies"

if ! dpkg -l | grep -q python3-venv; then
    print_subheader "Installing python3-venv package..."
    sudo apt-get update && sudo apt-get install -y python3-venv
    print_success "python3-venv installed."
fi

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
print_success "Python dependencies installed."

print_subheader "Setting Up MongoDB Admin Account"
python3 mongo-tools/add-admin-account.py
print_success "MongoDB admin account created successfully."

# Conditionally deploy WebUI
if [ "$DEPLOY_WEBUI" = true ]; then
    print_header "Deploying Open5GS Web UI"
    print_subheader "Applying WebUI configurations"
    kubectl apply -k open5gs-webui -n $NAMESPACE
    wait_for_pod_ready "nf" "webui"
    print_success "Open5GS web UI deployed."
else
    print_warning "WebUI deployment skipped (use --with-webui to enable)"
fi

# Final message for the user
print_header "Deployment Complete"
echo -e "\e[1;33mOpen5GS core deployment is complete and ready to use.\e[0m"

if [ "$DEPLOY_WEBUI" = true ]; then
    echo -e "Access the web UI at \e[1mhttp://localhost:30300\e[0m and log in with:"
    echo -e "  Username: \e[1m'admin'\e[0m"
    echo -e "  Password: \e[1m'1423'\e[0m"
    echo ""
    echo "Next steps:"
    echo "1. Use the WebUI to add subscribers and manage your 5G core"
    echo "2. Check the core logs for AMF, SMF, and UPF to ensure the core is functioning correctly"
else
    echo -e "To add subscribers, run: \e[1m./add-sim-subscribers.sh\e[0m"
    echo ""
    echo "Next steps:"
    echo "1. Run ./add-sim-subscribers.sh to add simulated subscribers to the core"
    echo "2. Check the core logs for AMF, SMF, and UPF to ensure the core is functioning correctly"
    echo "3. If you need WebUI later, run: ./deploy.sh --with-webui"
fi
