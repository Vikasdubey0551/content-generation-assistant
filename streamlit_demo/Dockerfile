
FROM python:3.9-slim


WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "streamlit.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false"]
