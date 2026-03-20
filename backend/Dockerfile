# Railway 用 Docker 构建，避免 Nixpacks 环境问题
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# Railway 会注入 PORT 环境变量
ENV PORT=5000
EXPOSE $PORT

# 直接启动，不用 start.sh
CMD gunicorn --bind 0.0.0.0:${PORT} "app:create_app()"
