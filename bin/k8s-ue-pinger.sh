#!/bin/bash

# function to print usage message
function usage {
  echo "Usage: $0 [namespace]"
  echo "       namespace (optional): the Kubernetes namespace where the pods are running"
  echo "This script will ping google.com from all pods containing 'ue' in their names."
}

# Function to prompt the user to select a namespace from a list
select_namespace() {
  echo "Select a namespace:"
  select NAMESPACE in $(kubectl get namespaces -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}')
  do
    if [ -n "$NAMESPACE" ]
    then
      break
    fi
  done
}

# Display help message if no namespace is provided
if [ "$#" -eq 0 ]
then
  select_namespace
else
  NAMESPACE=$1
fi

PODS=$(kubectl get pods -n $NAMESPACE | grep "ueransim-ue" | awk '{print $1}')

if [ -z "$PODS" ]
then
  echo "No pods found containing 'ueransim-ue' in namespace: $NAMESPACE"
  exit 1
fi

echo "Initiating ping to google.com from UE pods..."

# Loop through all matching pods and execute ping command, logging output
for POD in $PODS
do
  CONTAINER=$(kubectl get pod $POD -n $NAMESPACE -o jsonpath='{.spec.containers[0].name}')
  echo "Pinging from pod: $POD, container: $CONTAINER"
  # Creating a unique log file for each pod to avoid conflicts
  LOGFILE="ping-$(date +%s)-$POD.log"
  kubectl exec $POD -n $NAMESPACE -c $CONTAINER -- sh -c "ping -I uesimtun0 google.com > /tmp/$LOGFILE 2>&1 &"
  echo "Ping initiated in pod: $POD, container: $CONTAINER. Logs at /tmp/$LOGFILE"
done
