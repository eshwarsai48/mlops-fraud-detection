resource "random_id" "suffix" {
  byte_length = 2
}

resource "azurerm_storage_account" "model_store" {
  name                     = "${var.storage_account_name}${random_id.suffix.hex}"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  allow_blob_public_access = false

  tags = var.tags
}

resource "azurerm_storage_container" "model_container" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.model_store.name
  container_access_type = "private"
}
