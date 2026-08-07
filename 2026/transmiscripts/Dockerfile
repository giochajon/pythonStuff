FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home --shell /bin/bash appuser
USER appuser

EXPOSE 8073

ENV TRANSMIUSER=""
ENV TRANSMIPASS=""

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('localhost', 8073), timeout=3)" || exit 1

CMD ["python", "app.py"]
