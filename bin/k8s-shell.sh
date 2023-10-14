#!/bin/bash

# function to print usage message
function usage {
  echo "Usage: $0 keyword [namespace]"
  echo "       keyword: a string that identifies the pod you want to access, e.g. amf, smf, upf"
  echo "       namespace (optional): the Kubernetes namespace where the pod is running"
  echo "If no namespace is specified, a namespace picker will be displayed."
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

# Function to prompt the user to select a container from a list
select_container() {
  echo "Select a container:"
  select CONTAINER in $(kubectl get pod $POD -n $NAMESPACE -o jsonpath='{range .spec.containers[*]}{.name}{"\n"}{end}')
  do
    if [ -n "$CONTAINER" ]
    then
      break
    fi
  done
}

# Display help message if no arguments provided
if [ "$#" -eq 0 ]
then
  usage
  exit 1
fi

POD_KEYWORD=$1

# Prompt for namespace if not specified
if [ "$#" -eq 1 ]
then
  select_namespace
else
  NAMESPACE=$2
fi

POD=$(kubectl get pods -n $NAMESPACE | grep "$POD_KEYWORD" | awk '{print $1}')

if [ -z "$POD" ]
then
  echo "No pod found with keyword: $POD_KEYWORD in namespace: $NAMESPACE"
  exit 1
fi

CONTAINER_COUNT=$(kubectl get pod $POD -n $NAMESPACE -o jsonpath='{range .spec.containers[*]}{.name}{"\n"}{end}' | wc -l)

if [ "$CONTAINER_COUNT" -eq 1 ]
then
  CONTAINER=$(kubectl get pod $POD -n $NAMESPACE -o jsonpath='{.spec.containers[0].name}')
else
  select_container
fi

# Try bash shell, fallback to sh
SHELLS=("bash" "sh")
for SHELL in "${SHELLS[@]}"
do
  if kubectl exec $POD -n $NAMESPACE -c $CONTAINER -- $SHELL -c 'exit 0' > /dev/null 2>&1
  then
    kubectl exec -it $POD -n $NAMESPACE -c $CONTAINER -- $SHELL
    exit 0
  fi
done

echo "No supported shell found in pod: $POD"
exit 1

