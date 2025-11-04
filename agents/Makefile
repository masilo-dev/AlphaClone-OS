# AlphaClone-OS Agent Subsystem Makefile

PYTHON ?= python3
PYTEST ?= pytest
FLAKE8 ?= flake8

.PHONY: all clean test lint run

all: test lint

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

test:
	$(PYTEST) -v agents/*/tests/

lint:
	$(FLAKE8) agent_runtime agents

run:
	mkdir -p /tmp/alphaclone/ipc
	$(PYTHON) agent_launcher.py start

stop:
	$(PYTHON) agent_launcher.py stop

status:
	$(PYTHON) agent_launcher.py status