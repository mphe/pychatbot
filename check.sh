#!/usr/bin/env bash

mypy --python-version 3.8 chatbot tests
pylint --py-version 3.8 chatbot tests
