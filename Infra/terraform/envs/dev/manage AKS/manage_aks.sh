#!/bin/bash

# === CONFIGURATION ===
RESOURCE_GROUP="mlops-dev-rg"
CLUSTER_NAME="mlops-dev-aks"
NODEPOOL_NAME="default"
NODE_SIZE="Standard_B2s"
NODE_COUNT=1

# === FUNCTIONS ===
start_cluster() {
  echo "🚀 Starting AKS cluster..."
  az aks start --name $CLUSTER_NAME --resource-group $RESOURCE_GROUP
  echo "⏳ Waiting for cluster to stabilize..."
  sleep 240
  echo "✅ Cluster started."
  check_nodes
}

stop_cluster() {
  echo "🛑 Stopping AKS cluster (this will save costs)..."
  az aks stop --name $CLUSTER_NAME --resource-group $RESOURCE_GROUP
  echo "✅ Cluster stopped. You are no longer billed for compute."
}

check_nodes() {
  echo "🔍 Checking node status..."
  NODE_COUNT_K8S=$(kubectl get nodes --no-headers 2>/dev/null | wc -l)
  if [ "$NODE_COUNT_K8S" -eq 0 ]; then
    echo "⚠️  No nodes found in cluster. Attempting to recreate node pool..."
    recreate_nodepool
  else
    echo "✅ Nodes detected:"
    kubectl get nodes
  fi
}

recreate_nodepool() {
  echo "♻️  Recreating AKS node pool..."
  az aks nodepool delete \
    --resource-group $RESOURCE_GROUP \
    --cluster-name $CLUSTER_NAME \
    --name $NODEPOOL_NAME \
    --yes --no-wait

  echo "⏳ Waiting for deletion..."
  sleep 60

  az aks nodepool add \
    --resource-group $RESOURCE_GROUP \
    --cluster-name $CLUSTER_NAME \
    --name $NODEPOOL_NAME \
    --mode System \
    --node-count $NODE_COUNT \
    --node-vm-size $NODE_SIZE

  echo "✅ Node pool recreated. Wait a few minutes and recheck:"
  echo "   kubectl get nodes"
}

status_cluster() {
  echo "📊 Cluster power state:"
  az aks show \
    --name $CLUSTER_NAME \
    --resource-group $RESOURCE_GROUP \
    --query powerState.code \
    --output tsv
}

# === MAIN MENU ===
case "$1" in
  start)
    start_cluster
    ;;
  stop)
    stop_cluster
    ;;
  status)
    status_cluster
    ;;
  check)
    check_nodes
    ;;
  *)
    echo "Usage: $0 {start|stop|status|check}"
    ;;
esac
