resource "azurerm_resource_group" "rg_dev" {
  name     = var.resource_group_name
  location = var.location
}
