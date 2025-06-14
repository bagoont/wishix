project_dir := backend/

.PHONY: lint
lint:
	ruff check $(project_dir)
	pyright $(project_dir)

.PHONY: format
format:
	ruff check $(project_dir) --fix