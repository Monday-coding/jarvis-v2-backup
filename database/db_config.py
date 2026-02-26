#!/usr/bin/env python3
"""
更新數據庫連接配置
"""

# 數據庫配置
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "openclaw",
    "user": "openclaw",
    "password": "openclaw_password_2024"
}

# PostgreSQL 配置
POSTGRES_CONFIG = {
    "host": DB_CONFIG["host"],
    "port": DB_CONFIG["port"],
    "database": DB_CONFIG["database"],
    "user": DB_CONFIG["user"],
    "password": DB_CONFIG["password"]
}

print("數據庫配置已更新")
print("=" * 60)
print(f"Host: {DB_CONFIG['host']}")
print(f"Port: {DB_CONFIG['port']}")
print(f"Database: {DB_CONFIG['database']}")
print(f"User: {DB_CONFIG['user']}")
print(f"Password: {DB_CONFIG['password']}")
print("=" * 60)
