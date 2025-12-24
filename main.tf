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


provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Usa apenas data sources para ler a infraestrutura atual
# Assim o terraform não tenta recriar ou alterar a VM

data "google_compute_instance" "marinheiros" {
  project = var.project_id
  zone    = var.zone
  name    = var.instance_name
}

output "instance_ip" {
  description = "IP público atual da VM"
  value       = data.google_compute_instance.marinheiros.network_interface[0].access_config[0].nat_ip
}
