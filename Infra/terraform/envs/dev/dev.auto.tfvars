resource_group_name    = "mlops-dev-rg"
location               = "East US"

# ACR must be 5-50 chars, lowercase alphanumeric, globally unique
acr_name   = "mlopsdevacr2025"
acr_sku    = "Basic"

# AKS (only used if you enable module)
aks_name   = "mlops-dev-aks"
node_size  = "Standard_B2s"
node_count = 2

# DNS
domain_name        = "myapp.it.com"
ingress_public_ip  = "20.185.111.230"

az role assignment list \
  --assignee a9f2d354-7481-43ca-8bf9-f9c69d7a4657 \
  --scope /subscriptions/6a2461a4-b5bf-4d35-97cb-0184247fe647/resourceGroups/MC_mlops-dev-rg_mlops-aks_westus2 \
  --query "[].roleDefinitionName" -o tsv

az aks show \
  --name mlops-dev-aks \
  --resource-group mlops-dev-rg \
  --query nodeResourceGroup \
  -o tsv
