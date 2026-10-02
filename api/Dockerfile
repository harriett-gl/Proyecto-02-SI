FROM python:3.12-slim

WORKDIR /app

COPY ../requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY api/ /app/

EXPOSE 5001

CMD ["python", "app.py"]