import os
from datetime import timedelta

class Config:
    # Railway 插件提供 MySQL 环境变量
    MYSQL_HOST = os.environ.get('MYSQLHOST', os.environ.get('MYSQL_HOST', 'localhost'))
    MYSQL_PORT = os.environ.get('MYSQLPORT', os.environ.get('MYSQL_PORT', '3306'))
    MYSQL_USER = os.environ.get('MYSQLUSER', os.environ.get('MYSQL_USER', 'root'))
    MYSQL_PASSWORD = os.environ.get('MYSQLPASSWORD', os.environ.get('MYSQL_PASSWORD', '19491001China'))
    MYSQL_DATABASE = os.environ.get('MYSQLDATABASE', os.environ.get('MYSQL_DATABASE', 'heart_db'))
    
    # Railway MySQL 插件提供完整 URL
    DATABASE_URL = os.environ.get('MYSQL_URL')
    
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置 - Railway 环境变量
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # 其他配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true' 