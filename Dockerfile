# استفاده از ایمیج سبک و پایدار
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# نصب ابزارهای مورد نیاز سیستم‌عامل
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# نصب uv مستقیماً از ایمیج رسمی آن (فوق‌العاده سریع و استاندارد)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# نصب پکیج‌ها با استفاده از uv و کش داکر
COPY requirements.txt /app/
RUN uv pip install --system --no-cache -r requirements.txt

# کپی پروژه
COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
