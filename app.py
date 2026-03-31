import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(layout="wide", page_title="DSEDN Circuit Lab")

# --- Сторын төлөв ---
if 'max_current' not in st.session_state:
    st.session_state.max_current = 0.0
if 'history' not in st.session_state:
    st.session_state.history = [{"Гүйдэл": 45}]
if 'breaker_on' not in st.session_state:
    st.session_state.breaker_on = True
if 'fuse_blown' not in st.session_state:
    st.session_state.fuse_blown = {"АТП-2": False, "АТП-1": False, "КТП-1": False}

st.title("⚡ 6/0.4кВ-ын Ухаалаг Симуляци")

# --- Удирдлагын хэсэг ---
with st.sidebar:
    st.header("🕹 Удирдлага")
    if st.button("♻️ Систем Сэргээх"):
        st.session_state.max_current = 0.0
        st.session_state.history = [{"Гүйдэл": 45}]
        st.session_state.breaker_on = True
        st.session_state.fuse_blown = {"АТП-2": False, "АТП-1": False, "КТП-1": False}
        st.rerun()

    st.subheader("💥 Гэмтэл үүсгэх")
    target = st.selectbox("Байршил сонго:", ["Сонгох...", "6кВ Шугам", "АТП-2 (0.4кВ)", "АТП-1 (0.4кВ)", "КТП-1 (0.4кВ)"])
    
    if st.button("💥 ГЭМТЭЛ ҮҮСГЭХ") and target != "Сонгох...":
        # Гэмтлийн тооцоо
        fault_amp = 15400.5 # 15.4 кА гэмтлийн гүйдэл
        st.session_state.max_current = fault_amp
        st.session_state.history.append({"Гүйдэл": fault_amp})
        st.session_state.history.append({"Гүйдэл": 0}) # Тасарсны дараа 0 болно
        
        if target == "6кВ Шугам":
            st.session_state.breaker_on = False
        else:
            sub_name = target.split(" ")[0]
            st.session_state.fuse_blown[sub_name] = True
        st.rerun()

# --- Мэдээллийн хэсэг ---
col1, col2, col3 = st.columns(3)
with col1:
    curr = 45.0 if st.session_state.breaker_on else 0.0
    st.metric("Одоогийн гүйдэл", f"{curr} A")
with col2:
    st.metric("⚠️ БҮРТГЭГДСЭН ИХ ГҮЙДЭЛ", f"{st.session_state.max_current} A", delta_color="inverse")
with col3:
    st.subheader(f"Төлөв: {'🟢 Хэвийн' if st.session_state.breaker_on else '🔴 ТАСАРСАН'}")

# --- Схем зурах (Canvas) ---
# Схем харагдахгүй байх эрсдэлээс сэргийлж style-ийг тодорхой өгөв
canvas_html = f"""
<div id="wrapper" style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; width: 850px;">
    <canvas id="simCanvas" width="800" height="450"></canvas>
</div>

<script>
    const canvas = document.getElementById('simCanvas');
    const ctx = canvas.getContext('2d');
    let offset = 0;

    function draw() {{
        ctx.clearRect(0, 0, 800, 450);
        const isOn = {'true' if st.session_state.breaker_on else 'false'};
        const fuses = {st.session_state.fuse_blown};

        // 1. 6кВ Шин
        ctx.strokeStyle = "#888"; ctx.lineWidth = 6;
        ctx.beginPath(); ctx.moveTo(50, 40); ctx.lineTo(750, 40); ctx.stroke();
        ctx.fillStyle = "white"; ctx.font = "bold 16px Arial"; ctx.fillText("6кВ ШИН", 680, 30);

        // 2. Үндсэн шугам (АС-50) - Чиний зураг шиг
        ctx.strokeStyle = "#555"; ctx.lineWidth = 3;
        ctx.beginPath(); ctx.moveTo(70, 40); ctx.lineTo(70, 150); ctx.lineTo(600, 150); ctx.stroke();

        const subs = [
            {{ name: "АТП-2", kva: "100кВА", x: 200, y: 150, toY: 350 }},
            {{ name: "АТП-1", kva: "160кВА", x: 400, y: 150, toY: 300 }},
            {{ name: "КТП-1", kva: "630кВА", x: 600, y: 150, toY: 250 }}
        ];

        subs.forEach(s => {{
            // Салбар шугам
            ctx.beginPath(); ctx.strokeStyle = "#555";
            ctx.moveTo(s.x, s.y); ctx.lineTo(s.x, s.toY); ctx.stroke();

            // Трансформатор
            ctx.strokeStyle = "white"; ctx.lineWidth = 2;
            ctx.strokeRect(s.x-30, s.toY, 60, 40);
            ctx.fillStyle = "white"; ctx.font = "12px Arial";
            ctx.fillText(s.name, s.x-20, s.toY+20);
            ctx.fillText(s.kva, s.x-20, s.toY+55);

            // Гүйдлийн хөдөлгөөн
            if(isOn && !fuses[s.name]) {{
                ctx.beginPath(); ctx.setLineDash([8, 12]);
                ctx.lineDashOffset = -offset;
                ctx.strokeStyle = "#00ff00";
                ctx.moveTo(s.x, s.y); ctx.lineTo(s.x, s.toY); ctx.stroke();
                ctx.setLineDash([]);
            }}

            if(fuses[s.name]) {{
                ctx.fillStyle = "red"; ctx.fillText("🔥 FUSE BLOWN", s.x-40, s.toY-10);
            }}
        }});

        // Үндсэн шугамын хөдөлгөөн
        if(isOn) {{
            ctx.beginPath(); ctx.setLineDash([8, 12]); ctx.lineDashOffset = -offset;
            ctx.strokeStyle = "#00ff00";
            ctx.moveTo(70, 40); ctx.lineTo(70, 150); ctx.lineTo(600, 150); ctx.stroke();
            ctx.setLineDash([]);
        }}

        offset += 2;
        requestAnimationFrame(draw);
    }}
    draw();
</script>
"""

# Canvas-ийг харуулах
components.html(canvas_html, height=500, width=900)

# Гүйдлийн график
if len(st.session_state.history) > 1:
    st.subheader("📈 Гүйдлийн цохилтын бичлэг (Fault Record)")
    df = pd.DataFrame(st.session_state.history)
    st.area_chart(df)
