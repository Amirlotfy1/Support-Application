# استفاده از ایمیج سبک پایتون
FROM python:3.14

# تنظیم متغیرهای محیطی برای عملکرد بهتر پایتون در داکر
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# تعیین دایرکتوری کاری درون کانتینر
WORKDIR /app

# نصب ابزارهای مورد نیاز سیستم‌عامل در صورت نیاز
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# کپی فایل وابستگی‌ها و نصب پکیج‌ها
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# کپی کل پروژه به داخل کانتینر
COPY . /app/

# پورتی که جنگو روی آن سرویس می‌دهد
EXPOSE 8000

# دستور پیش‌فرض برای اجرای سرور توسعه
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
