variable "aks_name" {
  type = string
}
variable "resource_group_name" {
  type = string
}
variable "location" {
  type = string
  default = "East US"
}
variable "node_count" {
  type = number
  default = 1
}
variable "node_size" {
  type = string
  default = "Standard_B2s"
}
variable "acr_id" {
  type        = string
  description = "ACR resource ID for AcrPull role assignment"
}
