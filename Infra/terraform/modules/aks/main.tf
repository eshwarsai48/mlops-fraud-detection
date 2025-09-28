
resource "azurerm_kubernetes_cluster" "rm_aks_dev" {
  name                = var.aks_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "${var.aks_name}-dns"

  default_node_pool {
    name       = "default"
    node_count = var.node_count
    vm_size    = var.node_size
  }

  identity { type = "SystemAssigned" }
}

resource "azurerm_role_assignment" "aks_acr_pull" {
  principal_id         = azurerm_kubernetes_cluster.rm_aks_dev.kubelet_identity[0].object_id
  role_definition_name = "AcrPull"
  scope                = var.acr_id
}


data "azurerm_resource_group" "dev_rg" {
  name = var.resource_group_name
}

resource "azurerm_role_assignment" "aks_network_contributor" {
  principal_id         = azurerm_kubernetes_cluster.rm_aks_dev.identity[0].principal_id
  role_definition_name = "Network Contributor"
  scope                = data.azurerm_resource_group.dev_rg.id
}

