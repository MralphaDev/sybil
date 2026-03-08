# Python 基础镜像
FROM python:3.12-slim

WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制 backend 代码
COPY . .

# 暴露 FastAPI 端口
EXPOSE 8000

# 启动 FastAPI 并开启热重载
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]