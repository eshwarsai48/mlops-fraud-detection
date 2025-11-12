module "resource_group" {
  source   = "../../modules/resource_group"
  resource_group_name  = var.resource_group_name
  location = var.location
}

module "acr" {
  source              = "../../modules/acr"
  acr_name            = var.acr_name
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  sku                 = var.acr_sku
}


module "aks" {
   source              = "../../modules/aks"
   aks_name            = var.aks_name
   resource_group_name = module.resource_group.name
   location            = module.resource_group.location
   node_count          = var.node_count
   node_size           = var.node_size
   acr_id              = module.acr.id
 }

module "model_storage" {
  source              = "../../modules/model_storage"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  tags                = var.tags
}


module "dns" {
  source = "../../modules/dns"
  resource_group_name = module.resource_group.name
  domain_name  = var.domain_name
  subdomain    = "fraud-api"
  ingress_ipv4 = module.ingress_ip.ingress_ip
  ttl          = 300
}

module "ingress_ip" {
  source = "../../modules/ingress-ip"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
}

