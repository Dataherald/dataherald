initial-script:
	docker exec server-app-1 python3 -m database.scripts.initial_setup

start-dataherald:
	docker-compose \
		-f ./dataherald/docker-compose.yml \
		up --build -d

start-server:
	docker-compose \
		up --build -d

start: start-server start-dataherald initial-script
