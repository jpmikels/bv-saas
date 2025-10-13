# -----------------------------
# Dockerfile for Valuation App
# -----------------------------

# Use a full Python image so pandas/numpy don’t crash
FROM python:3.11

# Prevent .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cloud Run automatically sets PORT — default to 8080 for local use
ENV PORT=8080

# Set working directory
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Use Gunicorn in production and restrict to 1 worker to save memory
CMD ["sh","-c","gunicorn --workers=1 -b :${PORT:-8080} app:app"]
