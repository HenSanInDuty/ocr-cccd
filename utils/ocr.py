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

    decoded = decode(th)
    if (decoded):
        return decoded[0].data.decode('utf-8')
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