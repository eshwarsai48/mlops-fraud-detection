variable "resource_group_name" {
  description = "Resource group where the DNS zone will live"
  type        = string
}

variable "domain_name" {
  description = "The apex/root domain (e.g., myapp.com)"
  type        = string
}

variable "subdomain" {
  description = "Subdomain to create (e.g., fraud-api)"
  type        = string
  default     = "fraud-api"
}

variable "ingress_ipv4" {
  description = "Public IPv4 of your ingress controller Service (EXTERNAL-IP)"
  type        = string
}

variable "ttl" {
  description = "DNS TTL in seconds"
  type        = number
  default     = 300
}
