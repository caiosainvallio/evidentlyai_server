build:
	docker-compose build

run:
	docker-compose up -d

stop:
	docker-compose down

logs:
	docker-compose logs -f

logs-evidently:
	docker-compose logs -f evidently-service

logs-minio:
	docker-compose logs -f minio

restart:
	docker-compose restart

status:
	docker-compose ps

demo:
	python remote_demo_project.py

clear_all:
	docker-compose down --rmi all --volumes --remove-orphans

help:
	@echo "EvidentlyAI + MinIO Docker Compose Commands:"
	@echo ""
	@echo "make build       - build the docker images"
	@echo "make run         - run the docker containers in detached mode"
	@echo "make stop        - stop the docker containers"
	@echo "make restart     - restart all services"
	@echo "make status      - show status of all containers"
	@echo "make logs        - show logs of all containers"
	@echo "make logs-evidently - show logs of evidently service only"
	@echo "make logs-minio  - show logs of minio service only"
	@echo "make demo        - run the demo project script"
	@echo "make clear_all   - clear all containers, images, volumes and orphans"
	@echo "make help        - show this help message"
	@echo ""
	@echo "Services will be available at:"
	@echo "  EvidentlyAI UI: http://localhost:8000"
	@echo "  MinIO Console:  http://localhost:9001 (admin/minioadmin123)" 