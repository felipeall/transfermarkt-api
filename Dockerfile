FROM python:3.9-slim-bullseye

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# Install playwright browsers if playwright is in requirements
RUN python -c "import playwright" 2>/dev/null && playwright install chromium || true

COPY . ./

CMD ["python", "app/main.py"]