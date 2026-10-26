# Imagen de la aplicación Django "Gestión de Tareas"
# BASE_IMAGE permite usar un registro espejo si Docker Hub no está disponible.
ARG BASE_IMAGE=python:3.10-slim
FROM ${BASE_IMAGE}

# Versión de la release; el pipeline la pasa con --build-arg APP_VERSION=...
ARG APP_VERSION=dev

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_VERSION=${APP_VERSION}

LABEL org.opencontainers.image.title="gestion-tareas" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.authors="Erick Terranova, Marlon Aguiño"

WORKDIR /app

# 1) Dependencias primero: esta capa se reutiliza de la caché mientras
#    requirements.txt no cambie, acelerando los builds del pipeline.
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 2) Código de la aplicación
COPY . .
RUN chmod +x docker/entrypoint.sh \
    && useradd --create-home appuser \
    && chown -R appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=5 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health/').status==200 else 1)"

ENTRYPOINT ["docker/entrypoint.sh"]
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
