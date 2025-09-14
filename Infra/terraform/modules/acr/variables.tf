variable "acr_name" {
  type        = string
  description = "ACR name (globally unique, 5-50 lowercase alphanumeric)"
}

variable "resource_group_name" {
  type        = string
  description = "Resource group for ACR"
}

variable "location" {
  type        = string
  description = "Azure region"
}

variable "sku" {
  type        = string
  default     = "Basic"
  description = "ACR SKU: Basic, Standard, Premium"
}
