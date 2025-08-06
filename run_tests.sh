#!/bin/bash

cd "$(dirname "$(readlink -f "$0")")" || exit 1

cd tests || exit 1  # Some tests require CWD to be in tests/
python -m unittest discover ./
