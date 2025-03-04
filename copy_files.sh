#!/bin/bash

# Создаем необходимые директории
mkdir -p bot config utils tests

# Копируем файлы из старого проекта
cp ../.env ./ 2>/dev/null || echo "Warning: .env file not found"
cp ../requirements.txt ./ 2>/dev/null || echo "Warning: requirements.txt file not found"

# Делаем скрипт исполняемым
chmod +x copy_files.sh 