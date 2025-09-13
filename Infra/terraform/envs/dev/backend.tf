terraform {
  backend "azurerm" {
    resource_group_name  = "mlops-tfstate-rg"         # from bootstrap output
    storage_account_name = "mlopstfstatesa2025"       # from bootstrap output
    container_name       = "tfstate-container"        # from bootstrap output
    key                  = "dev.terraform.tfstate"    # unique per env (dev/prod/staging)
  }
}
