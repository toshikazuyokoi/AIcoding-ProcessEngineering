# Simple developer tasks
.PHONY: venv install check migrate run fmt clean

PY?=.venv/bin/python
PIP?=.venv/bin/pip
DJ?=$(PY) manage.py

venv:
	python3 -m venv .venv
	. .venv/bin/activate; $(PIP) install --upgrade pip

install: venv
	. .venv/bin/activate; $(PIP) install -r requirements.txt

check:
	. .venv/bin/activate; timeout 30s $(DJ) check --verbosity 2

migrate:
	. .venv/bin/activate; $(DJ) migrate --noinput

run:
	. .venv/bin/activate; $(DJ) runserver 127.0.0.1:8000 --noreload

clean:
	rm -rf .venv __pycache__ **/__pycache__ db.sqlite3
