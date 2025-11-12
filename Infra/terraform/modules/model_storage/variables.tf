variable "storage_account_name" {
  description = "Base name for the model storage account (a random suffix will be added)."
  type        = string
  default     = "mlopsmodelstore"
}

variable "container_name" {
  description = "The name of the storage container where model artifacts will be stored."
  type        = string
  default     = "ml-models"
}

variable "resource_group_name" {
  description = "The resource group where the model storage will be created."
  type        = string
}

variable "location" {
  description = "Azure region where the storage account will be deployed."
  type        = string
}

variable "tags" {
  description = "Optional tags for the resources."
  type        = map(string)
  default     = {}
}
