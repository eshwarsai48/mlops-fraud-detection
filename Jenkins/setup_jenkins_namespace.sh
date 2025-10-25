#!/bin/bash
# ==========================================================
# Script: setup_jenkins_namespace.sh
# Purpose: Connect to AKS and create Jenkins namespace
# ==========================================================

# --- User-defined variables (replace if needed) ---
RG="mlops-dev-rg"          # Resource Group name
AKS="mlops-dev-aks"        # AKS Cluster name
NS="jenkins"           # Namespace name

# --- Connect to AKS cluster ---
echo "🔹 Connecting to AKS cluster: $AKS in resource group: $RG..."
az aks get-credentials -g "$RG" -n "$AKS" --overwrite-existing

if [ $? -ne 0 ]; then
  echo "❌ Failed to get AKS credentials. Please check your Azure login or resource names."
  exit 1
fi

# --- Create Jenkins namespace if it doesn't exist ---
echo "🔹 Checking if namespace '$NS' exists..."
if kubectl get namespace "$NS" >/dev/null 2>&1; then
  echo "✅ Namespace '$NS' already exists."
else
  echo "🚀 Creating namespace '$NS'..."
  kubectl create namespace "$NS"
  echo "✅ Namespace '$NS' created successfully."
fi

echo "🎯 Jenkins namespace setup complete!"
