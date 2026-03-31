import streamlit as st
import time

st.title("⚡ Цахилгаан схемийн интерактив симуляци")

# Тохиргоо
col1, col2 = st.columns(2)
with col1:
    breaker_status = st.toggle("Толгойн таслуур (Main Breaker)", value=True)
    load_level = st.slider("Ачаалал нэмэх (Ампер)", 0, 200, 50)

# Симуляцийн логик
if breaker_status:
    if load_level > 150:
        st.error("⚠️ АНХААР: Ачаалал хэтэрлээ! Таслагч салгавал НУМ үүсэх эрсдэлтэй.")
        if st.button("Одоо таслах"):
            with st.empty():
                for _ in range(5):
                    st.write("💥 НУМ ҮҮСЭЖ БАЙНА (ARCING)...")
                    time.sleep(0.2)
            st.success("Таслагч амжилттай салгагдлаа.")
    
    if st.button("БОГИНО ХОЛБОЛТ ҮҮСГЭХ"):
        st.subheader("🔥 ГЭМТЭЛ!")
        st.write("Гүйдэл: ∞ Ампер")
        time.sleep(0.5)
        st.error("⚡ Реле ажиллалаа: Толгойн таслуур УНАВ!")
        breaker_status = False
else:
    st.info("Систем хүчдэлгүй байна.")

# Схемын визуал дүрслэл (Энгийнээр)
st.markdown(f"""
    <div style="border: 2px solid gray; padding: 20px; text-align: center;">
        <div style="color: {'green' if breaker_status else 'red'}; font-size: 24px;">
            {'● СИСТЕМ АЖИЛЛАЖ БАЙНА' if breaker_status else '○ СИСТЕМ ЗОГССОН'}
        </div>
        <hr>
        Гүйдлийн хэмжээ: {load_level if breaker_status else 0} A
    </div>
""", unsafe_allow_html=True)
