#!/bin/bash
print_header() {
    echo -e "\n\e[1;34m############################### $1 ###############################\e[0m"
}

print_success() {
    echo -e "\e[1;32m$1\e[0m"
}

print_header "Adding subscribers"
python3 mongo-tools/generate-data.py --num-cots-subscribers 4
python3 mongo-tools/add-subscribers.py
print_success "Subscribers added."
