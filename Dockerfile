# Sử dụng Python 3.11 slim image
FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt system dependencies cần thiết cho OpenCV và các thư viện khác
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libopenblas-dev \
    gfortran \
    wget \
    unzip \
    pkg-config \
    libhdf5-dev \
    python3-dev \
    gcc \
    curl \
    libzbar0 \
    libzbar-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Cài đặt Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code
COPY . .

# Tạo thư mục cho EasyOCR model cache
RUN mkdir -p ~/.EasyOCR

# Expose port mà Streamlit chạy
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Chạy ứng dụng Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]