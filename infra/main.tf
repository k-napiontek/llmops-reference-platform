    resource "azurerm_resource_group" "llmops" {
      name     = "rg-llmops-platform-dev"
      location = "polandcentral"
    }

    resource "azurerm_cognitive_account" "foundry" {
      name                       = "aoai-llmops-resource"
      location                   = azurerm_resource_group.llmops.location
      resource_group_name        = azurerm_resource_group.llmops.name
      kind                       = "AIServices"
      sku_name                   = "S0"
      custom_subdomain_name      = "aoai-llmops-resource"
      project_management_enabled = true

      identity {
        type = "SystemAssigned"
      }
    }

    resource "azurerm_cognitive_deployment" "gpt_5_4_mini" {
      name                   = "gpt-5.4-mini"
      cognitive_account_id   = azurerm_cognitive_account.foundry.id
      rai_policy_name        = "Microsoft.DefaultV2"
      version_upgrade_option = "OnceNewDefaultVersionAvailable"

      model {
        format  = "OpenAI"
        name    = "gpt-5.4-mini"
        version = "2026-03-17"
      }

      sku {
        name     = "GlobalStandard"
        capacity = 30
      }
    }