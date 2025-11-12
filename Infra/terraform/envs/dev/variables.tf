variable "resource_group_name"   {
  type = string
}
variable "location"  {
  type = string
  default = "East US"
}
variable "acr_name"  {
  type = string
}
variable "acr_sku"   {
  type = string
  default = "Basic"
}
variable "aks_name"  {
  type = string
  default = "mlops-dev-aks"
}
variable "node_count"{
  type = number
  default = 1
}
variable "node_size" {
  type = string
  default = "Standard_B2s"
}

variable "domain_name" {
  description = "Apex domain (e.g., myapp.com)"
  type        = string
}

variable "ingress_public_ip" {
  description = "Ingress controller EXTERNAL-IP"
  type        = string
}
variable "prefix" {
  description = "Prefix used for naming resources"
  default     = "fraud" # or whatever short name you prefer
}

variable "tags" {
  description = "A map of tags applied to all resources."
  type        = map(string)
  default = {
    environment = "dev"
    owner       = "eshwarsai"
    project     = "mlops-fraud-detection"
  }
}

