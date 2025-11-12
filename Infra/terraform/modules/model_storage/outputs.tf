output "storage_account_name" {
  description = "The name of the Azure Storage Account used for models."
  value       = azurerm_storage_account.model_store.name
}

output "container_name" {
  description = "The name of the Azure Blob container for models."
  value       = azurerm_storage_container.model_container.name
}

output "connection_string" {
  description = "Primary connection string for the model storage account."
  value       = azurerm_storage_account.model_store.primary_connection_string
  sensitive   = true
}
