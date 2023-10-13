#! /bin/bash
poetry run pytest -W ignore::DeprecationWarning --cov-report html --cov=nstimes tests/
