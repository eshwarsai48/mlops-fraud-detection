 resource "azurerm_resource_group" "tfstate_rg" {
  name     = var.tfstate_rg_name
  location = var.tfstate_location
}

resource "azurerm_storage_account" "tfstate_sa" {
  name                     = var.tfstate_sa_name
  resource_group_name      = azurerm_resource_group.tfstate_rg.name
  location                 = azurerm_resource_group.tfstate_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "tfstate_container" {
  name                  = var.tfstate_container_name
  storage_account_name  = azurerm_storage_account.tfstate_sa.name
  container_access_type = "private"
}
