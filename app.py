import streamlit as st
import streamlit.components.v1 as components
import time

st.set_page_config(layout="wide", page_title="DSEDN Circuit Simulator")
st.title("⚡ 6кВ-ын Түгээх Сүлжээний Интерактив Симуляци")

# --- Сторын төлөв (State Management) ---
if 'breaker_on' not in st.session_state:
    st.session_state.breaker_on = True
if 'fault_location' not in st.session_state:
    st.session_state.fault_location = "Байхгүй"

# --- Удирдлагын хэсэг ---
st.sidebar.header("🕹 Системийн удирдлага")
if st.sidebar.button("♻️ Систем дахин ачаалах"):
    st.session_state.breaker_on = True
    st.session_state.fault_location = "Байхгүй"
    st.rerun()

st.sidebar.subheader("🔌 Таслуурын төлөв")
st.session_state.breaker_on = st.sidebar.toggle("Толгойн таслуур (6кВ)", value=st.session_state.breaker_on)

st.sidebar.subheader("💥 Гэмтэл үүсгэх цэг")
target = st.sidebar.selectbox("Гэмтэл үүсгэх дэд станц сонго:", ["Байхгүй", "АТП-2 (100кВА)", "АТП-1 (160кВА)", "КТП-1 (630кВА)"])

if st.sidebar.button("💥 ГЭМТЭЛ ҮҮСГЭХ") and target != "Байхгүй":
    st.session_state.fault_location = target
    st.rerun()

# --- Физик тооцоолол ---
U_nom = 6000  # 6кВ
Z_sys = 0.4   # Системийн эсэргүүцэл
current_A = 0
status = "🟢 Хэвийн ажиллагаа"

if st.session_state.breaker_on:
    if st.session_state.fault_location == "Байхгүй":
        current_A = 45.5 # Хэвийн ачааллын дундаж гүйдэл
    else:
        current_A = U_nom / Z_sys # Богино холболтын гүйдэл I = U/Z
        status = f"🔥 {st.session_state.fault_location} дээр БОГИНО ХОЛБОЛТ!"
        
        # РХА-ийн ажиллагаа (Хэт гүйдлийн хамгаалалт)
        if current_A > 500:
            st.toast(f"🚨 РХА Ажиллалаа! I={current_A:.0f}A", icon="⚠️")
            time.sleep(1) # Хамгаалалтын хугацааны барилт
            st.session_state.breaker_on = False
            st.session_state.fault_location = "Байхгүй"
            status = "🚨 РХА ТАСЛАВ (Overcurrent Trip)"
            st.rerun()

# Мэдээллийн самбар
c1, c2 = st.columns(2)
c1.metric("Шугамын гүйдэл (А)", f"{current_A:.1f} A", delta=None if current_A < 500 else "АЮУЛТАЙ", delta_color="inverse")
c2.info(f"Төлөв: {status}")

# --- HTML5 Canvas Animation ---
canvas_code = f"""
<canvas id="simCanvas" width="900" height="550" style="background:#1e1e1e; border-radius:10px;"></canvas>
<script>
const canvas = document.getElementById('simCanvas');
const ctx = canvas.getContext('2d');
let dashOffset = 0;

function draw() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const isOn = {'true' if st.session_state.breaker_on else 'false'};
    const faultLoc = "{st.session_state.fault_location}";
    
    // 1. 6кВ Шин зурах
    ctx.strokeStyle = "#888"; ctx.lineWidth = 8;
    ctx.beginPath(); ctx.moveTo(50, 50); ctx.lineTo(850, 50); ctx.stroke();
    ctx.fillStyle = "white"; ctx.font = "bold 18px Courier"; ctx.fillText("6кВ ШИН", 750, 40);

    // 2. Толгойн таслуур
    ctx.strokeStyle = "white"; ctx.strokeRect(50, 70, 40, 40);
    if(isOn) {{ ctx.fillStyle = "#00ff00"; ctx.fillRect(55, 75, 30, 30); }}
    ctx.fillStyle = "white"; ctx.fillText("Шугам №1", 100, 95);

    // 3. Тэнхлэг шугам (АС-50)
    ctx.beginPath(); ctx.moveTo(70, 110); ctx.lineTo(70, 200); ctx.lineTo(600, 200); ctx.stroke();
    
    // Дэд станцуудын координат ба өгөгдөл
    const subs = [
        {{ name: "АТП-2", kva: "100кВА", x: 200, y: 200, toY: 400, label: "АС-50 (4.1км)" }},
        {{ name: "АТП-1", kva: "160кВА", x: 400, y: 200, toY: 350, label: "АС-50 (3км)" }},
        {{ name: "КТП-1", kva: "630кВА", x: 600, y: 200, toY: 300, label: "АС-50 (10км)" }}
    ];

    subs.forEach(s => {{
        // Салбар шугам
        ctx.beginPath(); ctx.moveTo(s.x, s.y); ctx.lineTo(s.x, s.toY); ctx.stroke();
        ctx.fillStyle = "#aaa"; ctx.font = "12px Arial"; ctx.fillText(s.label, s.x + 10, (s.y+s.toY)/2);

        // Трансформатор (Дүрслэл)
        ctx.strokeStyle = "white"; ctx.strokeRect(s.x - 30, s.toY, 60, 40);
        ctx.fillStyle = "white"; ctx.fillText(s.name, s.x - 25, s.toY + 25);
        ctx.font = "10px Arial"; ctx.fillText(s.kva, s.x - 25, s.toY + 55);

        // Хөдөлгөөнт гүйдэл
        if(isOn) {{
            ctx.beginPath();
            ctx.setLineDash([10, 15]);
            ctx.lineDashOffset = -dashOffset;
            ctx.strokeStyle = (faultLoc.includes(s.name)) ? "#ff0000" : "#00ff00";
            ctx.lineWidth = 3;
            ctx.moveTo(s.x, s.y); ctx.lineTo(s.x, s.toY); ctx.stroke();
            ctx.setLineDash([]);
        }}

        // Гэмтлийн эффект (Arc/Spark)
        if(faultLoc.includes(s.name)) {{
            ctx.beginPath();
            ctx.fillStyle = "yellow";
            for(let i=0; i<8; i++) {{
                let angle = i * Math.PI / 4;
                ctx.lineTo(s.x + Math.cos(angle)*40, s.toY + Math.sin(angle)*40);
            }}
            ctx.fill();
        }}
    }});

    // Үндсэн шугамын гүйдэл
    if(isOn) {{
        ctx.beginPath(); ctx.setLineDash([10, 15]); ctx.lineDashOffset = -dashOffset;
        ctx.strokeStyle = (faultLoc !== "Байхгүй") ? "#ff0000" : "#00ff00";
        ctx.moveTo(70, 110); ctx.lineTo(70, 200); ctx.lineTo(600, 200); ctx.stroke();
        ctx.setLineDash([]);
    }}

    dashOffset += (faultLoc !== "Байхгүй") ? 15 : 2;
    requestAnimationFrame(draw);
}}
draw();
</script>
"""
components.html(canvas_code, height=600)
