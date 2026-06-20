# Multi-stage build keeps the runtime image small.
FROM python:3.14-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Install runtime deps only
COPY services/health-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# App code + shared libs
COPY services/health-service/app ./app
COPY libs ./libs

# Run as non-root
RUN useradd -m appuser
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status==200 else 1)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
