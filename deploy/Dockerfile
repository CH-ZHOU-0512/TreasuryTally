FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --home /app app

COPY pyproject.toml ./
COPY src ./src
RUN python -m pip install --no-cache-dir .

COPY app ./app
COPY fixtures ./fixtures
RUN mkdir -p /app/data /app/receipts/private && chown -R app:app /app

USER app
EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/trust-receipt/_stcore/health', timeout=3)"

CMD ["python", "-m", "streamlit", "run", "app/streamlit_app.py", \
     "--server.address=0.0.0.0", "--server.port=8501", \
     "--server.baseUrlPath=trust-receipt", "--server.headless=true", \
     "--browser.gatherUsageStats=false"]

