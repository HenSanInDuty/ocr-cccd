import easyocr
import cv2, os
from PIL import Image
from pyzbar.pyzbar import decode, ZBarSymbol
from matplotlib import pyplot as plt

def get_ocr_reader(lang_list=['vi'], gpu=False):
    reader = easyocr.Reader(lang_list, gpu=gpu)
    return reader

def grayscale_conversion(img, scale = 1):
  # Tăng kích thước lên theo scale
  img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

  # Chuyển grayscale
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

  # Làm rõ cạnh
  gray = cv2.GaussianBlur(gray, (3, 3), 0)
  th = cv2.adaptiveThreshold(gray, 255,
                            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                            cv2.THRESH_BINARY, 31, 2)

  return th

def show_img(img):
    plt.figure(figsize=(10, 8))
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()

def qr_code_detection(img, show_image_flag=False, scale=2):
    th = grayscale_conversion(img, scale)
    if (show_image_flag):
        show_img(th)

    # Decode QR code
    decoded = decode(th, symbols=[ZBarSymbol.QRCODE])
    if (decoded):
        data = decoded[0].data
        
        if isinstance(data, bytes):
            # Decode UTF-8 (QR code CCCD Việt Nam dùng UTF-8)
            try:
                result = data.decode('utf-8', errors='strict')
                
                # Kiểm tra xem có ký tự lỗi không (các ký tự CJK lạ, halfwidth katakana)
                error_chars = ['盻', 'ｳ', 'ﾃ', 'ｺ', 'ｺ', 'ﾆ', '｡', 'ｪ', 'ｯ', 'ｺ']
                if any(char in result for char in error_chars):
                    raise ValueError(f"QR code có chứa ký tự lỗi encoding. Vui lòng quét lại hoặc sử dụng ảnh chất lượng tốt hơn.")
                
                return result
            except UnicodeDecodeError as e:
                raise ValueError(f"Lỗi decode QR code: {str(e)}. QR code không đúng định dạng UTF-8.")
        else:
            return data
    else:
        return None
    
def OCR_img(img, show_result=False):
    reader = get_ocr_reader(lang_list=['vi'], gpu=False)
    result = reader.readtext(img)
    boxes = [line[0] for line in result]
    texts = [line[1] for line in result]

    # Tạo bản copy để vẽ bounding boxes
    img_with_boxes = img.copy()
    
    for box in boxes:
        top_left     = (int(box[0][0]), int(box[0][1]))
        bottom_right = (int(box[2][0]), int(box[2][1]))
        cv2.rectangle(img_with_boxes, top_left, bottom_right, (0, 255, 0), 2)

    if show_result:
        show_img(img_with_boxes)
        
    return texts

def OCR_with_detection(img, model, class_names, show_result=False):
    """
    Thực hiện object detection trước, sau đó OCR từng vùng đã detect
    
    Parameters:
        img: OpenCV image (numpy array)
        model: YOLO model đã load
        class_names: List các class names từ get_class()
        show_result: Có hiển thị kết quả hay không
    
    Returns:
        detected_info: Dict mapping từ Vietnamese field name sang text OCR
        img_with_boxes: Ảnh với bounding boxes (nếu show_result=True)
        
    Raises:
        ValueError: Nếu không đủ thông tin bắt buộc
    """
    from utils.model_inference import retrieve_documents_from_image, rotate_if_necessary, get_class_vietnamese, get_required_fields
    import tempfile
    
    # Rotate ảnh nếu cần
    img = rotate_if_necessary(img)
    
    # Lưu ảnh tạm để model có thể đọc
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        tmp_path = tmp_file.name
        cv2.imwrite(tmp_path, img)
    
    try:
        # Thực hiện object detection
        docs = retrieve_documents_from_image(model, tmp_path)
        
        if not docs or len(docs) == 0:
            raise ValueError("Không detect được thông tin nào trên ảnh. Vui lòng chụp lại theo hướng dẫn.")
        
        # Khởi tạo OCR reader
        reader = get_ocr_reader(lang_list=['vi'], gpu=False)
        
        # Dictionary để lưu kết quả (English key)
        detected_info_en = {}
        img_with_boxes = img.copy()
        
        # OCR từng vùng đã detect
        for doc_img, class_id in docs:
            class_name = class_names[class_id]
            
            # Thực hiện OCR
            ocr_result = reader.readtext(doc_img)
            
            # Lấy text từ kết quả OCR
            texts = [line[1] for line in ocr_result]
            combined_text = ' '.join(texts).strip()
            
            # Lưu vào dict (chỉ lưu nếu có text)
            if combined_text:
                detected_info_en[class_name] = combined_text
            
            if show_result:
                # Vẽ bounding box lên ảnh gốc
                # (Cần tính lại tọa độ từ doc_img về img gốc - simplified version)
                pass
        
        # Xóa file tạm
        os.unlink(tmp_path)
        
        # Validate required fields
        required_fields = get_required_fields()
        missing_fields = [field for field in required_fields if field not in detected_info_en or not detected_info_en[field]]
        
        vietnamese_labels = get_class_vietnamese()
        
        if missing_fields:
            missing_vn = [vietnamese_labels.get(field, field) for field in missing_fields]
            raise ValueError(
                f"❌ Thiếu thông tin bắt buộc: {', '.join(missing_vn)}\n\n"
                f"📸 Vui lòng chụp lại theo hướng dẫn:\n"
                f"  • Chụp trực diện CCCD, không bị nghiêng\n"
                f"  • CCCD nằm đầy đủ trong khung ảnh\n"
                f"  • Không chụp quá nhỏ hoặc quá xa\n"
                f"  • Đảm bảo ánh sáng đủ, không quá chói hoặc quá tối\n"
                f"  • Ảnh rõ nét, không bị mờ\n"
                f"  • Tránh phản chiếu ánh sáng lên bề mặt thẻ"
            )
        
        # Chuyển đổi sang Vietnamese labels
        detected_info_vn = {}
        for en_key, text_value in detected_info_en.items():
            vn_key = vietnamese_labels.get(en_key, en_key)
            detected_info_vn[vn_key] = text_value
        
        return detected_info_vn, img_with_boxes
        
    except Exception as e:
        # Xóa file tạm nếu có lỗi
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise e