# FractalTrader - Makefile
# Quick commands for cloud deployment and management
#
# Platform-specific targets:
#   make aws-*     - AWS deployment (Dockerfile.aws, docker-compose.aws.yml)
#   make cloud-*   - Multi-platform (Dockerfile.cloud, docker-compose.cloud.yml)
#   make *         - Default (same as cloud-*)

.PHONY: help build start stop restart logs status report clean

# Default compose file (cloud = multi-platform)
COMPOSE_FILE ?= docker-compose.cloud.yml
DOCKERFILE ?= Dockerfile.cloud
CONTAINER_NAME ?= fractal-trader-production

# AWS-specific settings
AWS_COMPOSE_FILE = docker-compose.aws.yml
AWS_DOCKERFILE = Dockerfile.aws
AWS_CONTAINER_NAME = fractal-trader-aws

# Default target
help:
	@echo "FractalTrader Cloud Deployment Commands"
	@echo ""
	@echo "🚀 QUICK START (AWS - RECOMMENDED):"
	@echo "  make aws-setup      - First time AWS setup"
	@echo "  make aws-start      - Start bot on AWS"
	@echo "  make aws-logs       - View AWS bot logs"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - First time setup (.env configuration)"
	@echo "  make aws-setup      - AWS-specific setup"
	@echo ""
	@echo "Docker Operations (Default/Cloud):"
	@echo "  make build          - Build Docker image (multi-arch)"
	@echo "  make start          - Start bot (detached)"
	@echo "  make stop           - Stop bot"
	@echo "  make restart        - Restart bot"
	@echo ""
	@echo "Docker Operations (AWS):"
	@echo "  make aws-build      - Build AWS-optimized image"
	@echo "  make aws-start      - Start bot on AWS"
	@echo "  make aws-stop       - Stop AWS bot"
	@echo "  make aws-restart    - Restart AWS bot"
	@echo ""
	@echo "Monitoring (Default/Cloud):"
	@echo "  make logs           - View logs (follow)"
	@echo "  make logs-tail      - View last 100 lines"
	@echo "  make status         - Bot status"
	@echo "  make report         - Performance report"
	@echo "  make stats          - Docker container stats"
	@echo ""
	@echo "Monitoring (AWS):"
	@echo "  make aws-logs       - View AWS logs (follow)"
	@echo "  make aws-status     - AWS bot status"
	@echo "  make aws-report     - AWS performance report"
	@echo "  make aws-stats      - AWS container stats"
	@echo ""
	@echo "Management:"
	@echo "  make portainer      - Start Portainer web UI (port 9000)"
	@echo "  make aws-portainer  - Start Portainer for AWS"
	@echo "  make shell          - Shell into running container"
	@echo "  make aws-shell      - Shell into AWS container"
	@echo "  make clean          - Clean up stopped containers and images"
	@echo ""
	@echo "Development:"
	@echo "  make test           - Run tests in Docker"
	@echo "  make dev            - Start development environment"

# Setup
setup:
	@echo "Setting up FractalTrader..."
	@if [ ! -f .env ]; then \
		cp .env.cloud.example .env; \
		echo "✓ Created .env file"; \
		echo "⚠️  Please edit .env and configure your credentials:"; \
		echo "   nano .env"; \
	else \
		echo "✓ .env already exists"; \
	fi

# Docker operations
build:
	@echo "Building Docker image..."
	docker build -f Dockerfile.cloud -t fractal-trader:latest .

start: setup
	@echo "Starting FractalTrader bot..."
	docker compose -f docker-compose.cloud.yml up -d
	@echo "✓ Bot started"
	@echo "View logs: make logs"

stop:
	@echo "Stopping FractalTrader bot..."
	docker compose -f docker-compose.cloud.yml down
	@echo "✓ Bot stopped"

restart:
	@echo "Restarting FractalTrader bot..."
	docker compose -f docker-compose.cloud.yml restart
	@echo "✓ Bot restarted"

# Monitoring
logs:
	@echo "Following logs (Ctrl+C to exit)..."
	docker compose -f docker-compose.cloud.yml logs -f

logs-tail:
	@echo "Last 100 log lines:"
	docker compose -f docker-compose.cloud.yml logs --tail=100

