FROM python:3.12-slim

WORKDIR /app

# Build context is ./ml_worker, so paths are relative to this directory
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Optionally copy sources so the image can run without a volume
COPY . /app

CMD ["python", "main.py"]