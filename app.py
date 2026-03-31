import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("⚡ 6кВ-ын Түгээх Сүлжээний Симуляци")

# --- Баруун талын удирдлага ---
st.sidebar.header("🕹 Системийн удирдлага")
main_breaker = st.sidebar.toggle("6кВ Толгойн таслуур", value=True)

st.sidebar.subheader("🔌 Дэд станцууд")
ktp1_load = st.sidebar.slider("КТП-1 (630 кВА) ачаалал %", 0, 120, 50)
atp1_load = st.sidebar.slider("АТП-1 (160 кВА) ачаалал %", 0, 120, 30)
atp2_load = st.sidebar.slider("АТП-2 (100 кВА) ачаалал %", 0, 120, 20)

# --- Симуляцийн хэсэг ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Схемийн визуал дүрслэл")
    
    # Энэ хэсэгт схемээ энгийнээр дүрслэв
    status_color = "green" if main_breaker else "red"
    status_text = "ХҮЧДЭЛТЭЙ" if main_breaker else "ХҮЧДЭЛГҮЙ"
    
    st.markdown(f"""
    <div style="border: 3px solid {status_color}; padding: 20px; border-radius: 10px;">
        <h3 style="color: {status_color};">● ТҮГЭЭХ ШИН (6кВ): {status_text}</h3>
        <div style="margin-left: 40px; border-left: 5px dashed {status_color}; padding-left: 20px;">
            <p>⬇️ АБЛү 3x50 (Шугам №1)</p>
            <div style="display: flex; gap: 20px;">
                <div style="background: #f0f2f6; padding: 10px; border: 1px solid gray;">
                    <b>АТП-2 (100 кВА)</b><br>Ачаалал: {atp2_load}%
                </div>
                <div style="background: #f0f2f6; padding: 10px; border: 1px solid gray;">
                    <b>АТП-1 (160 кВА)</b><br>Ачаалал: {atp1_load}%
                </div>
                <div style="background: #f0f2f6; padding: 10px; border: 1px solid gray;">
                    <b>КТП-1 (630 кВА)</b><br>Ачаалал: {ktp1_load}%
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.subheader("📈 Тооцоолол")
    total_load = (atp2_load*1 + atp1_load*1.6 + ktp1_load*6.3) / 10 # Энгийн тооцоо
    st.metric("Нийт ачаалал (кВт)", f"{total_load:.1f}")
    
    if total_load > 80:
        st.error("🚨 АНХААР: Шугамын ачаалал хэтэрч байна!")
