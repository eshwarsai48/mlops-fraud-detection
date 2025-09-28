output "resource_group"   {
  value = module.resource_group.name
}
output "acr_login_server" {
  value = module.acr.login_server
}
output "aks_kubeconfig" {
  value = module.aks.kube_config
  sensitive = true
}
output "aks_cluster_principal_id" {
  value = module.aks.cluster_principal_id
}

output "aks_kubelet_object_id" {
  value = module.aks.kubelet_object_id
}

output "dns_zone_nameservers" {
  value = module.dns.name_servers
}

output "app_fqdn" {
  value = module.dns.fqdn
}
output "ingress_static_ip" {
  value = module.ingress_ip.ingress_ip
}

