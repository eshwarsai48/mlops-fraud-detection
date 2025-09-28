
# Create (host) the DNS zone in Azure
resource "azurerm_dns_zone" "zone" {
  name                = var.domain_name
  resource_group_name = var.resource_group_name
}

# A record: fraud-api.myapp.com -> <INGRESS-IP>
resource "azurerm_dns_a_record" "app" {
  name                = var.subdomain
  zone_name           = azurerm_dns_zone.zone.name
  resource_group_name = var.resource_group_name
  ttl                 = var.ttl
  records             = [var.ingress_ipv4]
}
