#!/usr/bin/env bash
# Despliegue simulado de "Gestión de Tareas" en una carpeta externa.
#
# Uso:
#   scripts/deploy_simulado.sh --origen <ruta o URL git> --destino <carpeta> \
#       [--imagen-tar <archivo.tar.gz>] [--version <x.y.z>] [--puerto 8000]
#
# Pasos: 1) descarga el proyecto en la carpeta destino
#        2) carga la imagen generada por el pipeline (si se indica)
#        3) levanta los contenedores con Docker Compose
#        4) valida el endpoint /health/ y la página principal
set -euo pipefail

ORIGEN="" DESTINO="" IMAGEN_TAR="" VERSION="latest" PUERTO="${WEB_PORT:-8000}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --origen) ORIGEN="$2"; shift 2 ;;
    --destino) DESTINO="$2"; shift 2 ;;
    --imagen-tar) IMAGEN_TAR="$2"; shift 2 ;;
    --version) VERSION="$2"; shift 2 ;;
    --puerto) PUERTO="$2"; shift 2 ;;
    *) echo "Parámetro desconocido: $1"; exit 2 ;;
  esac
done
[[ -z "$ORIGEN" || -z "$DESTINO" ]] && { echo "Faltan --origen y/o --destino"; exit 2; }

echo "==> [1/4] Descargando el proyecto en $DESTINO"
rm -rf "$DESTINO"
if [[ -d "$ORIGEN/.git" ]]; then
  git clone --quiet --depth 1 "file://$(realpath "$ORIGEN")" "$DESTINO"
elif [[ "$ORIGEN" =~ ^(https?|git)[:@] ]]; then
  git clone --quiet --depth 1 "$ORIGEN" "$DESTINO"
else
  mkdir -p "$DESTINO" && cp -r "$ORIGEN"/. "$DESTINO"/
fi
cp "$DESTINO/.env.example" "$DESTINO/.env"
sed -i "s/^WEB_PORT=.*/WEB_PORT=$PUERTO/" "$DESTINO/.env"
echo "    Archivos desplegados: $(find "$DESTINO" -maxdepth 1 -mindepth 1 -not -name '.*' -printf '%f\n' | sort | tr '\n' ' ')"

echo "==> [2/4] Preparando imagen gestion-tareas:$VERSION"
if [[ -n "$IMAGEN_TAR" ]]; then
  docker load -i "$IMAGEN_TAR"
else
  echo "    Sin artefacto: se construirá desde el Dockerfile"
fi

echo "==> [3/4] Levantando contenedores con Docker Compose"
cd "$DESTINO"
export IMAGE="gestion-tareas:$VERSION" APP_VERSION="$VERSION"
if [[ -n "$IMAGEN_TAR" ]]; then
  docker compose up -d --no-build
else
  docker compose up -d --build
fi

echo "==> [4/4] Validando el despliegue en http://localhost:$PUERTO"
for _ in $(seq 1 30); do
  if curl -fsS "http://localhost:$PUERTO/health/" -o /tmp/health.json 2>/dev/null; then
    echo "    /health/ -> $(cat /tmp/health.json)"
    curl -fsS "http://localhost:$PUERTO/" | grep -q "Gestión de Tareas" \
      && echo "    Página principal responde correctamente"
    docker compose ps
    echo "==> Despliegue exitoso de la versión $VERSION"
    exit 0
  fi
  sleep 2
done
echo "==> El despliegue no respondió a tiempo" >&2
docker compose logs --no-color | tail -40
exit 1
