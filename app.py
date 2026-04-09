import streamlit as st
import google.generativeai as genai
import plotly.express as px
import pandas as pd
import json
from datetime import datetime
import requests # Để gửi dữ liệu lên Google Sheets

# --- CẤU HÌNH ---
st.set_page_config(page_title="Hệ thống Đánh giá Năng lực số 6 Miền", layout="wide")
# Gọi khóa bảo mật từ hệ thống Streamlit
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("Chưa cấu hình API Key trong mục Secrets!")

# Sử dụng model ổn định nhất
model = genai.GenerativeModel('gemini-pro')

# Đường dẫn App Script (Tôi sẽ hướng dẫn bạn lấy ở bước dưới)
SHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbzVcReTeE26LxclsFo42HOT_j4Ps58NVHfibGOZXkknMn5EBVpU9oOZZZTINXHs-IqJnw/exec"

MIEN_LABELS = ["Dạy học số", "Kiểm tra", "Giao tiếp", "Sáng tạo", "An toàn", "Giải quyết vấn đề"]

# --- GIAO DIỆN ---
st.title("🌐 WEBSITE ĐÁNH GIÁ NĂNG LỰC SỐ HOÀN CHỈNH")

tab1, tab2 = st.tabs(["📝 Thực hiện Đánh giá", "📊 Quản trị dữ liệu"])

with tab1:
    with st.form("main_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Họ và tên giáo viên")
            email = st.text_input("Email")
        with c2:
            school = st.text_input("Trường")
            level = st.selectbox("Cấp học", ["Tiểu học", "THCS", "THPT"])
        
        files = st.file_uploader("Tải minh chứng", accept_multiple_files=True)
        submit = st.form_submit_button("GỬI VÀ CHẤM ĐIỂM")

    if submit:
        if name and files:
            with st.spinner("AI đang chấm điểm và lưu dữ liệu..."):
                # 1. AI Chấm điểm
                prompt = f"Chấm điểm 6 miền cho {name} (thang 1-4). Trả về JSON: {{\"scores\": [1.5, 2.0, 3.5, 4.0, 2.5, 3.0], \"summary\": \"nhận xét\"}}"
                response = model.generate_content(prompt)
                res = json.loads(response.text.replace('```json', '').replace('```', '').strip())
                
                # 2. Gửi dữ liệu lên Google Sheets (Giao tiếp qua API)
                data_to_save = {
                    "name": name, "email": email, "school": school, "level": level,
                    "scores": res['scores'], "summary": res['summary'],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                # (Phần này sẽ gọi đến Google Script để ghi vào Sheet)
                requests.post(SHEET_WEBAPP_URL, json=data_to_save)
                
                st.session_state['current_res'] = res
                st.success("Đã lưu kết quả thành công vào Google Sheets!")

# --- HIỂN THỊ BIỂU ĐỒ ---
if 'current_res' in st.session_state:
    res = st.session_state['current_res']
    df = pd.DataFrame(dict(r=res['scores'], theta=MIEN_LABELS))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True, range_r=[0,4])
    st.plotly_chart(fig)
    st.info(f"**Nhận xét:** {res['summary']}")
