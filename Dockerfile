FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
WORKDIR /app

# OS libs needed by numpy/pandas on slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgfortran5 ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# install deps first for better layer cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY . .

# production server; binds to $PORT
CMD ["sh","-c","gunicorn -b :${PORT:-8080} app:app"]
