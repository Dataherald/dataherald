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

variable "branch_name" { type= string }

variable "pinecone_index_name" {
  description = "pinecone_index_name"
  type        = string
}

variable "mongodb_uri" {
  description = "mongodb_uri"
  type        = string
}

variable "mongodb_name" {
  description = "mongodb_name"
  type        = string
}

variable "mongodb_username" {
  description = "mongodb_username"
  type        = string
}

variable "mongodb_password" {
  description = "mongodb_password"
  type        = string
}

variable "subnet_1_id" {
  description = "subnet_1_id"
  type        = string
  default = "subnet-076afb4a159204349"
}

variable "subnet_2_id" {
  description = "subnet_2_id"
  type        = string
  default = "subnet-0b6b9dbf631131b09"
}

variable "ecs_security_group_id" {
  description = "security_group_id"
  type        = string
  default = "sg-07fac199a96aa3b65"
}

resource "pinecone_index" "my_index" {
  name = var.pinecone_index_name
  dimension = 1536
  metric = "cosine"
  spec = {
    serverless = {
      cloud = "aws"
      region = "us-west-2"
    }
  }
}

locals {
  srv_connection_string = replace(var.mongodb_uri, "mongodb+srv://", "mongodb+srv://${var.mongodb_username}:${var.mongodb_password}@")
}

resource "aws_ecs_task_definition" "my_task_definition" {
  family = "k2-ephemeral-env-${var.branch_name}"
  task_role_arn = "arn:aws:iam::422486916789:role/ecsk2TaskExecutionRole"
  execution_role_arn = "arn:aws:iam::422486916789:role/ecsk2TaskExecutionRole"
  network_mode = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu = "2048"
  memory = "4096"
#  container_definitions = file("task_definition.json")
  container_definitions =<<DEFINITION
[
        {
            "name": "k2-core-ephemeral-env",
            "image": "422486916789.dkr.ecr.us-east-1.amazonaws.com/k2-core-ephemeral-envs:${var.branch_name}",
            "cpu": 1024,
            "memory": 3072,
            "portMappings": [
                {
                    "name": "k2-core-ephemeral-env-80-tcp",
                    "containerPort": 3001,
                    "hostPort": 3001,
                    "protocol": "tcp",
                    "appProtocol": "http"
                }
            ],
            "essential": true,
            "environmentFiles": [
                {
                    "value": "arn:aws:s3:::ecs-k2-core-ephemeral-environment-variables/.env",
                    "type": "s3"
                }
            ],
            "environment": [
              {
                  "name": "CORE_PORT",
                  "value": "3001"
              },
              {
                "name": "MONGODB_DB_NAME",
                "value": "${var.mongodb_name}"
              },
              {
                "name": "MONGODB_URI",
                "value": "${local.srv_connection_string}"
              },
              {
                "name": "GOLDEN_SQL_COLLECTION",
                "value": "${var.pinecone_index_name}"
              }
            ],
            "command": ["sh", "-c", "uvicorn dataherald.app:app --host 0.0.0.0 --port $CORE_PORT --log-config log_config.yml --log-level debug --reload"],
            "mountPoints": [],
            "volumesFrom": [],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-create-group": "true",
                    "awslogs-group": "/ecs/ecs-k2-ephemeral",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        },
        {
            "name": "k2-server-ephemeral-env",
            "image": "422486916789.dkr.ecr.us-east-1.amazonaws.com/k2-server-ephemeral-envs:${var.branch_name}",
            "cpu": 1024,
            "memory": 3072,
            "portMappings": [
                {
                    "name": "k2-server-ephemeral-env-3001-tcp",
                    "containerPort": 80,
                    "hostPort": 80,
                    "protocol": "tcp",
                    "appProtocol": "http"
                }
            ],
            "essential": true,
            "environmentFiles": [
                {
                    "value": "arn:aws:s3:::ecs-k2-server-ephemeral-environment-variables/.env",
                    "type": "s3"
                }
            ],
            "environment": [
              {
                  "name": "K2_CORE_URL",
                  "value": "http://localhost:3001/api/v1"
              },
              {
                "name": "MONGODB_DB_NAME",
                "value": "${var.mongodb_name}"
              },
              {
                "name": "MONGODB_URI",
                "value": "${local.srv_connection_string}"
              }
            ],
            "mountPoints": [],
            "volumesFrom": [],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-create-group": "true",
                    "awslogs-group": "/ecs/ecs-k2-ephemeral",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]
  DEFINITION
}

resource "aws_lb" "my_load_balancer" {
  name               = "${var.branch_name}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = ["sg-07fac199a96aa3b65"]  # Replace with your security group ID
  subnets            = ["subnet-076afb4a159204349", "subnet-0b6b9dbf631131b09"]  # Replace with your subnet IDs
}

resource "aws_lb_target_group" "ecs_target_group" {
  name        = "${var.branch_name}"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = "vpc-09c492a49b76fdf80"
  target_type = "ip"

  health_check {
    path                = "/heartbeat"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 5
    unhealthy_threshold = 2
    matcher             = "200-299"
  }
}

resource "aws_lb_listener" "ecs_listener" {
  load_balancer_arn = aws_lb.my_load_balancer.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_target_group.arn
  }
}

resource "aws_lb_listener" "https_listener" {
  load_balancer_arn = aws_lb.my_load_balancer.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"  # Choose an appropriate SSL policy for your application

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_target_group.arn
  }
  certificate_arn = "arn:aws:acm:us-east-1:422486916789:certificate/0159c510-ecbb-4607-bb4e-0df6be7b44ab"
}

resource "aws_ecs_service" "my_service" {
  name            = "k2-ephemeral-env-${var.branch_name}"
  cluster         = "arn:aws:ecs:us-east-1:422486916789:cluster/k2"
  task_definition = aws_ecs_task_definition.my_task_definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  enable_ecs_managed_tags = true
  wait_for_steady_state   = true

  load_balancer {
    target_group_arn = aws_lb_target_group.ecs_target_group.arn
    container_name   = "k2-server-ephemeral-env"
    container_port   = 80
  }

  network_configuration {
    subnets         = [var.subnet_1_id, var.subnet_2_id]
    security_groups = [var.ecs_security_group_id]
    assign_public_ip = true
  }
}

resource "aws_route53_record" "my_load_balancer_record" {
  zone_id = "Z07539241TW7P7NHVR11T"  # Replace with your Route 53 hosted zone ID
  name    = "${var.branch_name}.api.dataherald.ai"   # Replace with the desired domain name
  type    = "A"
  alias {
    name                   = aws_lb.my_load_balancer.dns_name
    zone_id                = aws_lb.my_load_balancer.zone_id
    evaluate_target_health = true
  }
}
