import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
import io
import pandas as pd
from utils.ocr import qr_code_detection, OCR_img

def parse_qr_result(qr_string):
    """
    Phân tích chuỗi QR code và trả về thông tin có cấu trúc
    Format: cccd|cmnd|họ và tên|ngày tháng năm sinh|giới tính|Nơi thường trú|ngày tháng năm cấp|...
    """
    try:
        # Tách chuỗi theo dấu |
        parts = qr_string.split('|')
        
        if len(parts) >= 7:
            parsed_info = {
                'Số CCCD/CMND': parts[0] if parts[0] else 'Không có',
                'Số CMND cũ': parts[1] if parts[1] else 'Không có',
                'Họ và tên': parts[2] if parts[2] else 'Không có',
                'Ngày sinh': parts[3] if parts[3] else 'Không có',
                'Giới tính': parts[4] if parts[4] else 'Không có',
                'Nơi thường trú': parts[5] if parts[5] else 'Không có',
                'Ngày cấp': parts[6] if parts[6] else 'Không có',
            }
            
            # Xử lý định dạng ngày sinh
            if parsed_info['Ngày sinh'] != 'Không có' and len(parsed_info['Ngày sinh']) == 8:
                date_str = parsed_info['Ngày sinh']
                formatted_date = f"{date_str[0:2]}/{date_str[2:4]}/{date_str[4:8]}"
                parsed_info['Ngày sinh'] = formatted_date
            
            # Xử lý định dạng ngày cấp
            if parsed_info['Ngày cấp'] != 'Không có' and len(parsed_info['Ngày cấp']) == 8:
                date_str = parsed_info['Ngày cấp']
                formatted_date = f"{date_str[0:2]}/{date_str[2:4]}/{date_str[4:8]}"
                parsed_info['Ngày cấp'] = formatted_date
            
            return parsed_info
        else:
            return {'Lỗi': 'Định dạng QR code không đúng', 'Dữ liệu gốc': qr_string}
            
    except Exception as e:
        return {'Lỗi': f'Không thể phân tích: {str(e)}', 'Dữ liệu gốc': qr_string}

def display_parsed_info(parsed_info):
    """
    Hiển thị thông tin đã phân tích dưới dạng đẹp mắt
    """
    st.success("✅ Phân tích thông tin QR code thành công!")
    
    # Tạo 2 cột để hiển thị thông tin
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown("### 👤 **Thông tin cá nhân**")
        st.markdown(f"**🆔 Số CCCD/CMND:** {parsed_info.get('Số CCCD/CMND', 'N/A')}")
        st.markdown(f"**🎂 Ngày sinh:** {parsed_info.get('Ngày sinh', 'N/A')}")
        st.markdown(f"**⚧ Giới tính:** {parsed_info.get('Giới tính', 'N/A')}")
        
    with info_col2:
        st.markdown("### 📄 **Thông tin giấy tờ**") 
        st.markdown(f"**📋 Số CMND cũ:** {parsed_info.get('Số CMND cũ', 'N/A')}")
        st.markdown(f"**📅 Ngày cấp:** {parsed_info.get('Ngày cấp', 'N/A')}")
    
    st.markdown("### 👨‍👩‍👧‍👦 **Thông tin khác**")
    st.markdown(f"**📝 Họ và tên:** {parsed_info.get('Họ và tên', 'N/A')}")
    st.markdown(f"**🏠 Nơi thường trú:** {parsed_info.get('Nơi thường trú', 'N/A')}")
    
    # Hiển thị bảng thông tin dạng table
    st.markdown("---")
    st.markdown("### 📊 **Bảng thông tin chi tiết**")
    
    df_data = []
    for key, value in parsed_info.items():
        if key not in ['Lỗi', 'Dữ liệu gốc']:
            df_data.append({'Thông tin': key, 'Giá trị': value})
    
    if df_data:
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

