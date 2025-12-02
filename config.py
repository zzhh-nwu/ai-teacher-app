# config.py - 配置文件
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# DeepSeek API配置
DEEPSEEK_API_KEY = "sk-335e06b971bc470fbaf13c5dc485cddf"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 网络配置
MAX_RETRIES = 3
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 120
BACKOFF_FACTOR = 0.5
TIMEOUT = (CONNECT_TIMEOUT, READ_TIMEOUT)

# 应用配置
APP_CONFIG = {
    "name": "AI课程设计助手",
    "version": "1.0.0",
    "description": "基于DeepSeek大模型的智能课程内容生成平台"
}