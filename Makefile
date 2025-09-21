SHELL := /bin/bash

# Konfiguratsiya (istalganini chaqirish paytida override qiling: make run_dev PORT=9000)
APP     ?= app.main:app
HOST    ?= 127.0.0.1
PORT    ?= 8000
WORKERS ?= 2
MSG     ?= init

UV ?= uv

.PHONY: help run_dev run_prod alembic_rev upgrade downgrade heads history migrate fmt lint clean sync env

help:
	@echo "Targets:"
	@echo "  make run_dev                 	# FastAPI dev server (auto-reload)"
	@echo "  make run_prod                	# Uvicorn (production-ish)"
	@echo "  make alembic_rev MSG=\"msg\"  	# Alembic revision --autogenerate"
	@echo "  make upgrade                 	# alembic upgrade head"
	@echo "  make downgrade               	# alembic downgrade -1"
	@echo "  make heads|history           	# ko'rish"
	@echo "  make migrate MSG=\"msg\"      	# revision + upgrade"
	@echo "  make fmt|lint|clean          	# yordamchi"
	@echo "  make sync                    	# uv sync (deps o'rnatish)"
	@echo "  make env                     	# muhit o'zgaruvchilarini ko'rsatish"

# Muhit
sync:
	$(UV) sync

env:
	@echo "APP=$(APP)"
	@echo "HOST=$(HOST) PORT=$(PORT) WORKERS=$(WORKERS)"
	@echo "MSG=$(MSG)"

# Dev server (reload bilan)
run_dev:
	$(UV) run fastapi dev app/main.py --host $(HOST) --port $(PORT)

# Prod(ga yaqin) server: uvicorn, reload YO'Q
run_prod:
	$(UV) run uvicorn $(APP) --host $(HOST) --port $(PORT) --workers $(WORKERS) --proxy-headers

# Alembic
alembic_rev:
	$(UV) run alembic revision --autogenerate -m "$(MSG)"

upgrade:
	$(UV) run alembic upgrade head

downgrade:
	$(UV) run alembic downgrade -1

heads:
	$(UV) run alembic heads

history:
	$(UV) run alembic history

# Tez yo'l: revision + upgrade
migrate: alembic_rev upgrade

# Ixtiyoriy: format/lint/clean (ruff/black o'rnatilgan bo'lishi kerak)
fmt:
	-$(UV) run ruff check --fix .
	-$(UV) run black .

lint:
	$(UV) run ruff check .
	$(UV) run black --check .

clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} + ; \
	find . -name "*.pyc" -delete
