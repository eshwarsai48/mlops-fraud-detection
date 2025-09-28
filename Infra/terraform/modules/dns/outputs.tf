output "fqdn" {
  description = "FQDN created for the app"
  value       = "${var.subdomain}.${azurerm_dns_zone.zone.name}"
}

output "name_servers" {
  description = "Azure DNS nameservers to set at the registrar"
  value       = azurerm_dns_zone.zone.name_servers
}
