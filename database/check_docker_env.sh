#!/bin/bash
# 檢查 Docker 環境變量

echo "PostgreSQL 容器環境變量："
docker exec openclaw-postgres env | grep -E "POSTGRES|PG"