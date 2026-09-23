# Imagem Python
FROM python:3.12-slim

# Sem arquivos .pyc e com logs sem buffer
# APP_ENV=production exige os segredos por variável de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production

WORKDIR /app

# Instala as dependências antes do código: aproveita o cache de camadas do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY app ./app
COPY run.py .

# Executa o usuário padrão sem privilégios
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && mkdir -p /app/instance \
    && chown -R appuser:appuser /app
USER appuser

# Persiste o SQLite fora do ciclo de vida do container
VOLUME ["/app/instance"]
EXPOSE 5000

# Verifica se a API responde.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/api/v1/healthcheck', timeout=3)"

# Gunicorn em vez do servidor de desenvolvimento
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--access-logfile", "-", "run:app"]
