#!/bin/bash
ACTION=$1 # up or down
RG="mlops-dev-rg"
CLUSTER="mlops-dev-aks"
NODEPOOL="default"

if [ "$ACTION" == "up" ]; then
  echo "Scaling AKS up..."
  az aks nodepool scale --resource-group $RG --cluster-name $CLUSTER --name $NODEPOOL --node-count 1
elif [ "$ACTION" == "down" ]; then
  echo "Scaling AKS down..."
  az aks nodepool scale --resource-group $RG --cluster-name $CLUSTER --name $NODEPOOL --node-count 0
else
  echo "Usage: ./aks_scale.sh [up|down]"
fi
