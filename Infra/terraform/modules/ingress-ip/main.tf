resource "azurerm_public_ip" "ingress_ip" {
  name                = "fraud-api-ingress-ip"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"
}

