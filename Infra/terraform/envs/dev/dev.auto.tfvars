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