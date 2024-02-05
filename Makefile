up:
	docker compose -f docker-compose.yaml up --build -d
down:
	docker compose -f docker-compose.yaml down && docker network prune --force
up_tests_container:
	docker compose -f docker-compose-tests.yaml up --build -d
run_tests:
	docker exec -it fastapi_app_tests /bin/sh -c 'export PYTHONPATH=/fastapi_app/api_v1 && pytest -v -rE tests/'
run_menu_tests:
	docker exec -it fastapi_app_tests /bin/sh -c 'export PYTHONPATH=/fastapi_app/api_v1 && pytest -v -rE tests/test_menu_crud.py'
run_submenu_tests:
	docker exec -it fastapi_app_tests /bin/sh -c 'export PYTHONPATH=/fastapi_app/api_v1 && pytest -v -rE tests/test_submenu_crud.py'
run_dishes_tests:
	docker exec -it fastapi_app_tests /bin/sh -c 'export PYTHONPATH=/fastapi_app/api_v1 && pytest -v -rE tests/test_dish_crud.py'
run_check_quan_of_dishes_and_submenus_tests:
	docker exec -it fastapi_app_tests /bin/sh -c 'export PYTHONPATH=/fastapi_app/api_v1 && pytest -v -rE tests/test_quan_of_dishes_and_submenus.py'
