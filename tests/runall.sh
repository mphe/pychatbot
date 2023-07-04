#!/bin/bash

cd "$(dirname "$(readlink -f "$0")")" || exit 1

python -m unittest discover ./
