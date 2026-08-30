FROM python:3.12-slim

WORKDIR /workspace

COPY app/requirements.txt ./requirements.txt

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a non-root user and switch to it for security
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /workspace

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
