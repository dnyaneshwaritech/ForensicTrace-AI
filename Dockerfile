# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed by OpenCV & PDF generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies first for efficient Docker layer caching
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose ports: 8501 for Streamlit, 8000 for FastAPI
EXPOSE 8501
EXPOSE 8000

# Default command: Start both FastAPI backend and Streamlit companion
CMD python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 & \
    streamlit run app/main_app.py --server.port 8501 --server.address 0.0.0.0