def process_images(front_image, back_image, cccd_type):
    """
    Xử lý ảnh tùy theo loại CCCD với 2 ảnh được upload cùng lúc
    """
    results = {}
    
    if cccd_type == "CCCD Mới":
        # CCCD Mới: Quét QR ở mặt sau, OCR ở mặt trước
        if back_image is not None:
            st.info("🔍 Đang quét QR code ở mặt sau CCCD mới...")
            
            # Chuyển đổi ảnh mặt sau thành OpenCV image
            back_file_bytes = np.asarray(bytearray(back_image.read()), dtype=np.uint8)
            back_img = cv2.imdecode(back_file_bytes, 1)
            
            # Quét QR code với nhiều scale khác nhau
            qr_result = None
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, scale in enumerate([1, 2, 3]):
                status_text.text(f"Đang thử scale {scale}...")
                progress_bar.progress((i + 1) / 3)
                qr_result = qr_code_detection(back_img, scale=scale)
                if qr_result:
                    break
            
            progress_bar.empty()
            status_text.empty()
            
            if qr_result:
                results['qr_code'] = qr_result
                st.success("✅ Đã quét được QR code!")
                st.text_area("Kết quả QR code:", qr_result, height=100)
            else:
                st.warning("⚠️ Không quét được QR code, chuyển sang OCR mặt trước...")
                results['qr_code'] = None
                
                if front_image is not None:
                    # Chuyển đổi ảnh mặt trước thành OpenCV image
                    front_file_bytes = np.asarray(bytearray(front_image.read()), dtype=np.uint8)
                    front_img = cv2.imdecode(front_file_bytes, 1)
                    
                    st.info("🔍 Đang thực hiện OCR...")
                    ocr_result = OCR_img(front_img)
                    results['ocr_text'] = ocr_result
                    
                    st.success("✅ Hoàn thành OCR!")
                    st.text_area("Kết quả OCR:", '\n'.join(ocr_result), height=200)
                else:
                    st.error("❌ Cần ảnh mặt trước để thực hiện OCR!")
        else:
            st.error("❌ Cần ảnh mặt sau để quét QR code!")
    
    elif cccd_type == "CCCD Cũ":
        # CCCD Cũ: Quét QR ở mặt trước, OCR ở mặt trước
        if front_image is not None:
            st.info("🔍 Đang quét QR code ở mặt trước CCCD cũ...")
            
            # Chuyển đổi ảnh mặt trước thành OpenCV image
            front_file_bytes = np.asarray(bytearray(front_image.read()), dtype=np.uint8)
            front_img = cv2.imdecode(front_file_bytes, 1)
            
            # Quét QR code với nhiều scale khác nhau
            qr_result = None
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, scale in enumerate([1, 2, 3]):
                status_text.text(f"Đang thử scale {scale}...")
                progress_bar.progress((i + 1) / 3)
                qr_result = qr_code_detection(front_img, scale=scale)
                if qr_result:
                    break
            
            progress_bar.empty()
            status_text.empty()
            
            if qr_result:
                results['qr_code'] = qr_result
                st.success("✅ Đã quét được QR code!")
                st.text_area("Kết quả QR code:", qr_result, height=100)
            else:
                st.warning("⚠️ Không quét được QR code, chuyển sang OCR...")
                results['qr_code'] = None
                
                # Thực hiện OCR trên cùng ảnh mặt trước
                st.info("🔍 Đang thực hiện OCR...")
                ocr_result = OCR_img(front_img)
                results['ocr_text'] = ocr_result
                
                st.success("✅ Hoàn thành OCR!")
                st.text_area("Kết quả OCR:", '\n'.join(ocr_result), height=200)
        else:
            st.error("❌ Cần ảnh mặt trước để quét QR code!")
    
    return results

def capture_image_from_camera():
    """
    Chụp ảnh từ camera sử dụng st.camera_input
    """
    camera_photo = st.camera_input("📸 Chụp ảnh từ camera")
    
    if camera_photo is not None:
        # Chuyển đổi thành PIL Image
        image = Image.open(camera_photo)
        return image
    return None

