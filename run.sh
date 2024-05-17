#!/bin/bash

docker network create dataherald_network

docker-compose -p dataherald -f services/engine/docker-compose.yml up --build -d;
docker-compose -p dataherald -f services/enterprise/docker-compose.yml up --build -d;
docker-compose -p dataherald -f services/slackbot/docker-compose.yml up --build -d;
docker-compose -p dataherald -f services/admin-console/docker-compose.yml up --build -d;