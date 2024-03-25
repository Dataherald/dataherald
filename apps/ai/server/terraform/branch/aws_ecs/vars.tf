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

variable "subnet_1_id" {
  description = "subnet_1_id"
  type        = string
}

variable "subnet_2_id" {
  description = "subnet_2_id"
  type        = string
}

variable "ecs_security_group_id" {
  description = "security_group_id"
  type        = string
}