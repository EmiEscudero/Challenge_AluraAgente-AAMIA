FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=production

WORKDIR /app

RUN groupadd --system aamia && useradd --system --gid aamia --create-home aamia

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY eldercare_agent ./eldercare_agent
COPY scripts ./scripts
COPY app.py ./.env.example ./
COPY .streamlit ./.streamlit
COPY docs ./docs

RUN mkdir -p /app/data/index /app/logs && chown -R aamia:aamia /app

USER aamia
EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3)"

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
