#!/bin/bash
cp apps/ai/clients/benchmark-tool/init-files/* apps/ai/server/dataherald/initdb.d/
cp apps/ai/clients/benchmark-tool/init-files/.env apps/ai/server/dataherald/
docker network create backendnetwork
docker-compose -f apps/ai/server/dataherald/docker-compose.yml up --build -d
sleep 10
python3 apps/ai/clients/benchmark-tool/src/datastore_setup.py -u
python3 apps/ai/clients/benchmark-tool/src/main.py -u