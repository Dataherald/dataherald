terraform {
  required_providers {
    aws = {
      source  = "aws"
      version = "4.1.0"
    }
  }
}

resource "aws_ecs_task_definition" "my_task_definition" {
  family                   = "ai-backend-branch-${var.branch_name}"
  task_role_arn            = "arn:aws:iam::422486916789:role/ecsk2TaskExecutionRole"
  execution_role_arn       = "arn:aws:iam::422486916789:role/ecsk2TaskExecutionRole"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "2048"
  memory                   = "4096"
  #  container_definitions = file("task_definition.json")
  container_definitions = <<DEFINITION
[
        {
            "name": "ai-engine-branch",
            "image": "422486916789.dkr.ecr.us-east-1.amazonaws.com/ai-engine-branch:${var.branch_name}-${var.sha}",
            "cpu": 1024,
            "memory": 3072,
            "portMappings": [
                {
                    "name": "ai-engine-branch-80-tcp",
                    "containerPort": 3001,
                    "hostPort": 3001,
                    "protocol": "tcp",
                    "appProtocol": "http"
                }
            ],
            "essential": true,
            "environmentFiles": [
                {
                    "value": "arn:aws:s3:::ai-engine-branch-environment-variables/.env",
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
                "value": "${var.mongodb_uri}"
              },
              {
                "name": "GOLDEN_SQL_COLLECTION",
                "value": "${var.index_name}"
              }
            ],
            "command": ["sh", "-c", "uvicorn dataherald.app:app --host 0.0.0.0 --port $CORE_PORT --log-config log_config.yml --log-level debug --reload"],
            "mountPoints": [],
            "volumesFrom": [],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-create-group": "true",
                    "awslogs-group": "/ecs/ai-engine-branch",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        },
        {
            "name": "ai-server-branch",
            "image": "422486916789.dkr.ecr.us-east-1.amazonaws.com/ai-server-branch:${var.branch_name}-${var.sha}",
            "cpu": 1024,
            "memory": 3072,
            "portMappings": [
                {
                    "name": "ai-server-branch-3001-tcp",
                    "containerPort": 80,
                    "hostPort": 80,
                    "protocol": "tcp",
                    "appProtocol": "http"
                }
            ],
            "essential": true,
            "environmentFiles": [
                {
                    "value": "arn:aws:s3:::ai-server-branch-environment-variables/.env",
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
                "value": "${var.mongodb_uri}"
              }
            ],
            "mountPoints": [],
            "volumesFrom": [],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-create-group": "true",
                    "awslogs-group": "/ecs/ai-server-branch",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]
  DEFINITION
}

resource "aws_lb" "my_load_balancer" {
  name               = var.branch_name
  internal           = false
  idle_timeout       = 300
  load_balancer_type = "application"
  security_groups    = [var.ecs_security_group_id]
  subnets            = [var.subnet_1_id, var.subnet_2_id]
}

resource "aws_lb_target_group" "ecs_target_group" {
  name        = var.branch_name
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
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
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06" # Choose an appropriate SSL policy for your application

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_target_group.arn
  }
  certificate_arn = "arn:aws:acm:us-east-1:422486916789:certificate/0159c510-ecbb-4607-bb4e-0df6be7b44ab"
}

resource "aws_ecs_service" "my_service" {
  name                    = "ai-backend-branch-${var.branch_name}"
  cluster                 = "arn:aws:ecs:us-east-1:422486916789:cluster/ai"
  task_definition         = aws_ecs_task_definition.my_task_definition.arn
  desired_count           = 1
  launch_type             = "FARGATE"
  enable_ecs_managed_tags = true
  wait_for_steady_state   = true

  load_balancer {
    target_group_arn = aws_lb_target_group.ecs_target_group.arn
    container_name   = "ai-server-branch"
    container_port   = 80
  }

  network_configuration {
    subnets          = [var.subnet_1_id, var.subnet_2_id]
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = true
  }
}

resource "aws_route53_record" "my_load_balancer_record" {
  zone_id = "Z07539241TW7P7NHVR11T"                # Replace with your Route 53 hosted zone ID
  name    = "${var.branch_name}.api.dataherald.ai" # Replace with the desired domain name
  type    = "A"
  alias {
    name                   = aws_lb.my_load_balancer.dns_name
    zone_id                = aws_lb.my_load_balancer.zone_id
    evaluate_target_health = true
  }
}
