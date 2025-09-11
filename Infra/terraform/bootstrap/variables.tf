variable "tfstate_rg_name" {
  type        = string
  description = "Resource Group for Terraform state"
  default     = "mlops-tfstate-rg"
}

variable "tfstate_location" {
  type        = string
  description = "Azure region for the state resources"
  default     = "East US"
}

variable "tfstate_sa_name" {
  type        = string
  description = "Globally-unique Storage Account name for state (lowercase, 3-24 chars)"
}

variable "tfstate_container_name" {
  type        = string
  description = "Blob container name for state"
  default     = "tfstate"
}
