variable "branch_name" { type= string }

variable "sha" { type= string }

variable "mongodb_name" {
  description = "mongodb_name"
  type        = string
}
variable "mongodb_uri" {
  description = "mongodb_uri"
  type        = string
}
variable "index_name" {
  description = "index_name"
  type        = string
}

variable "vpc_id" {
  description = "vpc_id"
  type        = string
}

variable "private_subnet_1_id" {
  description = "private_subnet_1_id"
  type        = string
}

variable "private_subnet_2_id" {
  description = "private_subnet_2_id"
  type        = string
}

variable "public_subnet_1_id" {
  description = "public_subnet_1_id"
  type        = string
}

variable "public_subnet_2_id" {
  description = "public_subnet_2_id"
  type        = string
}

variable "ecs_security_group_id" {
  description = "security_group_id"
  type        = string
}