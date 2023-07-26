#!/bin/bash
docker network create backendnetwork
docker-compose -f apps/ai/server/dataherald/docker-compose.yml up --build -d
sleep 5
python3 apps/ai/clients/benchmark-tool/main.py -u