# Notas de despliegue simulado — Gestión de Tareas

Autores: Erick Steven Terranova Vega · Marlon Rainier Aguiño Salinas

El despliegue se simula en una **carpeta externa** al repositorio (por ejemplo
`/opt/despliegue/gestion-tareas` en Linux o `C:\despliegue\gestion-tareas` en Windows),
usando la imagen Docker que genera el pipeline como artefacto.

## Requisitos

- Docker Engine 24+ con el plugin Docker Compose v2 (`docker compose version`).
- Git.
- Puerto 8000 libre (se puede cambiar con `--puerto` o `WEB_PORT`).

## Convención de versiones (nombrado de releases)

| Origen del build             | Versión generada        | Ejemplo            |
|------------------------------|-------------------------|--------------------|
| Push a una rama              | `0.1.<run>-<sha corto>` | `0.1.4-1a2b3c4`    |
| Tag semántico `vX.Y.Z`       | `X.Y.Z`                 | `1.0.0`            |

La versión se inyecta en la imagen (`APP_VERSION`), aparece en la cabecera de la
aplicación y en `GET /health/`, de modo que siempre se sabe qué release está corriendo.

## A. Despliegue automático (GitHub Actions)

El job `deploy-simulado` se ejecuta después de `test` y `build`:

1. Descarga el artefacto `imagen-docker` (`gestion-tareas-<versión>.tar.gz`).
2. Ejecuta `scripts/deploy_simulado.sh` con destino `$RUNNER_TEMP/despliegue`.
3. El script copia el proyecto, carga la imagen con `docker load`, levanta
   `docker compose up -d --no-build` y valida `/health/` y la página principal.
4. Muestra los logs y detiene el entorno (`docker compose down -v`).

## B. Despliegue manual en el equipo local

### 1. Descargar el artefacto del pipeline

En GitHub: **Actions → ejecución exitosa → Artifacts → imagen-docker** y
descomprimir el `.zip` descargado. Se obtiene `gestion-tareas-<versión>.tar.gz`.

### 2. Descargar el proyecto en la carpeta externa

```bash
git clone https://github.com/<usuario>/gestion-tareas.git /opt/despliegue/gestion-tareas
cd /opt/despliegue/gestion-tareas
cp .env.example .env        # ajustar DJANGO_SECRET_KEY y contraseñas
```

### 3. Cargar la imagen y levantar los contenedores

```bash
docker load -i ~/Descargas/gestion-tareas-1.0.0.tar.gz
export IMAGE=gestion-tareas:1.0.0 APP_VERSION=1.0.0
docker compose up -d --no-build
docker compose ps           # web y db deben aparecer como (healthy)
```

Alternativa en un solo paso:

```bash
bash scripts/deploy_simulado.sh \
  --origen https://github.com/<usuario>/gestion-tareas.git \
  --destino /opt/despliegue/gestion-tareas \
  --imagen-tar ~/Descargas/gestion-tareas-1.0.0.tar.gz --version 1.0.0
```

### 4. Validar desde el navegador

- Aplicación: <http://localhost:8000/>  → debe mostrar "Gestión de Tareas" y la versión.
- Salud: <http://localhost:8000/health/> → `{"status": "ok", "database": "ok", "version": "1.0.0"}`

### 5. Rollback a una versión anterior

```bash
docker load -i gestion-tareas-<versión-anterior>.tar.gz
export IMAGE=gestion-tareas:<versión-anterior>
docker compose up -d --no-build      # recrea solo el contenedor web
```

Los datos se conservan en el volumen `pgdata`.

### 6. Detener el entorno

```bash
docker compose down        # conserva los datos
docker compose down -v     # elimina también el volumen de PostgreSQL
```

## Problemas frecuentes

| Síntoma                                   | Causa / solución                                                       |
|-------------------------------------------|------------------------------------------------------------------------|
| `port is already allocated`               | El puerto 8000 está ocupado: usar `WEB_PORT=8080` o `--puerto 8080`.    |
| `web` reiniciándose                       | Revisar `docker compose logs web`; normalmente credenciales de BD.     |
| `DisallowedHost` en el navegador          | Agregar el host a `DJANGO_ALLOWED_HOSTS` en `.env`.                     |
| `pull access denied for gestion-tareas`   | Falta `docker load` del artefacto o usar `--build` para construir.      |
