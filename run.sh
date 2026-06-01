#!/bin/bash
# запуск из корня проекта

if [ ! -d "inbox" ]; then
    echo "нет папки inbox"
    echo "failed"
    exit 1
fi

mkdir -p logs

echo "запуск..."
echo "ошибки в errors.log"

if python3 -m src.main >> logs/run_output.log 2>> errors.log; then
    echo "success"
    exit 0
else
    echo "failed"
    exit 1
fi
