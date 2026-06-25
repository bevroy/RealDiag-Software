.PHONY: help install test clean build docker-build docker-up docker-down lint

help:
	@echo "RealDiag-Software - Available Make Targets"
	@echo "==========================================="
	@echo "  install      - Install dependencies"
	@echo "  test         - Run test suite"
	@echo "  clean        - Remove build artifacts"
	@echo "  build        - Build distribution packages"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-up    - Start Docker services"
	@echo "  docker-down  - Stop Docker services"
	@echo "  lint         - Run linters (if installed)"
	@echo "  run          - Run the CLI tool"

install:
	pip install -r requirements.txt

test:
	python -m unittest discover -s tests -p "test_*.py" -v

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf reports/*.json 2>/dev/null || true

build: clean
	python setup.py sdist bdist_wheel

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

lint:
	@command -v flake8 >/dev/null 2>&1 && flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || echo "flake8 not installed"
	@command -v black >/dev/null 2>&1 && black --check . || echo "black not installed"

run:
	python main.py --all
