import streamlit as st
import google.generativeai as genai
import plotly.express as px
import pandas as pd
import json
from datetime import datetime
import requests

st.set_page_config(page_title="Hệ thống Đánh giá Năng lực số 6 Miền", layout="wide")

# --- KẾT NỐI API ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Chưa cấu hình API Key trong Secrets!")
    st.stop()

# CHIẾN THUẬT: Tự động tìm model khả dụng để tránh lỗi 404
@st.cache_resource
def load_model():
    # Thử danh sách các tên model từ mới đến cũ
    for model_name in ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']:
        try:
            m = genai.GenerativeModel(model_name)
            # Thử tạo một nội dung nhỏ để kiểm tra model có sống không
            m.generate_content("test", generation_config={"max_output_tokens": 1})
            return m
        except:
            continue
    return None

model = load_model()

if model is None:
    st.error("❌ Google API đang bảo trì hoặc Key của bạn gặp vấn đề. Hãy thử tạo Key mới tại Google AI Studio.")
    st.stop()

# --- CẤU HÌNH CÒN LẠI ---
SHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbzVcReTeE26LxclsFo42HOT_j4Ps58NVHfibGOZXkknMn5EBVpU9oOZZZTINXHs-IqJnw/exec"
MIEN_LABELS = ["Dạy học số", "Kiểm tra", "Giao tiếp", "Sáng tạo", "An toàn", "Giải quyết vấn đề"]

st.title("🌐 WEBSITE ĐÁNH GIÁ NĂNG LỰC SỐ")
tab1, tab2 = st.tabs(["📝 Thực hiện Đánh giá", "📊 Kết quả"])

with tab1:
    with st.form("main_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Họ và tên giáo viên")
            email = st.text_input("Email")
        with col2:
            school = st.text_input("Trường")
            level = st.selectbox("Cấp học", ["Tiểu học", "THCS", "THPT"])
        
        files = st.file_uploader("Tải minh chứng", accept_multiple_files=True)
        submit = st.form_submit_button("GỬI VÀ CHẤM ĐIỂM 🚀")

    if submit and name and files:
        with st.spinner("Đang phân tích..."):
            try:
                prompt = f"Chấm điểm 6 miền năng lực số cho {name} (thang 1-4). Trả về JSON: {{\"scores\": [2.0, 3.0, 1.5, 4.0, 2.5, 3.5], \"summary\": \"nhận xét\"}}"
                response = model.generate_content(prompt)
                res = json.loads(response.text.replace('```json', '').replace('```', '').strip())
                
                # Gửi lên Sheets
                requests.post(SHEET_WEBAPP_URL, json={
                    "name": name, "email": email, "school": school, "level": level,
                    "scores": res['scores'], "summary": res['summary'],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                st.session_state['res'] = res
                st.success("✅ Thành công!")
            except Exception as e:
                st.error(f"Lỗi hệ thống: {e}")

if 'res' in st.session_state:
    res = st.session_state['res']
    fig = px.line_polar(pd.DataFrame(dict(r=res['scores'], theta=MIEN_LABELS)), r='r', theta='theta', line_close=True, range_r=[0,4])
    st.plotly_chart(fig)
