#!/bin/bash
# Скрипт запуска PanelWithControl
# Автоматически активирует виртуальное окружение и запускает приложение

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем приложение
python3 main.py "$@"
