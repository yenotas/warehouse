# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Обновляем pip и устанавливаем Python-зависимости
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Открываем порт для работы
EXPOSE 8000

# Команда для запуска приложения с миграциями и сборкой статических файлов
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn warehouse.wsgi:application --bind 0.0.0.0:8000"]
