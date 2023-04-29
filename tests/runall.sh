#!/bin/bash

cd "$(dirname "$(readlink -f "$0")")" || exit 1

RED="$(tput setaf 1)"
GREEN="$(tput setaf 2)"
RESET="$(tput sgr0)"

# arg1: test
runtest() {
    echo "$1"
    python3 "$1" --test > /dev/null && echo "${GREEN}Successful${RESET}" || echo "${RED}Failed${RESET}"
}


if [ $# -gt 0 ]; then
    while [ $# -gt 0 ]; do
        runtest "$1"
        shift
    done
else
    runtest command_test.py
    runtest dispatcher_test.py
    runtest event_test.py
    runtest plugin_manager.py
    runtest testapi_test.py
    runtest configtest.py
    ./test_storage.py
fi
