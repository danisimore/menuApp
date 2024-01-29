up:
	docker compose -f docker-compose.yaml up --build -d
down:
	docker compose -f docker-compose.yaml down && docker network prune --force
run_tests:
	docker exec -it fastapi_app /bin/sh -c 'export PYTHONPATH=/fastapi_app/api_v1 && pytest -v -rE tests/'
