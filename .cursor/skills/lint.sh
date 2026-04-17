#!/bin/bash
# Simple linting script that only runs what is present
echo "Running linters..."
if ls -- *.py 1> /dev/null 2>&1; then ruff check .; ruff format .; fi
if ls -- *.js 1> /dev/null 2>&1; then biome check --write .; fi
if ls -- *.sh 1> /dev/null 2>&1; then shellcheck -- *.sh; fi
if ls -- *.yaml 1> /dev/null 2>&1 || ls -- *.yml 1> /dev/null 2>&1; then yamllint .; fi
if ls -- *.tf 1> /dev/null 2>&1; then tflint; terraform validate; fi
echo "Linting complete."
