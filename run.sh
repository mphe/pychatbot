#!/bin/sh

cd $(dirname $(readlink -f "$0"))

RESTART_CODE=42

while true; do
    python3 -m chatbot.main "$@"
    code=$?
    [ $code -ne $RESTART_CODE ] && exit $code
    echo "---------------- Restart ----------------"
done
