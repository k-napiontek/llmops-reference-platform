output "foundry_endpoint" {
  description = "Base URL of the Azure AI Foundry resource"
  value       = azurerm_cognitive_account.foundry.endpoint
}