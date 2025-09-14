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
