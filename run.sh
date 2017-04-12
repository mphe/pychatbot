#!/bin/sh

RESTART_CODE=42

while true; do
    python -m chatbot.main "$@"
    code=$?
    [ $code -ne $RESTART_CODE ] && exit $code
    echo "---------------- Restart ----------------"
done
