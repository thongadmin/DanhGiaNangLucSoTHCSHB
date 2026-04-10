import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
from datetime import datetime
from google import genai

# ================= CONFIG =================
st.set_page_config(page_title="AI Digital Competence", layout="wide")

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ Thiếu GOOGLE_API_KEY (vào Settings → Secrets)")
    st.stop()

# Gemini client (SDK mới)
client = genai.Client(api_key=API_KEY)

# ================= CONSTANTS =================
MIEN_LABELS = [
    "Miền 1: Dạy học số", 
    "Miền 2: Kiểm tra đánh giá", 
    "Miền 3: Trao quyền người học", 
    "Miền 4: Kỹ năng công nghệ", 
    "Miền 5: Phát triển chuyên môn", 
    "Miền 6: Trí tuệ nhân tạo (AI)"
]

# ================= FUNCTIONS =================
def analyze_with_ai(name, files):
    file_names = ", ".join([f.name for f in files])

    prompt = f"""
    Bạn là chuyên gia đánh giá năng lực số giáo viên theo khung 6 miền.

    Minh chứng gồm: {file_names}

    Hãy:
    - Chấm điểm từng miền (0 → 4)
    - Nhận xét chi tiết
    - Đưa ra khuyến nghị cải thiện

    TRẢ VỀ JSON DUY NHẤT:
    {{
        "scores": [x1,x2,x3,x4,x5,x6],
        "summary": "Nhận xét chi tiết",
        "recommendations": "Đề xuất cải thiện"
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        # Làm sạch JSON
        text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception as e:
        return {"error": str(e)}


def draw_chart(scores):
    df = pd.DataFrame(dict(r=scores, theta=MIEN_LABELS))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True, range_r=[0,4])
    fig.update_traces(fill='toself')
    return fig

# ================= UI =================
st.title("🧠 AI ĐÁNH GIÁ NĂNG LỰC SỐ GIÁO VIÊN (GENAI SDK)")

menu = st.sidebar.radio("Chọn chức năng", ["Đánh giá", "Báo cáo", "Dashboard"])

# ================= TAB 1 =================
if menu == "Đánh giá":
    st.header("Nhập thông tin")

    name = st.text_input("Họ tên")
    unit = st.text_input("Đơn vị")
    role = st.selectbox("Vai trò", ["Giáo viên","Nhân viên","Quản lý"])

    files = st.file_uploader("Upload minh chứng", accept_multiple_files=True)

    if st.button("🚀 Phân tích bằng AI"):
        if not name or not files:
            st.warning("Thiếu dữ liệu")
        else:
            with st.spinner("AI đang phân tích..."):
                result = analyze_with_ai(name, files)

                if "error" in result:
                    st.error(result["error"])
                else:
                    st.session_state["result"] = {
                        "info": {"name": name, "unit": unit, "role": role},
                        "scores": result["scores"],
                        "summary": result["summary"],
                        "recommendations": result.get("recommendations", ""),
                        "time": str(datetime.now())
                    }
                    st.success("✅ Đánh giá hoàn tất!")

# ================= TAB 2 =================
elif menu == "Báo cáo":
    if "result" not in st.session_state:
        st.info("Chưa có dữ liệu")
    else:
        res = st.session_state["result"]

        st.subheader(f"Báo cáo: {res['info']['name']}")

        col1, col2 = st.columns([2,1])

        with col1:
            st.plotly_chart(draw_chart(res['scores']), use_container_width=True)

        with col2:
            avg = round(sum(res['scores'])/6,2)
            st.metric("Điểm trung bình", avg)
            st.info(res['summary'])
            st.warning(res['recommendations'])

            st.download_button(
                "📄 Xuất báo cáo JSON",
                data=json.dumps(res, ensure_ascii=False, indent=2),
                file_name="report.json"
            )

# ================= TAB 3 =================
elif menu == "Dashboard":
    st.header("Dashboard tổng hợp")

    data = pd.DataFrame([
        {"Tên":"Nguyễn A","Điểm":3.2},
        {"Tên":"Trần B","Điểm":2.5}
    ])

    st.bar_chart(data.set_index("Tên"))
