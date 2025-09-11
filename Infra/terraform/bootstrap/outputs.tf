output "tfstate_rg_name" {
  value = azurerm_resource_group.tfstate_rg.name
}

output "tfstate_sa_name" {
  value = azurerm_storage_account.tfstate_sa.name
}

output "tfstate_container_name" {
  value = azurerm_storage_container.tfstate_container.name
}
