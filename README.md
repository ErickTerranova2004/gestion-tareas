# Gestión de Tareas — Flujo CI/CD para Django

Proyecto de la Práctica 3 de **Gestión de la Configuración de Software** (UNEMI).
Aplicación Django con PostgreSQL que implementa un flujo de integración y despliegue
continuo con **GitHub Actions** y **Docker**.

Autores: Erick Steven Terranova Vega · Marlon Rainier Aguiño Salinas

## Estructura

```
manage.py
project/            # configuración del proyecto (settings, urls, wsgi)
tareas/             # app funcional: modelo, vistas, formulario, plantillas y tests
requirements.txt
Dockerfile
docker-compose.yml
docker/entrypoint.sh
.github/workflows/ci.yml
scripts/deploy_simulado.sh
deploy-notes.md
```

## Ejecutar en local (sin Docker)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# PostgreSQL debe estar corriendo; variables por defecto: postgres/postgres@localhost:5432/gestion_tareas
python manage.py migrate
python manage.py test
python manage.py runserver
```

## Ejecutar con Docker

```bash
cp .env.example .env
docker compose up --build -d
# http://localhost:8000  ·  http://localhost:8000/health/
```

## Pipeline

`.github/workflows/ci.yml` ejecuta tres jobs encadenados:

1. **test** – lint con flake8 y `python manage.py test` contra un servicio PostgreSQL.
2. **build** – construye la imagen Docker, la etiqueta con la versión y la guarda como artefacto.
3. **deploy-simulado** – descarga el artefacto, levanta `docker compose` y valida `/health/`.

Ver `deploy-notes.md` para el despliegue simulado manual.
