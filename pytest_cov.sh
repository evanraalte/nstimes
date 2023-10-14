#! /bin/bash
poetry run pytest -W ignore::DeprecationWarning --cov-report html --cov-report xml --cov=nstimes tests/
