# ---------- Build stage ----------
FROM python:3.13-slim AS build
WORKDIR /app
COPY requirements.txt .
# Install into an isolated prefix so we can copy only the compiled packages.
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- Runtime stage ----------
FROM python:3.13-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/install/bin:${PATH}" \
    PYTHONPATH="/install/lib/python3.13/site-packages:${PYTHONPATH}"

# Copy compiled dependencies from the build stage.
COPY --from=build /install /install

# Copy application source.
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
