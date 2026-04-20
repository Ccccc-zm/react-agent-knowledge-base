# 使用 Python 3.11 官方镜像作为基础
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目所有代码到容器中
COPY . .

# 暴露 Streamlit 默认端口和 FastAPI 默认端口
EXPOSE 8501 8000

# 默认启动命令（可被 docker-compose 覆盖）
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]