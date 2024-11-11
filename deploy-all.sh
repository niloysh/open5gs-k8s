#!/bin/bash
print_header() {
    echo -e "\n\e[1;34m############################### $1 ###############################\e[0m"
}

print_success() {
    echo -e "\e[1;32m$1\e[0m"
}

SCRIPT_DIRECTORY="$(dirname $(realpath "$0"))"

source $SCRIPT_DIRECTORY/deploy-core.sh

print_header "Adding subscribers"
python3 mongo-tools/generate-data.py
python3 mongo-tools/add-subscribers.py
print_success "Subscribers added."

source $SCRIPT_DIRECTORY/deploy-ran.sh