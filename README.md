# 🆔 CCCD Scanner App

Ứng dụng Streamlit để quét QR code và OCR trên ảnh CCCD (Căn cước công dân).

## ✨ Tính năng

- **Quét QR Code**: Tự động phát hiện và đọc QR code với 3 scale khác nhau (1→2→3)
- **OCR Tiếng Việt**: Nhận dạng văn bản tiếng Việt khi không quét được QR
- **Đa phương thức nhập ảnh**: Upload file hoặc chụp trực tiếp từ camera
- **Camera tích hợp**: Chụp ảnh CCCD trực tiếp từ camera thiết bị
- **Hỗ trợ 2 loại CCCD**:
  - **CCCD Mới**: Quét QR ở mặt sau, OCR ở mặt trước
  - **CCCD Cũ**: Quét QR ở mặt trước, OCR ở mặt trước
- **Giao diện thân thiện**: Sử dụng Streamlit với UI đẹp mắt

## 🚀 Cài đặt và chạy

### Phương pháp 1: Local Development

#### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

#### 2. Chạy ứng dụng

```bash
streamlit run app.py
```

#### 3. Truy cập ứng dụng

Mở trình duyệt và truy cập: `http://localhost:8501`

### Phương pháp 2: Docker (Khuyến nghị cho Production)

#### 1. Sử dụng script tự động:

**Windows:**
```bash
docker-build.bat
```

**Linux/Mac:**
```bash
chmod +x docker-build.sh
./docker-build.sh
```

#### 2. Hoặc sử dụng Docker Compose:

```bash
# Build và chạy
docker-compose up --build -d

# Truy cập: http://localhost:8501
```

> 📖 **Chi tiết Docker**: Xem [DOCKER_README.md](DOCKER_README.md) để biết thêm chi tiết.

## 📖 Hướng dẫn sử dụng

### Upload File:
1. Chọn "📁 Upload file" trong sidebar
2. Chọn loại CCCD (Mới/Cũ)
3. Upload ảnh theo yêu cầu
4. Nhấn "Bắt đầu xử lý"

### Chụp Camera:
1. Chọn "📸 Chụp camera" trong sidebar
2. Chọn loại CCCD (Mới/Cũ)
3. Sử dụng camera để chụp ảnh CCCD
4. Nhấn "Bắt đầu xử lý"

### CCCD Mới:
- **Upload/Camera**: Ảnh mặt sau (bắt buộc) + Mặt trước (tùy chọn)
- **Quy trình**: QR ở mặt sau → OCR ở mặt trước (nếu QR thất bại)

### CCCD Cũ:
- **Upload/Camera**: Ảnh mặt trước (bắt buộc)
- **Quy trình**: QR ở mặt trước → OCR ở mặt trước (nếu QR thất bại)

## 📁 Cấu trúc project

```
ocr_poc/
├── app.py                        # Ứng dụng Streamlit chính
├── requirements.txt              # Dependencies
├── README.md                     # Tài liệu chính
├── DOCKER_README.md              # Hướng dẫn Docker
├── Dockerfile                    # Docker image
├── docker-compose.yml            # Docker compose config
├── .dockerignore                 # Docker ignore file
├── docker-build.bat             # Windows Docker script
├── docker-build.sh              # Linux/Mac Docker script
├── docker-compose-manager.bat   # Windows compose manager
├── run_app.bat                   # Windows run script
└── utils/
    └── ocr.py                    # Functions xử lý OCR và QR
```

## 🔧 Yêu cầu hệ thống

- Python 3.7+
- RAM: Tối thiểu 4GB (EasyOCR cần nhiều RAM)
- GPU: Không bắt buộc (nhưng sẽ nhanh hơn nếu có)

## 📝 Ghi chú

- Ảnh upload nên có độ phân giải cao để kết quả OCR tốt hơn
- QR code cần rõ nét và không bị che khuất
- Hỗ trợ các định dạng ảnh: JPG, JPEG, PNG