status:
	@echo "Bot Status:"
	@docker exec -it fractal-trader-production python -m live.cli status || echo "Bot is not running"

report:
	@echo "Generating performance report..."
	@docker exec -it fractal-trader-production python -m live.cli report || echo "No trading data available"

stats:
	@echo "Container resource usage:"
	docker stats fractal-trader-production --no-stream

# Management
portainer:
	@echo "Starting Portainer web UI..."
	docker compose -f docker-compose.cloud.yml --profile management up -d
	@echo "✓ Portainer started"
	@echo "Access at: http://localhost:9000"
	@echo "(or http://YOUR_SERVER_IP:9000 if remote)"

shell:
	@echo "Opening shell in container..."
	docker exec -it fractal-trader-production bash

clean:
	@echo "Cleaning up Docker resources..."
	docker compose -f docker-compose.cloud.yml down
	docker system prune -f
	@echo "✓ Cleanup complete"

# Development
test:
	@echo "Running tests..."
	docker run --rm \
		-v $(PWD):/app \
		fractal-trader:latest \
		python -m pytest tests/ -v --tb=short

dev:
	@echo "Starting development environment..."
	docker compose up -d
	@echo "✓ Development environment started"
	@echo "Access shell: docker exec -it fractal-trader-dev bash"

# Build multi-arch (requires buildx)
build-multiarch:
	@echo "Building multi-architecture image..."
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		-f Dockerfile.cloud \
		-t fractal-trader:latest \
		.
	@echo "✓ Multi-arch build complete"

# ============================================================
# AWS-SPECIFIC TARGETS (Recommended for production)
# ============================================================

aws-setup:
	@echo "AWS Setup..."
	@if [ ! -f .env ]; then \
		cp .env.cloud.example .env; \
		echo "✓ Created .env file"; \
		echo "⚠️  Please edit .env and configure your credentials:"; \
		echo "   nano .env"; \
	else \
		echo "✓ .env already exists"; \
	fi

aws-build:
	@echo "Building AWS-optimized Docker image..."
	docker build -f $(AWS_DOCKERFILE) -t fractal-trader:aws .
	@echo "✓ AWS image built"

aws-start: aws-setup
	@echo "Starting FractalTrader on AWS..."
	docker compose -f $(AWS_COMPOSE_FILE) up -d
	@echo "✓ Bot started"
	@echo "View logs: make aws-logs"

aws-stop:
	@echo "Stopping AWS bot..."
	docker compose -f $(AWS_COMPOSE_FILE) down
	@echo "✓ Bot stopped"

aws-restart:
	@echo "Restarting AWS bot..."
	docker compose -f $(AWS_COMPOSE_FILE) restart
	@echo "✓ Bot restarted"

aws-logs:
	@echo "Following AWS logs (Ctrl+C to exit)..."
	docker compose -f $(AWS_COMPOSE_FILE) logs -f

aws-logs-tail:
	@echo "Last 100 log lines (AWS):"
	docker compose -f $(AWS_COMPOSE_FILE) logs --tail=100

aws-status:
	@echo "AWS Bot Status:"
	@docker exec -it $(AWS_CONTAINER_NAME) python -m live.cli status || echo "Bot is not running"

aws-report:
	@echo "Generating AWS performance report..."
	@docker exec -it $(AWS_CONTAINER_NAME) python -m live.cli report || echo "No trading data available"

aws-stats:
	@echo "AWS Container resource usage:"
	docker stats $(AWS_CONTAINER_NAME) --no-stream

aws-portainer:
	@echo "Starting Portainer for AWS..."
	docker compose -f $(AWS_COMPOSE_FILE) --profile management up -d
	@echo "✓ Portainer started"
	@echo "Access at: http://localhost:9000"

aws-shell:
	@echo "Opening shell in AWS container..."
	docker exec -it $(AWS_CONTAINER_NAME) bash

# Quick alias for most common AWS operations
aws: aws-start

aws-update:
	@echo "Updating AWS bot..."
	git pull
	docker compose -f $(AWS_COMPOSE_FILE) up -d --build
	@echo "✓ AWS bot updated"
