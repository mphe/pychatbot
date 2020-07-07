#!/bin/sh

cd "$(dirname "$(readlink -f "$0")")" || exit 1

RESTART_CODE=42
GITPULL=50

while true; do
    python3 -m chatbot.main "$@"
    code=$?
    [ $code -ne $RESTART_CODE ] && [ $code -ne $GITPULL ] && exit $code
    [ $code -eq $GITPULL ] && git pull
    echo "---------------- Restart ----------------"
done
