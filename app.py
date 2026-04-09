import streamlit as st
import google.generativeai as genai
import plotly.express as px
import pandas as pd
import json
from datetime import datetime
import requests

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ thống Đánh giá Năng lực số 6 Miền", layout="wide", page_icon="🌐")

# --- KẾT NỐI API TỪ SECRETS ---
# Thay thế đoạn khởi tạo model cũ bằng đoạn này:
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # Chiến thuật: Thử Flash trước, nếu lỗi thì thử Pro
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except:
        model = genai.GenerativeModel('gemini-1.0-pro')
        
except Exception as e:
    st.error(f"Lỗi kết nối API: {e}")

# URL Google App Script để lưu dữ liệu vào Sheets
SHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbzVcReTeE26LxclsFo42HOT_j4Ps58NVHfibGOZXkknMn5EBVpU9oOZZZTINXHs-IqJnw/exec"

MIEN_LABELS = ["Dạy học số", "Kiểm tra", "Giao tiếp", "Sáng tạo", "An toàn", "Giải quyết vấn đề"]

# --- GIAO DIỆN CHÍNH ---
st.title("🌐 WEBSITE ĐÁNH GIÁ NĂNG LỰC SỐ HOÀN CHỈNH")
st.markdown("---")

tab1, tab2 = st.tabs(["📝 Thực hiện Đánh giá", "📊 Kết quả Dashboard"])

with tab1:
    with st.form("main_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Họ và tên giáo viên", placeholder="VD: Nguyễn Văn A")
            email = st.text_input("Email", placeholder="example@gmail.com")
        with c2:
            school = st.text_input("Trường", placeholder="Tên trường học")
            level = st.selectbox("Cấp học", ["Tiểu học", "THCS", "THPT"])
        
        files = st.file_uploader("Tải minh chứng (Ảnh, PDF, Docx...)", accept_multiple_files=True)
        submit = st.form_submit_button("GỬI VÀ CHẤM ĐIỂM 🚀")

    if submit:
        if not name or not files:
            st.warning("Vui lòng nhập đầy đủ thông tin và tải lên minh chứng!")
        else:
            with st.spinner("AI đang phân tích và lưu dữ liệu vào Google Sheets..."):
                try:
                    # 1. AI Phân tích minh chứng
                    prompt = f"""Bạn là chuyên gia đánh giá năng lực số giáo viên. 
                    Hãy phân tích hồ sơ của giáo viên {name}.
                    Chấm điểm 6 miền từ 1.0 đến 4.0.
                    Trả về duy nhất định dạng JSON sau:
                    {{"scores": [số1, số2, số3, số4, số5, số6], "summary": "Nhận xét ngắn gọn ưu nhược điểm"}}"""
                    
                    response = model.generate_content(prompt)
                    
                    # 2. Xử lý kết quả trả về
                    clean_text = response.text.strip().replace('```json', '').replace('```', '')
                    res = json.loads(clean_text)
                    
                    # 3. Ghi dữ liệu vào Google Sheets
                    data_to_save = {
                        "name": name, 
                        "email": email, 
                        "school": school, 
                        "level": level,
                        "scores": res['scores'], 
                        "summary": res['summary'],
                        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }
                    
                    requests.post(SHEET_WEBAPP_URL, json=data_to_save)
                    
                    # Lưu vào session để hiển thị
                    st.session_state['current_res'] = res
                    st.session_state['teacher_name'] = name
                    st.success("✅ Đã lưu kết quả thành công vào Google Sheets!")
                    
                except Exception as e:
                    st.error(f"❌ Lỗi xử lý: {e}")

# --- HIỂN THỊ KẾT QUẢ ---
with tab2:
    if 'current_res' in st.session_state:
        res = st.session_state['current_res']
        t_name = st.session_state['teacher_name']
        
        st.header(f"📊 Kết quả của: {t_name}")
        
        col_chart, col_info = st.columns([1.5, 1])
        
        with col_chart:
            # Vẽ biểu đồ Radar (Spider Chart)
            df = pd.DataFrame(dict(r=res['scores'], theta=MIEN_LABELS))
            fig = px.line_polar(df, r='r', theta='theta', line_close=True, range_r=[0,4])
            fig.update_traces(fill='toself', fillcolor='rgba(31, 119, 180, 0.3)', line_color='#1f77b4')
            st.plotly_chart(fig, use_container_width=True)
        
        with col_info:
            st.subheader("📝 Nhận xét chi tiết")
            st.info(res['summary'])
            
            # Thanh tiến trình điểm số
            for label, score in zip(MIEN_LABELS, res['scores']):
                st.write(f"**{label}:** {score}/4.0")
                st.progress(score/4.0)
    else:
        st.info("Mời bạn thực hiện đánh giá ở Tab 1 để xem kết quả tại đây.")
