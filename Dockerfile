# --- frontend build (optional; 後で追加) ---
FROM node:20 AS fe
WORKDIR /app/frontend
COPY frontend/ ./
RUN [ -f package.json ] && npm ci && npm run build || true

# --- backend ---
FROM python:3.11-slim
WORKDIR /app
COPY backend/ ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt
# フロント成果物を配信（後で追加する想定）
COPY --from=fe /app/frontend/dist ./backend/dist/ || true
WORKDIR /app/backend
EXPOSE 8686
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8686", "--reload"]
