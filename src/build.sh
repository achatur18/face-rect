#!/bin/bash

PYTHON_CMD="python3"
command -v $PYTHON_CMD >/dev/null 2>&1 || { PYTHON_CMD="python"; }

$PYTHON_CMD setup.py sdist bdist_wheel