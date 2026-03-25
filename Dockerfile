# 使用官方的 Python 3.11 基礎輕量化映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 將目前目錄的文件複製到容器中
COPY . /app

# 安裝需要的套件包含 flask
RUN pip install --no-cache-dir requests schedule python-dotenv flask

# 執行主程式
CMD ["python", "main.py"]
