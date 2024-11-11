#!/bin/bash
NAMESPACE="open5gs"
kubectl get namespace $NAMESPACE 2>/dev/null || kubectl create namespace $NAMESPACE
kubectl delete -k mongodb -n $NAMESPACE
kubectl delete -k networks5g -n $NAMESPACE
kubectl delete --wait=true -k open5gs -n $NAMESPACE

# wait till kubectl get pods -l app=open5gs does not return null
while [ "$(kubectl get pods -n "$NAMESPACE" -l="app=open5gs" -o jsonpath='{.items[*].metadata.name}')" != "" ]; do
    sleep 5
    echo "Waiting for all pods to be deleted in namespace $NAMESPACE ..."
done
echo "All pods deleted in namespace $NAMESPACE."

# kubectl delete namespace $NAMESPACE
# echo "Namespace $NAMESPACE deleted."

echo "open5gs core removed successfully."