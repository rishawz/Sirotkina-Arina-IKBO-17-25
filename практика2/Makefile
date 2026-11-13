PYTHON ?= python3
export PYTHONDONTWRITEBYTECODE = 1
export PYTHONPATH = src

.PHONY: run test

# Пример: make run ARGS="--package serde"
run:
	$(PYTHON) src/main.py $(ARGS)

test:
	$(PYTHON) -m unittest discover -s tests -v