def convert_pil_to_opencv(pil_image):
    """
    Chuyển đổi PIL Image thành OpenCV image
    """
    if pil_image is not None:
        # Chuyển PIL image thành numpy array
        numpy_image = np.array(pil_image)
        # Chuyển từ RGB sang BGR (OpenCV format)
        opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
        return opencv_image
    return None

def process_images_from_source(front_source, back_source, cccd_type):
    """
    Xử lý ảnh từ nhiều nguồn khác nhau (upload file hoặc camera)
    """
    results = {}
    front_img = None
    back_img = None
    
    # Xử lý ảnh mặt trước
    if front_source is not None:
        if hasattr(front_source, 'read'):  # File upload
            front_file_bytes = np.asarray(bytearray(front_source.read()), dtype=np.uint8)
            front_img = cv2.imdecode(front_file_bytes, 1)
        else:  # PIL Image từ camera
            front_img = convert_pil_to_opencv(front_source)
    
    # Xử lý ảnh mặt sau
    if back_source is not None:
        if hasattr(back_source, 'read'):  # File upload
            back_file_bytes = np.asarray(bytearray(back_source.read()), dtype=np.uint8)
            back_img = cv2.imdecode(back_file_bytes, 1)
        else:  # PIL Image từ camera
            back_img = convert_pil_to_opencv(back_source)
    
    # Logic xử lý tương tự như function cũ
    if cccd_type == "CCCD Mới":
        # CCCD Mới: Quét QR ở mặt sau, OCR ở mặt trước
        if back_img is not None:
            st.info("🔍 Đang quét QR code ở mặt sau CCCD mới...")
            
            # Quét QR code với nhiều scale khác nhau
            qr_result = None
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, scale in enumerate([1, 2, 3]):
                status_text.text(f"Đang thử scale {scale}...")
                progress_bar.progress((i + 1) / 3)
                qr_result = qr_code_detection(back_img, scale=scale)
                if qr_result:
                    break
            
            progress_bar.empty()
            status_text.empty()
            
            if qr_result:
                results['qr_code'] = qr_result
                st.success("✅ Đã quét được QR code!")
                
                # Phân tích và hiển thị thông tin QR
                parsed_info = parse_qr_result(qr_result)
                if 'Lỗi' in parsed_info:
                    st.warning("⚠️ Có lỗi khi phân tích QR code:")
                    st.error(parsed_info['Lỗi'])
                    st.text_area("Dữ liệu QR gốc:", qr_result, height=100)
                else:
                    display_parsed_info(parsed_info)
                    
                    # Hiển thị dữ liệu gốc trong expander
                    with st.expander("🔍 Xem dữ liệu QR gốc"):
                        st.code(qr_result)
            else:
                st.warning("⚠️ Không quét được QR code, chuyển sang OCR mặt trước...")
                results['qr_code'] = None
                
                if front_img is not None:
                    st.info("🔍 Đang thực hiện OCR...")
                    ocr_result = OCR_img(front_img)
                    results['ocr_text'] = ocr_result
                    
                    st.success("✅ Hoàn thành OCR!")
                    st.text_area("Kết quả OCR:", '\n'.join(ocr_result), height=200)
                else:
                    st.error("❌ Cần ảnh mặt trước để thực hiện OCR!")
        else:
            st.error("❌ Cần ảnh mặt sau để quét QR code!")
    
    elif cccd_type == "CCCD Cũ":
        # CCCD Cũ: Quét QR ở mặt trước, OCR ở mặt trước
        if front_img is not None:
            st.info("🔍 Đang quét QR code ở mặt trước CCCD cũ...")
            
            # Quét QR code với nhiều scale khác nhau
            qr_result = None
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, scale in enumerate([1, 2, 3]):
                status_text.text(f"Đang thử scale {scale}...")
                progress_bar.progress((i + 1) / 3)
                qr_result = qr_code_detection(front_img, scale=scale)
                if qr_result:
                    break
            
            progress_bar.empty()
            status_text.empty()
            
            if qr_result:
                results['qr_code'] = qr_result
                st.success("✅ Đã quét được QR code!")
                
                # Phân tích và hiển thị thông tin QR
                parsed_info = parse_qr_result(qr_result)
                if 'Lỗi' in parsed_info:
                    st.warning("⚠️ Có lỗi khi phân tích QR code:")
                    st.error(parsed_info['Lỗi'])
                    st.text_area("Dữ liệu QR gốc:", qr_result, height=100)
                else:
                    display_parsed_info(parsed_info)
                    
                    # Hiển thị dữ liệu gốc trong expander
                    with st.expander("🔍 Xem dữ liệu QR gốc"):
                        st.code(qr_result)
            else:
                st.warning("⚠️ Không quét được QR code, chuyển sang OCR...")
                results['qr_code'] = None
                
                # Thực hiện OCR trên cùng ảnh mặt trước
                st.info("🔍 Đang thực hiện OCR...")
                ocr_result = OCR_img(front_img)
                results['ocr_text'] = ocr_result
                
                st.success("✅ Hoàn thành OCR!")
                st.text_area("Kết quả OCR:", '\n'.join(ocr_result), height=200)
        else:
            st.error("❌ Cần ảnh mặt trước để quét QR code!")
    
    return results

