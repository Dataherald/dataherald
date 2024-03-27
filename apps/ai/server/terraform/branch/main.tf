terraform {
  required_providers {
    aws = {
      source  = "aws"
      version = "4.1.0"
    }

    pinecone = {
      source  = "skyscrapr/pinecone"
      version = "0.5.1"
    }
  }
  backend "s3" {
    bucket = "terraform-states2"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}
provider "pinecone" {}

module "aws_ecs" {
  source                = "./aws_ecs"
  branch_name           = var.branch_name
  sha                   = var.sha
  mongodb_uri           = replace(var.mongodb_uri, "mongodb+srv://", "mongodb+srv://${var.mongodb_username}:${var.mongodb_password}@")
  mongodb_name          = var.mongodb_name
  index_name            = var.index_name
  vpc_id                = var.vpc_id
  private_subnet_1_id   = var.private_subnet_1_id
  private_subnet_2_id   = var.private_subnet_2_id
  public_subnet_1_id    = var.public_subnet_1_id
  public_subnet_2_id    = var.public_subnet_2_id
  ecs_security_group_id = var.ecs_security_group_id
}

module "pinecone_index" {
  source     = "./pinecone_index"
  index_name = var.index_name
}
