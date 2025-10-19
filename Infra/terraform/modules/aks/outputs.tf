output "kube_config" {
  value     = azurerm_kubernetes_cluster.rm_aks_dev.kube_config_raw
  sensitive = true
}
output "cluster_principal_id" {
  value = azurerm_kubernetes_cluster.rm_aks_dev.identity[0].principal_id
}

# Kubelet identity – used for ACR pulls
output "kubelet_object_id" {
  value = azurerm_kubernetes_cluster.rm_aks_dev.kubelet_identity[0].object_id
}

output "cluster_id" {
  description = "AKS cluster ID"
  value       = azurerm_kubernetes_cluster.rm_aks_dev.id
}
