# Dockerfile for Horse Genetics Simulator
# Supports both Streamlit web UI and FastAPI REST API

FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./
COPY LICENSE ./
COPY README.md ./

# Copy application code
COPY genetics/ ./genetics/
COPY api/ ./api/
COPY .streamlit/ ./.streamlit/
COPY streamlit_app.py ./
COPY horse_genetics.py ./
COPY horse_genetics_gui.py ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .
RUN pip install --no-cache-dir streamlit fastapi uvicorn

# Expose ports
# 8501 for Streamlit
# 8000 for FastAPI
EXPOSE 8501 8000

# Default command (Streamlit web UI)
CMD ["streamlit", "run", "streamlit_app.py", "--server.address", "0.0.0.0"]