def main():
    st.set_page_config(
        page_title="CCCD Scanner",
        page_icon="🆔",
        layout="wide"
    )
    
    st.title("🆔 Ứng dụng quét CCCD")
    st.markdown("---")
    
    # Sidebar cho cấu hình
    with st.sidebar:
        st.header("⚙️ Cấu hình")
        
        # Chọn loại CCCD
        cccd_type = st.selectbox(
            "Chọn loại CCCD:",
            options=["CCCD Mới", "CCCD Cũ"],
            help="CCCD Mới: Quét QR ở mặt sau | CCCD Cũ: Quét QR ở mặt trước"
        )
        
        # Chọn phương thức nhập ảnh
        input_method = st.radio(
            "Phương thức nhập ảnh:",
            options=["📁 Upload file", "📸 Chụp camera"],
            help="Chọn cách thức để lấy ảnh CCCD"
        )
        
        st.markdown("---")
        st.markdown("### 📋 Hướng dẫn:")
        if input_method == "📁 Upload file":
            if cccd_type == "CCCD Mới":
                st.markdown("""
                1. Upload ảnh **mặt sau** (bắt buộc) để quét QR code
                2. Upload ảnh **mặt trước** (tùy chọn) để OCR khi QR thất bại
                3. Nhấn "Bắt đầu xử lý"
                """)
            else:
                st.markdown("""
                1. Upload ảnh **mặt trước** (bắt buộc) để quét QR code
                2. Ảnh mặt sau không cần thiết cho CCCD cũ
                3. Nhấn "Bắt đầu xử lý"
                """)
        else:  # Camera
            if cccd_type == "CCCD Mới":
                st.markdown("""
                1. Chụp ảnh **mặt sau** (bắt buộc) để quét QR code
                2. Chụp ảnh **mặt trước** (tùy chọn) để OCR khi QR thất bại
                3. Nhấn "Bắt đầu xử lý"
                """)
            else:
                st.markdown("""
                1. Chụp ảnh **mặt trước** (bắt buộc) để quét QR code
                2. Ảnh mặt sau không cần thiết cho CCCD cũ
                3. Nhấn "Bắt đầu xử lý"
                """)
        
        st.markdown("---")
        st.markdown("### ⚙️ Cải tiến:")
        st.markdown("""
        - 🔄 Thử 3 scale khác nhau (1→2→3) để quét QR
        - 📤 Upload file hoặc chụp camera
        - 📸 Chụp trực tiếp từ camera
        - 🎯 Xử lý thông minh theo loại CCCD
        """)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(f"📤 {input_method} - {cccd_type}")
        
        front_source = None
        back_source = None
        
        if input_method == "📁 Upload file":
            # Giao diện upload file
            upload_col1, upload_col2 = st.columns(2)
            
            with upload_col1:
                st.subheader("📄 Ảnh mặt trước")
                front_source = st.file_uploader(
                    "Upload ảnh mặt trước CCCD:",
                    type=['jpg', 'jpeg', 'png'],
                    help="Hỗ trợ định dạng: JPG, JPEG, PNG",
                    key="front_upload"
                )
                
                if front_source is not None:
                    image_front = Image.open(front_source)
                    st.image(image_front, caption="Mặt trước", use_container_width=True)
            
            with upload_col2:
                st.subheader("📄 Ảnh mặt sau")
                back_source = st.file_uploader(
                    "Upload ảnh mặt sau CCCD:",
                    type=['jpg', 'jpeg', 'png'],
                    help="Hỗ trợ định dạng: JPG, JPEG, PNG",
                    key="back_upload"
                )
                
                if back_source is not None:
                    image_back = Image.open(back_source)
                    st.image(image_back, caption="Mặt sau", use_container_width=True)
        
        else:  # Camera input
            # Giao diện chụp camera
            camera_col1, camera_col2 = st.columns(2)
            
            with camera_col1:
                st.subheader("📸 Chụp mặt trước")
                with st.expander("📷 Camera mặt trước", expanded=True):
                    front_camera = st.camera_input("Chụp ảnh mặt trước CCCD", key="front_camera")
                    if front_camera is not None:
                        front_source = Image.open(front_camera)
                        st.image(front_source, caption="Mặt trước (vừa chụp)", use_container_width=True)
            
            with camera_col2:
                st.subheader("📸 Chụp mặt sau")
                with st.expander("📷 Camera mặt sau", expanded=True):
                    back_camera = st.camera_input("Chụp ảnh mặt sau CCCD", key="back_camera")
                    if back_camera is not None:
                        back_source = Image.open(back_camera)
                        st.image(back_source, caption="Mặt sau (vừa chụp)", use_container_width=True)
        
        # Nút xử lý
        st.markdown("---")
        process_button = st.button("🚀 Bắt đầu xử lý", type="primary", use_container_width=True)
        
        if process_button:
            # Kiểm tra ảnh cần thiết theo loại CCCD
            can_process = False
            
            if cccd_type == "CCCD Mới":
                if back_source is not None:
                    can_process = True
                    if front_source is None:
                        st.warning("⚠️ Chưa có ảnh mặt trước. Nếu QR không quét được sẽ không thể OCR.")
                else:
                    st.error("❌ Cần ảnh mặt sau để quét QR code cho CCCD mới!")
            
            elif cccd_type == "CCCD Cũ":
                if front_source is not None:
                    can_process = True
                else:
                    st.error("❌ Cần ảnh mặt trước để quét QR code cho CCCD cũ!")
            
            if can_process:
                # Reset file pointers nếu là upload file
                if input_method == "📁 Upload file":
                    if front_source and hasattr(front_source, 'seek'):
                        front_source.seek(0)
                    if back_source and hasattr(back_source, 'seek'):
                        back_source.seek(0)
                
                # Xử lý ảnh
                with st.spinner("Đang xử lý..."):
                    results = process_images_from_source(front_source, back_source, cccd_type)
    
    with col2:
        st.header("ℹ️ Thông tin")
        
        st.info(f"**Loại CCCD:** {cccd_type}")
        
        if cccd_type == "CCCD Mới":
            st.markdown("""
            **Quy trình:**
            1. Quét QR code ở mặt sau (scale 1→3)
            2. Nếu thất bại → OCR mặt trước
            """)
        else:
            st.markdown("""
            **Quy trình:**
            1. Quét QR code ở mặt trước (scale 1→3)
            2. Nếu thất bại → OCR mặt trước
            """)
        
        st.markdown("---")
        st.markdown("### 🔧 Tính năng:")
        st.markdown("""
        - ✅ Quét QR code tự động với 3 scale
        - ✅ OCR văn bản tiếng Việt
        - ✅ Hỗ trợ CCCD mới và cũ
        - ✅ Upload file hoặc chụp camera
        - 📸 Chụp trực tiếp từ camera
        - ✅ Giao diện thân thiện
        """)

if __name__ == "__main__":
    main()