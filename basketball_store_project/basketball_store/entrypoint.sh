#!/bin/sh

# Применяем миграции
python manage.py migrate

# Собираем статику (опционально)
python manage.py collectstatic --noinput

# Запускаем сервер
exec "$@"