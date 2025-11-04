# Tóm tắt các thay đổi - Object Detection + OCR

## 🎯 Mục đích
Thêm luồng cho phép chọn mô hình YOLO để object detection trước khi thực hiện OCR, với mapping thông tin theo các trường đã định nghĩa.

## 📝 Các thay đổi chính

### 1. **File `utils/ocr.py`**
#### ✅ Đã sửa lỗi encoding QR code
- Thêm xử lý decode UTF-8 với fix các ký tự bị encode lỗi
- Mapping các ký tự lỗi (盻ｳ, ﾃｺ, v.v.) sang ký tự tiếng Việt đúng

#### ✅ Thêm hàm `OCR_with_detection()`
```python
def OCR_with_detection(img, model, class_names, show_result=False):
    """
    Thực hiện object detection trước, sau đó OCR từng vùng đã detect
    
    Parameters:
        img: OpenCV image
        model: YOLO model đã load
        class_names: List các class names từ get_class()
        show_result: Có hiển thị kết quả hay không
    
    Returns:
        detected_info: Dict mapping từ class name sang text OCR
        img_with_boxes: Ảnh với bounding boxes
    """
```

**Quy trình:**
1. Rotate ảnh nếu cần (`rotate_if_necessary`)
2. Thực hiện object detection bằng YOLO model
3. OCR từng vùng đã detect
4. Map kết quả theo class_names
5. Trả về dictionary {class_name: text_value}

### 2. **File `app.py`**

#### ✅ Thêm import
```python
from utils.ocr import OCR_with_detection
from utils.model_inference import get_model, get_class
```

#### ✅ Thêm UI chọn phương thức OCR trong Sidebar
- **OCR trực tiếp**: OCR toàn bộ ảnh (như cũ)
- **Object Detection + OCR**: Detect từng trường rồi OCR

#### ✅ Thêm UI chọn mô hình YOLO
- Hiển thị khi chọn "Object Detection + OCR"
- Options: `yolov8`, `yolov11`
- Load model vào `st.session_state` để tránh reload nhiều lần

#### ✅ Cập nhật hàm `process_images_from_source()`
Thêm tham số:
- `ocr_method`: Phương thức OCR
- `detection_model`: Model YOLO
- `class_names`: List các class names

**Logic:**
```python
if ocr_method == "Object Detection + OCR" and detection_model is not None:
    # Thực hiện Object Detection + OCR
    detected_info, img_with_boxes = OCR_with_detection(img, model, class_names)
    
    # Hiển thị kết quả theo từng trường
    for field_name, text_value in detected_info.items():
        st.markdown(f"**{field_name}:** {text_value}")
else:
    # OCR thường (như cũ)
    ocr_result = OCR_img(img)
```

#### ✅ Hiển thị danh sách các trường detect
Trong sidebar, hiển thị 12 trường từ `get_class()`:
1. current_place
2. dob
3. expire_date
4. features
5. finger_print
6. gender
7. id
8. issue_date
9. name
10. nationality
11. origin_place
12. qr

## 🔄 Quy trình hoạt động

### Luồng CCCD Mới (QR ở mặt sau)
```
1. User upload/chụp ảnh mặt sau
2. Thử quét QR code (scale 1→2→3)
3. Nếu QR thành công → Parse và hiển thị thông tin
4. Nếu QR thất bại:
   - Nếu chọn "Object Detection + OCR":
     a. Detect các trường trên ảnh mặt trước
     b. OCR từng trường đã detect
     c. Map kết quả theo class_names
     d. Hiển thị bảng thông tin
   - Nếu chọn "OCR trực tiếp":
     → OCR toàn bộ ảnh (như cũ)
```

### Luồng CCCD Cũ (QR ở mặt trước)
```
1. User upload/chụp ảnh mặt trước
2. Thử quét QR code (scale 1→2→3)
3. Nếu QR thành công → Parse và hiển thị thông tin
4. Nếu QR thất bại:
   - Nếu chọn "Object Detection + OCR":
     a. Detect các trường trên ảnh mặt trước
     b. OCR từng trường đã detect
     c. Map kết quả theo class_names
     d. Hiển thị bảng thông tin
   - Nếu chọn "OCR trực tiếp":
     → OCR toàn bộ ảnh (như cũ)
```

## 📊 Kết quả hiển thị

### Object Detection + OCR
```
### 📋 Thông tin đã detect:
**id:** 075303000545
**name:** Huỳnh Phước Tấ Uyên
**dob:** 19/03/2003
**gender:** Nữ
**current_place:** B-3-05 C/c Tanibuilding...
**issue_date:** 25/01/2022
...

| Trường        | Giá trị              |
|---------------|----------------------|
| id            | 075303000545         |
| name          | Huỳnh Phước Tấ Uyên  |
| dob           | 19/03/2003           |
| ...           | ...                  |
```

### OCR trực tiếp (như cũ)
```
Kết quả OCR:
Huỳnh Phước Tấ Uyên
19/03/2003
Nữ
...
```

## 🚀 Cách sử dụng

1. Chọn loại CCCD (Mới/Cũ)
2. Chọn phương thức nhập ảnh (Upload/Camera)
3. **Chọn phương thức OCR:**
   - OCR trực tiếp: Nhanh, không cần model
   - Object Detection + OCR: Chính xác hơn, mapping theo trường
4. Nếu chọn Object Detection:
   - Chọn mô hình (yolov8/yolov11)
   - Đợi load model
5. Upload/chụp ảnh
6. Nhấn "Bắt đầu xử lý"

## ⚠️ Lưu ý

1. **Model path**: Đảm bảo model YOLO có trong thư mục `models_inference/`
2. **Performance**: Object Detection + OCR chậm hơn OCR trực tiếp
3. **Memory**: Model YOLO cần ~100-200MB RAM
4. **Session state**: Model được cache trong session để tránh reload

## 🔧 Troubleshooting

### Lỗi: "Không tìm thấy model"
```bash
# Kiểm tra đường dẫn model
ls models_inference/YOLOV8/content/runs/detect/train/weights/best.pt
ls models_inference/YOLOV11/content/runs/detect/train/weights/best.pt
```

### Lỗi: "Out of memory"
- Giảm kích thước ảnh trước khi xử lý
- Sử dụng model nhẹ hơn (yolov8n thay vì yolov8x)
- Hoặc dùng "OCR trực tiếp"

### QR code bị lỗi ký tự
✅ Đã fix! Hàm `qr_code_detection()` tự động sửa các ký tự lỗi.
