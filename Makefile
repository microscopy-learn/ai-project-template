.PHONY: setup test lint format eval run demo docker

setup:      ## Install everything and the git hooks
	uv sync --all-extras
	uv run pre-commit install

test:       ## Run unit and API tests
	uv run pytest -q

lint:       ## Check style
	uv run ruff check .
	uv run ruff format --check .

format:     ## Fix style
	uv run ruff check --fix .
	uv run ruff format .

eval:       ## Run the eval suite and write evals/results/results.md
	uv run python evals/run_evals.py

run:        ## Start the API on http://localhost:8080/docs
	uv run uvicorn app.main:app --reload --port 8080

demo:       ## Start the Streamlit demo
	uv run --extra demo streamlit run demo/streamlit_app.py

docker:     ## Build and run the container
	docker compose up --build
