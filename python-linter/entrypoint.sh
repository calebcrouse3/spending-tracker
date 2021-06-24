#!/bin/bash
set -e

echo "Running black..."
python3 -m black . --check --diff
echo "success!"
echo

echo "Running pylint..."
find . -name "*.py" | \
  grep -v ".ipynb_checkpoints" | \
  xargs python3 -m pylint --rcfile python-linter/.pylintrc
echo "success!"
echo

echo "Running mypy..."
python3 -m mypy --config-file python-linter/mypy.ini .
echo "success!"
echo

echo "Runnimg yamllint..."
python3 -m yamllint -c python-linter/yamllint.yml .
echo "success!"
echo

echo "Running bandit..."
python3 -m bandit --recursive --quiet .
echo "success!"
