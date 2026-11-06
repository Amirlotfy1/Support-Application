# Support application Platform


An enterprise-grade customer support, ticketing, and real-time communication platform built with **Django**, **Django REST Framework (DRF)**, and **Django Channels**. The backend handles secure JWT authentication, multi-type ticketing, real-time WebSocket chat rooms, file attachments, and multi-channel notifications (Email, SMS (Console), and Bale Messenger).


# System Requirements & Dependencies
```text
Django==6.0.6
djangorestframework==3.17.1
djangorestframework_simplejwt==5.5.1
channels==4.3.2
channels_redis==4.3.0
daphne==4.2.2
django-environ==0.14.0
redis==8.0.0
drf-spectacular>=0.28.0
django-silk>=5.3.0
```

# env file
3. Environment Variables Configuration (.env)
Create a .env file in the project root directory:
```bash
SECRET_KEY=WRITE-YOUR-SECRET-KEY
ALLOWED_HOSTS=localhost,127.0.0.1

# Notification
BALE_BOT_TOKEN=YOUR-BALE-BOT-TOKEN

# SMTP Email Configuration
EMAIL_HOST=YOUR-EMAIL-HOST
EMAIL_PORT=YOUR-PORT
EMAIL_USERNAME=YOUR-UESRNAME
EMAIL_PASSWORD=YOUR-SMTP-PASSWORD
DEFAULT_FROM_EMAIL=YOUR-EMAIL-DEFUALT
```

# API Documentation & Swagger UI
The project integrates drf-spectacular to provide auto-generated interactive API documentation:
```text
Swagger UI: http://<your-domain>/swagger/
ReDoc UI: http://<your-domain>/redoc/
OpenAPI Schema JSON: http://<your-domain>/schema/
Performance Profiling Dashboard (Silk): http://<your-domain>/silk/
```