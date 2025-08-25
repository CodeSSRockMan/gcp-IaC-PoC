variable "vpc_name" {
  description = "Name of the VPC network"
  type        = string
}

variable "subnet_name" {
  description = "Name of the private subnet"
  type        = string
}

variable "subnet_cidr" {
  description = "CIDR range for the private subnet"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "api_subnet_cidr" {
  description = "CIDR range for the API service subnet allowed to access resources"
  type        = string
}
