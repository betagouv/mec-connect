#!/bin/bash

THIS_DIR=$(dirname "$(realpath "$0")")
PYTHON_VERSION=$(cat "$THIS_DIR/../.python-version")
echo "$PYTHON_VERSION" > "$THIS_DIR/../runtime.txt"
