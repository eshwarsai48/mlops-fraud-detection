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
output "dns_zone_nameservers" {
  value = module.dns.name_servers
}

output "app_fqdn" {
  value = module.dns.fqdn
}
output "ingress_static_ip" {
  value = module.ingress_ip.ingress_ip
}

