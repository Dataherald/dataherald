.PHONY: all test clean

DOCKER_COMPOSE_PROJECT    ?= bariloche

define container-exec
	docker exec \
		-it $(DOCKER_COMPOSE_PROJECT)_backend_1 \
			sh -c '$(1)'
endef

start:
	docker-compose \
		-p $(DOCKER_COMPOSE_PROJECT) \
		-f docker-compose.yml \
		up -d


stop:
	docker-compose stop

# First migration
migrate:
	$(call container-exec,python3 -m src.db.static_page_generation.bariloche_cli migrate-all-collections)
