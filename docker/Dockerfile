# 使用Python官方基础镜像
# 注意: 为了加速构建，建议在Docker Desktop中配置国内镜像源
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制requirements.txt并安装依赖
# 注意: 这里的COPY路径是相对于docker-compose.yml中设置的context（即项目根目录）
COPY requirements.txt .

# 设置pip国内镜像源加速依赖安装
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

# 复制项目所有文件到工作目录
# 注意: 这里的COPY路径是相对于docker-compose.yml中设置的context（即项目根目录）
COPY . .

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV PROJECT_NAME=destiny

# 暴露Flask应用运行的端口
EXPOSE 5000

# 运行应用程序
CMD ["python", "run_app.py"]