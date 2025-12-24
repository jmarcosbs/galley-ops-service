terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

variable "project_id" {
  description = "ID do projeto no Google Cloud"
  type        = string
}

variable "region" {
  description = "Região onde os recursos estão"
  type        = string
}

variable "zone" {
  description = "Zona onde a VM está criada"
  type        = string
}

variable "instance_name" {
  description = "Nome da VM já existente"
  type        = string
  default     = "marinheiros"
}

variable "firewall_name" {
  description = "Nome da regra de firewall que já existe"
  type        = string
  default     = "marinheiros-allow"
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Usa apenas data sources para ler a infraestrutura atual
# Assim o terraform não tenta recriar ou alterar a VM ou firewall

data "google_compute_instance" "marinheiros" {
  project = var.project_id
  zone    = var.zone
  name    = var.instance_name
}

data "google_compute_firewall" "marinheiros" {
  project = var.project_id
  name    = var.firewall_name
}

output "instance_ip" {
  description = "IP público atual da VM"
  value       = data.google_compute_instance.marinheiros.network_interface[0].access_config[0].nat_ip
}

output "firewall_allowed_ports" {
  description = "Lista de portas liberadas na regra de firewall"
  value       = [for rule in data.google_compute_firewall.marinheiros.allow : rule.ports]
}
