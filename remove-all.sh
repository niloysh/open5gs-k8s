#!/bin/bash
print_header() {
    echo -e "\n\e[1;34m############################### $1 ###############################\e[0m"
}

print_success() {
    echo -e "\e[1;32m$1\e[0m"
}

SCRIPT_DIRECTORY="$(dirname $(realpath "$0"))"

source $SCRIPT_DIRECTORY/remove-ran.sh
print_header "Deleting subscribers"
python3 mongo-tools/delete-subscribers.py
print_success "Subscribers deleted."

source $SCRIPT_DIRECTORY/remove-core.sh



