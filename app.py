import streamlit as st
import streamlit.components.v1 as components
import time

st.set_page_config(layout="wide")
st.title("⚡ 6кВ-ын Түгээх Сүлжээний Ухаалаг Симуляци")

# --- Тохиргооны хэсэг ---
st.sidebar.header("🕹 Системийн удирдлага")
main_breaker = st.sidebar.toggle("6кВ Толгойн таслуур", value=True)
load_perc = st.sidebar.slider("Хэвийн ачаалал (%)", 0, 120, 60)

# Гэмтэл үүсгэх товчлуур
st.sidebar.subheader("💥 Гэмтлийн симуляци")
fault_type = st.sidebar.selectbox("Гэмтлийн төрөл", ["Байхгүй", "КТП-1 дээр 3 фазын БХ"])
fault_button = st.sidebar.button("💥 ГЭМТЭЛ ҮҮСГЭХ", disabled=fault_type == "Байхгүй")

# --- Симуляцийн логик ---
# Системийн өгөгдөл
U_nom = 6000 # В
Z_sys = 0.5 # Ом (Системийн хялбарчилсан эсэргүүцэл)
I_load_max = 50 # А (Хэвийн үеийн хамгийн их гүйдэл)

# Гүйдлийн тооцоо
current_current = I_load_max * (load_perc / 100) if main_breaker else 0
is_fault = False
status_text = "🟢 Хэвийн горим"

# Гэмтэл үүссэн үеийн тооцоо
if fault_button and main_breaker:
    is_fault = True
    current_current = U_nom / Z_sys # Огцом өссөн гүйдэл (I = U/Z)
    status_text = "💥 БОГИНО ХОЛБОЛТ ҮҮСЛЭЭ!"

# РХА-ийн ажиллагаа
relay_tripped = False
if current_current > 150: # Хэт гүйдлийн хамгаалалтын заалт
    relay_tripped = True
    status_text = "🚨 РХА АЖИЛЛАВ! Таслуур тасарлаа."
    current_current = 0 # Тасарсан тул гүйдэл 0 болно.
    main_breaker = False # Таслуур унана.

# Мэдээллийн хэсэг
col_m1, col_m2 = st.columns(2)
col_m1.metric("Гүйдлийн хэмжээ (А)", f"{current_current:.1f}")
col_m2.subheader(f"Системийн төлөв: {status_text}")

# --- HTML Canvas & JavaScript Хөдөлгөөнт схем ---
# Энэ хэсэгт чиний зурсан бүх бичиглэлийг нэмсэн.
canvas_html = f"""
<canvas id="circuitCanvas" width="800" height="600" style="border:1px solid #d3d3d3; background: #262730;"></canvas>

<script>
const canvas = document.getElementById('circuitCanvas');
const ctx = canvas.getContext('2d');
let offset = 0;

function draw() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Өнгө ба төлөв тохируулах
    const mainColor = {'"#00FF00"' if main_breaker else '"#555"'};
    const faultColor = {'"#FF0000"' if is_fault else '"#FFF"'};
    const speed = {'"10"' if is_fault else '"2"'};
    
    // --- 1. Түгээх шин (6кВ) ---
    ctx.fillStyle = "white";
    ctx.font = "bold 20px Arial";
    ctx.fillText("6кВ", 700, 40);
    ctx.fillRect(50, 50, 700, 10); // Шин
    
    // --- 2. Үндсэн таслуур ба шугам №1 ---
    ctx.fillStyle = "white";
    ctx.font = "16px Arial";
    ctx.fillText("АБЛү 3x50 (Шугам №1)", 150, 90);
    ctx.fillText("АС 50", 150, 110);
    
    // Таслуур зурах (дөрвөлжин)
    ctx.strokeStyle = "white";
    ctx.lineWidth = 2;
    ctx.strokeRect(50, 70, 30, 30);
    if ({'true' if main_breaker else 'false'}) ctx.fillRect(55, 75, 20, 20); // Залгаатай

    // --- 3. Салбар шугамууд ба дэд станцууд (КТП) ---
    const paths = [
        [[100, 100], [100, 400], "АС 50 (4.1км)", "100кВА АТП-2 (0.4кВ)"], // АТП-2 салбар
        [[300, 100], [300, 350], "АС 50 (3км)", "160кВА АТП-1 (0.4кВ)"],  // АТП-1 салбар
        [[550, 100], [550, 300], "АС 50 (10км)", "630кВА КТП-1 (0.4кВ)"]   // КТП-1 салбар (Гэмтэл үүсэх газар)
    ];

    paths.forEach(path => {{
        // Үндсэн шугам
        ctx.beginPath();
        ctx.strokeStyle = '#777';
        ctx.lineWidth = 3;
        ctx.moveTo(path[0][0], path[0][1]);
        ctx.lineTo(path[1][0], path[1][1]);
        ctx.stroke();

        // Шугамын бичиглэл
        ctx.fillStyle = "white";
        ctx.font = "14px Arial";
        ctx.fillText(path[2], path[0][0] + 10, (path[0][1] + path[1][1]) / 2);

        // Дэд станц зурах (дөрвөлжин)
        ctx.strokeStyle = "white";
        ctx.lineWidth = 2;
        ctx.strokeRect(path[1][0] - 25, path[1][1], 50, 40);
        ctx.fillText(path[3], path[1][0] - 80, path[1][1] + 60);

        // Хөдөлгөөнт гүйдэл зурах (Таслуур залгаатай бол)
        if ({'true' if main_breaker else 'false'}) {{
            ctx.beginPath();
            ctx.setLineDash([15, 15]);
            ctx.lineDashOffset = -offset;
            ctx.strokeStyle = mainColor; // Ногоон (хэвийн) эсвэл улаан (БХ)
            ctx.lineWidth = 3;
            ctx.moveTo(path[0][0], path[0][1]);
            ctx.lineTo(path[1][0], path[1][1]);
            ctx.stroke();
            ctx.setLineDash([]);
        }}
    }});
    
    // --- 4. Гэмтлийн визуал үзүүлэлт ---
    if ({'true' if is_fault else 'false'}) {{
        ctx.beginPath();
        ctx.fillStyle = "rgba(255, 0, 0, 0.5)"; // Улаан туяа
        ctx.arc(550, 300, 50, 0, 2 * Math.PI);
        ctx.fill();
        ctx.fillStyle = "white";
        ctx.fillText("💥 БОГИНО ХОЛБОЛТ!", 570, 280);
    }}

    offset += speed;
    requestAnimationFrame(draw);
}}
draw();
</script>
"""

# Canvas-ийг Streamlit рүү оруулах
components.html(canvas_html, height=650)

# Гэмтэл үүссэн үед РХА ажиллах хүртэлх хугацааг ( delay) симуляци хийх
if is_fault:
    time.sleep(1) # 1 секундын дараа тасарна.
    st.experimental_rerun() # Хуудсыг дахин ачаалж төлөвийг шинэчлэх
