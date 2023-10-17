#! /bin/bash
poetry run pytest -W ignore::DeprecationWarning --cov-report html --cov-report xml --cov-report term-missing --cov=nstimes tests/
