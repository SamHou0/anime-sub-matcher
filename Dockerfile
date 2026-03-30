FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ ./app/

# 创建必要的目录
RUN mkdir -p /app/uploads /app/bangumi

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app
ENV PYTHONUNBUFFERED=1

# 启动应用
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
