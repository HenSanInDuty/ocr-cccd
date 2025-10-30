# 🐳 Docker Deployment Guide

Hướng dẫn build và chạy ứng dụng CCCD Scanner bằng Docker.

## 📋 Yêu cầu

- Docker Desktop (Windows/Mac) hoặc Docker Engine (Linux)
- Docker Compose (thường đi kèm với Docker Desktop)
- Tối thiểu 4GB RAM (để chạy EasyOCR)
- Khoảng 3GB dung lượng ổ cứng

## 🚀 Cách chạy

### Phương pháp 1: Script tự động (Khuyến nghị)

#### Windows:
```bash
# Chạy script build và deploy
docker-build.bat

# Hoặc sử dụng docker-compose manager
docker-compose-manager.bat
```

#### Linux/Mac:
```bash
# Cấp quyền thực thi
chmod +x docker-build.sh

# Chạy script
./docker-build.sh
```

### Phương pháp 2: Docker Compose (Manual)

```bash
# Build và chạy
docker-compose up --build -d

# Chỉ chạy (nếu đã build)
docker-compose up -d

# Dừng
docker-compose down

# Xem logs
docker-compose logs -f

# Rebuild hoàn toàn
docker-compose down -v --rmi all
docker-compose up --build -d
```

### Phương pháp 3: Docker Commands (Manual)

```bash
# Build image
docker build -t cccd-scanner:latest .

# Chạy container
docker run -d \
  --name cccd-scanner-app \
  -p 8501:8501 \
  --restart unless-stopped \
  cccd-scanner:latest

# Xem logs
docker logs cccd-scanner-app

# Dừng và xóa
docker stop cccd-scanner-app
docker rm cccd-scanner-app
```

## 🌐 Truy cập ứng dụng

Sau khi build thành công, truy cập:
- **Local**: http://localhost:8501
- **Network**: http://[YOUR_IP]:8501

## 📊 Quản lý Container

### Xem trạng thái
```bash
docker ps                          # Containers đang chạy
docker-compose ps                  # Services status
```

### Xem logs
```bash
docker logs cccd-scanner-app       # Docker command
docker-compose logs -f             # Docker compose
```

### Restart
```bash
docker restart cccd-scanner-app    # Docker command
docker-compose restart             # Docker compose
```

### Cập nhật code
```bash
# Dừng, rebuild, và chạy lại
docker-compose down
docker-compose up --build -d
```

## 🔧 Troubleshooting

### Lỗi thường gặp:

1. **Port 8501 đã được sử dụng**
   ```bash
   # Kiểm tra process đang dùng port
   netstat -tulpn | grep 8501
   
   # Thay đổi port trong docker-compose.yml
   ports:
     - "8502:8501"  # Đổi 8501 thành 8502
   ```

2. **Container không start**
   ```bash
   # Xem logs để debug
   docker logs cccd-scanner-app
   ```

3. **Không đủ RAM**
   ```bash
   # Kiểm tra RAM available
   docker system df
   
   # Dọn dẹp Docker
   docker system prune -a
   ```

4. **EasyOCR download lỗi**
   ```bash
   # Xóa volume và rebuild
   docker-compose down -v
   docker-compose up --build -d
   ```

## 📁 Cấu trúc Files

```
ocr_poc/
├── Dockerfile                    # Docker image definition
├── docker-compose.yml           # Docker compose configuration
├── .dockerignore                # Files to exclude from build
├── docker-build.bat            # Windows build script
├── docker-build.sh             # Linux/Mac build script
├── docker-compose-manager.bat  # Windows compose manager
└── DOCKER_README.md             # This file
```

## ⚡ Tips tối ưu

1. **Sử dụng Volume cho EasyOCR models**
   - Models sẽ được cache và không cần download lại

2. **Multi-stage build** (Advanced)
   - Có thể tối ưu size image bằng multi-stage build

3. **Health checks**
   - Container tự động restart nếu unhealthy

4. **Resource limits**
   ```yaml
   # Trong docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 4G
         cpus: '2'
   ```

## 🐛 Debug Mode

Để chạy container ở debug mode:

```bash
# Interactive mode với bash
docker run -it --rm -p 8501:8501 cccd-scanner:latest bash

# Override entrypoint để debug
docker run -it --rm -p 8501:8501 \
  --entrypoint="" cccd-scanner:latest bash
```