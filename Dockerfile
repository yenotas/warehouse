# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Открываем порт для работы
EXPOSE 8000

# Команда для запуска приложения
CMD ["gunicorn", "warehouse.wsgi:application", "--bind", "0.0.0.0:8000"]
