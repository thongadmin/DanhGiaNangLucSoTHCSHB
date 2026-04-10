import streamlit as st
import google.generativeai as genai
import plotly.express as px
import pandas as pd
import json
from datetime import datetime
import requests
import google.generativeai as genai
import os

# --- CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="AI Digital Competence Assessment", layout="wide")
API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("models/gemini-1.5-flash")

response = model.generate_content(
    "Hello",
    generation_config={
        "response_mime_type": "text/plain"
    }
)

print(response.text)

# URL Google App Script để lưu dữ liệu (Tùy chọn)
SHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbzVcReTeE26LxclsFo42HOT_j4Ps58NVHfibGOZXkknMn5EBVpU9oOZZZTINXHs-IqJnw/exec"

# Danh sách 6 miền năng lực theo ảnh
MIEN_LABELS = [
    "Miền 1: Dạy học số", 
    "Miền 2: Kiểm tra đánh giá", 
    "Miền 3: Trao quyền người học", 
    "Miền 4: Kỹ năng công nghệ", 
    "Miền 5: Phát triển chuyên môn", 
    "Miền 6: Trí tuệ nhân tạo (AI)"
]

# --- GIAO DIỆN ---
st.title("🛡️ HỆ THỐNG AI ĐÁNH GIÁ NĂNG LỰC SỐ QUA 6 MIỀN")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📝 Thực hiện Đánh giá", "📊 Kết quả & Báo cáo", "⚙️ Quản trị hệ thống"])

with tab1:
    st.header("Nhập thông tin & Minh chứng")
    with st.form("assessment_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Họ và tên")
            unit = st.text_input("Đơn vị công tác")
        with col2:
            role = st.selectbox("Đối tượng", ["Giáo viên", "Nhân viên", "Quản lý"])
            email = st.text_input("Email nhận báo cáo")
        
        st.info("💡 Hãy tải lên các minh chứng (Giáo án số, Đề kiểm tra, Sản phẩm số, Chứng chỉ...)")
        uploaded_files = st.file_uploader("Tải lên minh chứng (PDF, Hình ảnh, Word)", accept_multiple_files=True)
        
        submit_btn = st.form_submit_button("PHÂN TÍCH VÀ CHẤM ĐIỂM BẰNG AI")

    if submit_btn:
        if name and uploaded_files:
            with st.spinner("AI đang phân tích minh chứng và chấm điểm..."):
                # Giả lập logic Prompt cho AI (Trong thực tế bạn sẽ gửi nội dung file cho Gemini)
                prompt = f"""
                Bạn là chuyên gia đánh giá năng lực số giáo viên theo tiêu chuẩn 6 miền.
                Hãy chấm điểm cho {name} (thang điểm 4.0) dựa trên các miền sau: {', '.join(MIEN_LABELS)}.
                Trả về kết quả dưới dạng JSON duy nhất: {{"scores": [v1, v2, v3, v4, v5, v6], "summary": "Nhận xét chi tiết"}}
                """
                
                try:
                    response = model.generate_content(prompt)
                    # Làm sạch phản hồi JSON từ AI
                    clean_res = response.text.replace('```json', '').replace('```', '').strip()
                    res_data = json.loads(clean_res)
                    
                    # Lưu kết quả vào session state
                    st.session_state['assessment_result'] = {
                        "info": {"Họ tên": name, "Đơn vị": unit, "Đối tượng": role},
                        "scores": res_data['scores'],
                        "summary": res_data['summary']
                    }
                    st.success("Đã hoàn thành đánh giá!")
                except Exception as e:
                    st.error(f"Lỗi phân tích AI: {e}")
        else:
            st.warning("Vui lòng điền tên và tải lên minh chứng.")

with tab2:
    if 'assessment_result' in st.session_state:
        res = st.session_state['assessment_result']
        
        st.subheader(f"Báo cáo năng lực số: {res['info']['Họ tên']}")
        
        col_chart, col_text = st.columns([2, 1])
        
        with col_chart:
            # Vẽ biểu đồ Radar (Spider Chart)
            df_chart = pd.DataFrame(dict(r=res['scores'], theta=MIEN_LABELS))
            fig = px.line_polar(df_chart, r='r', theta='theta', line_close=True, 
                               range_r=[0, 4], template="plotly_dark",
                               title="Biểu đồ đa giác năng lực số")
            fig.update_traces(fill='toself')
            st.plotly_chart(fig, use_container_width=True)
            
        with col_text:
            st.write("**Điểm trung bình:**", round(sum(res['scores'])/6, 2))
            st.write("**Nhận xét tổng quát:**")
            st.info(res['summary'])
            
            # Nút xuất PDF (Giả lập)
            st.download_button("Tải Báo cáo (PDF)", data="...", file_name=f"Bao_cao_{name}.pdf")
    else:
        st.info("Chưa có dữ liệu đánh giá. Vui lòng thực hiện tại Tab 1.")

with tab3:
    st.header("Dashboard Quản trị")
    st.write("Dữ liệu tổng hợp từ các giáo viên/nhân viên đã thực hiện.")
    # Hiển thị bảng dữ liệu mẫu
    data_summary = pd.DataFrame([
        {"Họ tên": "Nguyễn Văn A", "Đơn vị": "Trường THPT X", "Điểm TB": 3.5, "Ngày": "2026-04-10"},
        {"Họ tên": "Trần Thị B", "Đơn vị": "Phòng GD", "Điểm TB": 2.8, "Ngày": "2026-04-09"}
    ])
    st.table(data_summary)
