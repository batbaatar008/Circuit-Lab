import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="DSEDN Protection Lab")
st.title("⚡ РХА-ийн Гэмтэл Бүртгэгч ба Симуляци")

# --- Сторын төлөв (State) ---
if 'max_current' not in st.session_state:
    st.session_state.max_current = 0.0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'breaker_on' not in st.session_state:
    st.session_state.breaker_on = True
if 'fuse_blown' not in st.session_state:
    st.session_state.fuse_blown = {"АТП-2": False, "АТП-1": False, "КТП-1": False}

# --- Удирдлагын хэсэг ---
st.sidebar.header("🕹 Систем")
if st.sidebar.button("♻️ Түүх арилгах & Сэргээх"):
    st.session_state.max_current = 0.0
    st.session_state.history = []
    st.session_state.breaker_on = True
    st.session_state.fuse_blown = {"АТП-2": False, "АТП-1": False, "КТП-1": False}
    st.rerun()

target = st.sidebar.selectbox("🎯 Гэмтэл үүсгэх цэг:", 
                             ["Сонгох...", "6кВ Шугам", "АТП-2 (0.4кВ)", "АТП-1 (0.4кВ)", "КТП-1 (0.4кВ)"])

# --- Логик ба Тооцоолол ---
U_nom = 6000
Z_sys = 0.35 # Гэмтлийн гүйдлийг их байлгахын тулд багасгав
current_A = 45.0 if st.session_state.breaker_on else 0.0
is_fault = False

if st.sidebar.button("💥 ГЭМТЭЛ ҮҮСГЭХ") and target != "Сонгох...":
    is_fault = True
    current_A = U_nom / Z_sys # Гэмтлийн үеийн асар их гүйдэл
    
    # Хамгийн их гүйдлийг хадгалах (Peak Hold)
    if current_A > st.session_state.max_current:
        st.session_state.max_current = current_A
    
    # Түүхэнд бичих
    st.session_state.history.append(current_A)
    
    # Хамгаалалтын ажиллагаа
    if target == "6кВ Шугам":
        st.session_state.breaker_on = False
    else:
        sub_name = target.split(" ")[0]
        st.session_state.fuse_blown[sub_name] = True
    
    st.rerun()

# --- Мэдээллийн самбар ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Одоогийн гүйдэл", f"{current_A:.1f} A")

with col2:
    # Хамгийн их гүйдлийг улаанаар тодруулж харуулна
    st.metric("⚠️ БҮРТГЭГДСЭН ИХ ГҮЙДЭЛ", f"{st.session_state.max_current:.1f} A", 
              delta=f"{st.session_state.max_current - 45:.1f} A хэтрэлт", delta_color="inverse")

with col3:
    status = "🟢 Хэвийн" if st.session_state.breaker_on else "🔴 ТАСАРСАН"
    st.subheader(f"Төлөв: {status}")

# --- Гүйдлийн график (Осциллограмм шиг) ---
if st.session_state.history:
    st.subheader("📈 Гүйдлийн өөрчлөлтийн график (Fault Record)")
    chart_data = pd.DataFrame(st.session_state.history, columns=["Ампер (А)"])
    st.line_chart(chart_data)

# --- Canvas Animation ---
canvas_code = f"""
<canvas id="simCanvas" width="900" height="400" style="background:#1e1e1e; border-radius:10px;"></canvas>
<script>
const canvas = document.getElementById('simCanvas');
const ctx = canvas.getContext('2d');
let dashOffset = 0;

function draw() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const isOn = {'true' if st.session_state.breaker_on else 'false'};
    const fuses = {st.session_state.fuse_blown};

    // Шугамууд зурах
    ctx.strokeStyle = "#555"; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.moveTo(50, 50); ctx.lineTo(850, 50); ctx.stroke(); // Шин
    ctx.beginPath(); ctx.moveTo(70, 50); ctx.lineTo(70, 150); ctx.lineTo(600, 150); ctx.stroke(); // Үндсэн шугам

    const subs = [
        {{ name: "АТП-2", x: 200, y: 150, toY: 300 }},
        {{ name: "АТП-1", x: 400, y: 150, toY: 300 }},
        {{ name: "КТП-1", x: 600, y: 150, toY: 300 }}
    ];

    subs.forEach(s => {{
        ctx.beginPath(); ctx.moveTo(s.x, s.y); ctx.lineTo(s.x, s.toY); ctx.stroke();
        ctx.strokeStyle = "white"; ctx.strokeRect(s.x-25, s.toY, 50, 30);
        ctx.fillStyle = "white"; ctx.fillText(s.name, s.x-20, s.toY+20);

        if(isOn && !fuses[s.name]) {{
            ctx.beginPath(); ctx.setLineDash([10, 15]); ctx.lineDashOffset = -dashOffset;
            ctx.strokeStyle = "#00ff00"; ctx.stroke();
            ctx.moveTo(s.x, s.y); ctx.lineTo(s.x, s.toY); ctx.stroke();
            ctx.setLineDash([]);
        }}
        if(fuses[s.name]) {{
            ctx.fillStyle = "red"; ctx.fillText("🔥 FUSE BLOWN", s.x-35, s.toY-10);
        }}
    }});

    dashOffset += 2;
    requestAnimationFrame(draw);
}}
draw();
</script>
"""
components.html(canvas_code, height=420)
