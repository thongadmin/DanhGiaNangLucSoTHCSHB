import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CẤU HÌNH ---
st.set_page_config(page_title="Hệ thống Đánh giá Năng lực số", layout="wide")

# CSS để giao diện đẹp và hiện đại
st.markdown("""
<style>
    .stApp { background-color: #f4f7f9; }
    .main-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .metric-card { background: white; padding: 20px; border-radius: 12px; border-top: 5px solid #4f46e5; text-align: center; }
    .ai-box { background: linear-gradient(135deg, #6366f1, #a855f7); color: white; padding: 20px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# --- QUẢN LÝ DỮ LIỆU (Giả lập hoặc Kết nối thật) ---
# Trong thực tế, bạn sẽ dùng st.connection("gsheets") để ghi vào Google Sheets
if 'db' not in st.session_state:
    st.session_state['db'] = pd.DataFrame(columns=['Họ tên', 'Đơn vị', 'Dạy học số', 'Kiểm tra', 'Giao tiếp', 'Sáng tạo', 'An toàn', 'Giải quyết vấn đề', 'Trung bình'])

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🌐 DIGITAL SKILLS")
    st.markdown("---")
    menu = st.radio("CHỨC NĂNG", ["📝 Thực hiện đánh giá", "📊 Dashboard tổng hợp", "📂 Quản lý minh chứng"])

# --- MÀN HÌNH 1: THỰC HIỆN ĐÁNH GIÁ ---
if menu == "📝 Thực hiện đánh giá":
    st.title("Phiếu Đánh giá Năng lực số")
    
    with st.form("eval_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Họ và tên giáo viên/nhân viên *")
            unit = st.text_input("Đơn vị công tác *")
        with c2:
            email = st.text_input("Email nhận kết quả")
            files = st.file_uploader("Tải lên minh chứng (PDF/Ảnh)", accept_multiple_files=True)
            
        st.markdown("---")
        st.subheader("Tự đánh giá các miền năng lực (Thang 1.0 - 4.0)")
        
        col_left, col_right = st.columns(2)
        with col_left:
            m1 = st.slider("1. Dạy học số", 1.0, 4.0, 2.5, 0.1)
            m2 = st.slider("2. Kiểm tra đánh giá", 1.0, 4.0, 2.5, 0.1)
            m3 = st.slider("3. Giao tiếp & Cộng tác", 1.0, 4.0, 2.5, 0.1)
        with col_right:
            m4 = st.slider("4. Sáng tạo nội dung số", 1.0, 4.0, 2.5, 0.1)
            m5 = st.slider("5. An toàn số", 1.0, 4.0, 2.5, 0.1)
            m6 = st.slider("6. Giải quyết vấn đề", 1.0, 4.0, 2.5, 0.1)
            
        submit = st.form_submit_button("GỬI KẾT QUẢ & PHÂN TÍCH")

    if submit:
        if name and unit:
            avg = round((m1+m2+m3+m4+m5+m6)/6, 2)
            new_data = [name, unit, m1, m2, m3, m4, m5, m6, avg]
            st.session_state['db'].loc[len(st.session_state['db'])] = new_data
            
            st.success(f"Chúc mừng {name} đã hoàn thành đánh giá!")
            
            # Hiển thị kết quả ngay lập tức
            st.markdown("---")
            res_col1, res_col2 = st.columns([1.5, 1])
            
            with res_col1:
                labels = ['Dạy học số', 'Kiểm tra', 'Giao tiếp', 'Sáng tạo', 'An toàn', 'Giải quyết vấn đề']
                scores = [m1, m2, m3, m4, m5, m6]
                df_plot = pd.DataFrame(dict(r=scores, theta=labels))
                fig = px.line_polar(df_plot, r='r', theta='theta', line_close=True, range_r=[0,4])
                fig.update_traces(fill='toself', fillcolor='rgba(99, 102, 241, 0.3)', line_color='#4f46e5')
                st.plotly_chart(fig)
                
            with res_col2:
                st.markdown(f"""
                <div class="ai-box">
                    <h4>🤖 Phân tích AI</h4>
                    <p><b>Điểm TB: {avg}</b></p>
                    <p>Dựa trên minh chứng, bạn đang ở mức <b>{ "Thành thạo" if avg > 3 else "Khởi động" }</b>.</p>
                    <p><i>Gợi ý: Hãy tập trung thêm vào miền 'Sáng tạo' để tối ưu bài giảng.</i></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Vui lòng nhập đầy đủ Họ tên và Đơn vị!")

# --- MÀN HÌNH 2: DASHBOARD TỔNG HỢP (Dành cho Quản trị/Đồng nghiệp xem chung) ---
elif menu == "📊 Dashboard tổng hợp":
    st.title("Báo cáo Tổng hợp Năng lực số")
    
    if st.session_state['db'].empty:
        st.info("Chưa có dữ liệu đánh giá nào được ghi lại.")
    else:
        # Thống kê nhanh
        df = st.session_state['db']
        c1, c2, c3 = st.columns(3)
        c1.metric("Tổng số lượt", len(df))
        c2.metric("Điểm TB Hệ thống", round(df['Trung bình'].mean(), 2))
        c3.metric("Mức độ cao nhất", df['Trung bình'].max())
        
        st.markdown("### Danh sách chi tiết")
        st.dataframe(df, use_container_width=True)
        
        # Biểu đồ cột so sánh
        st.markdown("### So sánh giữa các cá nhân")
        fig_bar = px.bar(df, x='Họ tên', y='Trung bình', color='Trung bình', text_auto=True)
        st.plotly_chart(fig_bar, use_container_width=True)
