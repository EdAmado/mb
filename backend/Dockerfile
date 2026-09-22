FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Ensure uploads directory exists
RUN mkdir -p /app/uploads

CMD ["python", "app.py"]