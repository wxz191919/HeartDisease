import os
from datetime import timedelta

class Config:
    # Railway MySQL 插件提供完整 URL；无则用 SQLite 保证能启动
    DATABASE_URL = os.environ.get('MYSQL_URL') or os.environ.get('DATABASE_URL')
    
    if DATABASE_URL and DATABASE_URL.startswith('mysql'):
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    elif DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # 无 MySQL 时用 SQLite，避免 Railway 上启动即崩溃
        _tmp = os.environ.get('SQLITE_PATH', '/tmp/heart.db')
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{_tmp}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置 - Railway 环境变量
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # 其他配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true' 