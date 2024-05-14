FROM python:3.9-alpine
WORKDIR /protocol_management_system
EXPOSE 8000

COPY requirements.txt .

RUN pip install -r requirements.txt && rm requirements.txt

COPY src .

# CMD ./manage.py runserver 0.0.0.0:8000