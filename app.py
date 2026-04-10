import streamlit as st
import pandas as pd
import plotly.express as px

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ thống Đánh giá Năng lực số", layout="wide")

# --- CUSTOM CSS ĐỂ SAO CHÉP GIAO DIỆN HTML ---
st.markdown("""
<style>
    /* Nền tảng và Sidebar */
    .stApp { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #1a1e36 !important; color: white; }
    
    /* Tùy chỉnh các thẻ Card */
    .custom-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #edf2f7;
    }
    .card-label { color: #64748b; font-size: 14px; font-weight: 500; margin-bottom: 10px; }
    .card-value { color: #1e293b; font-size: 32px; font-weight: 700; margin: 0; }
    .card-sub { color: #10b981; font-size: 13px; margin-top: 5px; }
    .level-tag { color: #6366f1; font-style: italic; font-weight: bold; font-size: 24px; text-transform: uppercase; }
    
    /* Hộp phân tích AI */
    .ai-box {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
    }
    
    /* Sidebar Navigation */
    .stRadio [role="radiogroup"] { color: white; }
    div[data-testid="stSidebarNav"] { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:white;'>DIGITAL SKILLS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8;'>ASSESSMENT</p>", unsafe_allow_html=True)
    st.write("---")
    menu = st.radio("ĐIỀU HƯỚNG", ["Kết quả tổng quan", "Thực hiện đánh giá", "Quản trị dữ liệu"])
    st.markdown("<br><br><br><br><br><div style='font-size:12px; color:#94a3b8;'>PHIÊN BẢN 1.5<br>Khung năng lực UNESCO</div>", unsafe_allow_html=True)

# --- DỮ LIỆU ---
labels = ['Dạy học số', 'Kiểm tra', 'Giao tiếp', 'Sáng tạo', 'An toàn', 'Giải quyết vấn đề']
scores = [3.5, 3.2, 3.0, 3.8, 2.8, 2.5]

# --- HIỂN THỊ ---
if menu == "Kết quả tổng quan":
    # Header
    c_header1, c_header2 = st.columns([3, 1])
    with c_header1:
        st.title("BÁO CÁO NĂNG LỰC CÁ NHÂN")
    with c_header2:
        st.markdown("""<div style='text-align:right; margin-top:20px;'>
            <b>GV. Nguyễn Văn A</b><br><small style='color:gray;'>TRƯỜNG THPT CHUYÊN</small>
        </div>""", unsafe_allow_html=True)

    # Row 1: Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="custom-card"><p class="card-label">Điểm trung bình</p><p class="card-value">3.2 / 4.0</p><p class="card-sub">▲ Tăng 12% so với kỳ trước</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="custom-card"><p class="card-label">Xếp loại năng lực</p><p class="level-tag">THÀNH THẠO</p><p style="color:gray; font-size:12px;">Mức 3: Advanced User</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="custom-card"><p class="card-label">Minh chứng đã nộp</p><p class="card-value">12 <span style="font-size:16px; font-weight:normal;">File</span></p><p style="font-size:13px;"><a href="#">Xem chi tiết hồ sơ</a></p></div>', unsafe_allow_html=True)

    # Row 2: Biểu đồ & AI
    c1, c2 = st.columns([1.8, 1.2])
    with c1:
        st.markdown('<div class="custom-card"><h5>Mô hình 6 Miền Năng lực</h5>', unsafe_allow_html=True)
        df = pd.DataFrame(dict(r=scores, theta=labels))
        fig = px.line_polar(df, r='r', theta='theta', line_close=True, range_r=[0,4])
        fig.update_traces(fill='toself', line_color='#6366f1', fillcolor='rgba(99, 102, 241, 0.3)')
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown("""<div class="ai-box">
            <h5 style='display:flex; align-items:center;'>🤖 Phân tích từ AI</h5>
            <p style='font-style:italic; font-size:14px; line-height:1.6; opacity:0.9;'>
            "Bạn thể hiện thế mạnh vượt trội trong việc <b>Dạy học số</b> và <b>Kiểm tra đánh giá</b>. 
            Tuy nhiên, khả năng <b>Giải quyết vấn đề công nghệ</b> cần được cải thiện bằng cách tham gia 
            thêm các khóa đào tạo về quản trị hệ thống."
            </p>
        </div>""", unsafe_allow_html=True)
        
        st.write("")
        st.markdown('<div class="custom-card"><h6>Chi tiết điểm từng miền</h6>', unsafe_allow_html=True)
        for l, s in zip(labels, scores):
            st.caption(f"{l}: {s}/4.0")
            st.progress(s/4.0)
        st.markdown('</div>', unsafe_allow_html=True)
