output "kube_config" {
  value     = azurerm_kubernetes_cluster.rm_aks_dev.kube_config_raw
  sensitive = true
}
