variable "branch_name" {
  type    = string
  default = ""
}

variable "vpc_id" {
  type = string
  default = ""
}

variable "subnet_1_id" {
  type = string
  default = ""
}

variable "subnet_2_id" {
  type = string
  default = ""
}

variable "ecs_security_group_id" {
  type = string
  default = ""
}

variable "sha" {
  type    = string
  default = ""
}

variable "index_name" {
  description = "index_name"
  type        = string
}

variable "mongodb_uri" {
  description = "mongodb_uri"
  type        = string
  default     = "mongodb://localhost:27017"
}

variable "mongodb_name" {
  description = "mongodb_name"
  type        = string
  default     = "dataherald"
}

variable "mongodb_username" {
  description = "mongodb_username"
  type        = string
  default     = "admin"
}

variable "mongodb_password" {
  description = "mongodb_password"
  type        = string
  default     = "admin"
}
