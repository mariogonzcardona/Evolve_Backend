#!/bin/bash
set -e

echo "🧹 Limpiando recursos de Docker..."
docker system prune -a --volumes -f
docker builder prune --all -f

echo "🧹 Limpiando logs del sistema..."
sudo journalctl --vacuum-time=1d

echo "🧹 Limpiando logs de contenedores..."
sudo find /var/lib/docker/containers/ -name "*.log" -exec truncate -s 0 {} \;

echo "✅ Limpieza completada."

docker compose down --remove-orphans
docker compose up --build -d