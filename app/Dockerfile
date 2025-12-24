FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY app/ /app/
COPY database/ /app/database/

EXPOSE 8000

CMD ["python", "main.py"]