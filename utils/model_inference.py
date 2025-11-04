import os
from ultralytics import YOLO
import numpy as np
import cv2
from PIL import Image

def get_class():
    """
    Get the class names for the model.

    Returns:
        class_names : list : List of class names
    """
    return ['current_place', 'dob', 'expire_date', 'features', 'finger_print', 'gender', 'id', 'issue_date', 'name', 'nationality', 'origin_place', 'qr']

def get_class_vietnamese():
    """
    Get the Vietnamese labels for the model classes.

    Returns:
        dict : Mapping from English class names to Vietnamese labels
    """
    return {
        'id': 'Số CCCD',
        'name': 'Họ và tên',
        'dob': 'Ngày sinh',
        'gender': 'Giới tính',
        'nationality': 'Quốc tịch',
        'origin_place': 'Quê quán',
        'current_place': 'Nơi thường trú',
        'issue_date': 'Ngày cấp',
        'expire_date': 'Ngày hết hạn',
        'features': 'Đặc điểm nhận dạng',
        'finger_print': 'Vân tay',
        'qr': 'Mã QR'
    }

def get_required_fields():
    """
    Get the list of required fields for a valid CCCD scan.
    
    Note: 'features' and 'finger_print' are optional fields.

    Returns:
        list : List of required field names
    """
    return ['id', 'name', 'dob', 'gender', 'current_place']

def get_optional_fields():
    """
    Get the list of optional fields that may not appear on all CCCDs.

    Returns:
        list : List of optional field names
    """
    return ['features', 'finger_print', 'expire_date', 'nationality', 'origin_place', 'issue_date', 'qr']

def get_model_path(model_name='yolov8', model_dir='models_inference'):
    """
    Get the file path of a model.

    Parameters:
        model_name : str : Name of the model variant (e.g., yolov8, yolov11, etc.)
        model_dir : str : Directory where models are stored

    Returns:
        model_path : str : Path to the model file
    """
    model_filename = f"best.pt"
    model_path = os.path.join(os.getcwd(), model_dir, model_name.upper(), "content/runs/detect/train/weights", model_filename)
    return model_path

def get_model(model_name='yolov8', device='cpu'):
    """
    Load and return a model.

    Parameters:
        model_name : str : Name of the model variant (e.g., yolov8, yolov11, etc.)
        device : str : Device to load the model on ('cpu' or 'cuda')

    Returns:
        model : model
    """
    model = YOLO(get_model_path(model_name)).to(device)
    return model

def compare_white_pixels(image):
    """
    Returns True if the left half of image
    has more white pixels than the right half

    Parameters:
        image : np.ndarray
    """

    width = image.shape[1]
    left_region = image[:, :int(width / 2)]
    right_region = image[:, int(width / 2):]

    left_white_pixels = np.sum(left_region == 255)
    right_white_pixels = np.sum(right_region == 255)

    return left_white_pixels > right_white_pixels

def rotate_if_necessary(image):
    """
    Resets an image that has been rotated 90°/180°/270°.

    Parameters
        image : np.ndarray
    """

    # Reset image to horizontal position if necessary
    if image.shape[0] > image.shape[1]:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    # Convert image to grayscale
    image_binary = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Apply some Gaussian blur and then Otsu's thresholding
    image_binary = cv2.GaussianBlur(image_binary,(5,5),0)
    _, image_binary = cv2.threshold(image_binary, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Rotate image by 180° if necessary
    if not compare_white_pixels(image_binary):
        image = cv2.rotate(image, cv2.ROTATE_180)

    return image

def retrieve_documents_from_image(model, image_path):
    results = model(image_path)
    predictions = results[0].boxes.data.tolist()

    im = Image.open(image_path)
    im = np.array(im)

    docs = []

    for prediction in predictions:
        pred_class = int(prediction[-1])
        x1, y1, x2, y2 = prediction[:4]
        docs.append((im[int(y1):int(y2), int(x1):int(x2)], pred_class))

    return docs