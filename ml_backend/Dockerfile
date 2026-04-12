FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements.render.txt .
RUN pip install --no-cache-dir -r requirements.render.txt

COPY . .

ENV PORT=8000
ENV MODEL_VERSION=1.0.0
ENV SAFETY_MODE=conservative
ENV CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000

EXPOSE 8000

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
