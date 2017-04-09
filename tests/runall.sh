#!/bin/bash


RED="$(tput setaf 1)"
GREEN="$(tput setaf 2)"
RESET="$(tput sgr0)"

runtest() {
    echo "$1"
    echo "Python3: $(runtest_python "$1" python3)"
    echo "Python2: $(runtest_python "$1" python2)"
}

# arg1: test
# arg2: python
runtest_python() {
    $2 "$1" --test > /dev/null && echo "${GREEN}Successful${RESET}" || echo "${RED}Failed${RESET}"
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
    runtest plugintest.py
    runtest testapi_test.py
fi
