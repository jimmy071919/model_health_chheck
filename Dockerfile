# 使用官方的 Python 3.11 基礎輕量化映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 將目前目錄的文件複製到容器中
COPY . /app

# 因為你習慣使用 uv，我們也可以安裝 uv 來加速安裝相依套件 (可選)，或直接使用 pip
RUN pip install --no-cache-dir requests schedule python-dotenv

# 執行主程式
CMD ["python", "main.py"]
