import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 数据库配置 - 优先从环境变量读取，否则使用默认值
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'rm-bp1455j4m154h13ydto.mysql.rds.aliyuncs.com'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'kk'),
    'password': os.environ.get('DB_PASSWORD', 'kk123_456'),
    'database': os.environ.get('DB_NAME', 'destiny'),
    'charset': 'utf8mb4'
}

# Ollama配置 - 优先从环境变量读取
OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://kkteam.online:10434/api/generate')

# Flask配置 - 优先从环境变量读取
FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't', 'y', 'yes')