import streamlit as st
import streamlit.components.v1 as components

st.title("⚡ Интерактив Хөдөлгөөнт Схем")

# Таслуурын төлөвийг сонгох
power_on = st.toggle("Хүчдэл залгах", value=True)
speed = st.slider("Гүйдлийн хурд", 1, 10, 3)

# HTML & JavaScript Canvas код
canvas_html = f"""
<canvas id="circuitCanvas" width="600" height="400" style="border:1px solid #d3d3d3; background: #262730;"></canvas>

<script>
const canvas = document.getElementById('circuitCanvas');
const ctx = canvas.getContext('2d');
let offset = 0;

function draw() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Шугамын замууд (Чиний зурсан схемтэй төстэй)
    const paths = [
        [[50, 50], [500, 50]],   // Үндсэн 6кВ шугам
        [[150, 50], [150, 150]], // АТП-2 салбар
        [[300, 50], [300, 150]], // АТП-1 салбар
        [[450, 50], [450, 150]]  // КТП-1 салбар
    ];

    paths.forEach(path => {{
        // 1. Үндсэн хар шугам зурах
        ctx.beginPath();
        ctx.strokeStyle = '#555';
        ctx.lineWidth = 4;
        ctx.moveTo(path[0][0], path[0][1]);
        ctx.lineTo(path[1][0], path[1][1]);
        ctx.stroke();

        // 2. Хөдөлгөөнт "Цэгүүд" (Гүйдэл) зурах
        if ({'true' if power_on else 'false'}) {{
            ctx.beginPath();
            ctx.setLineDash([10, 15]); // Цэг хоорондын зай
            ctx.lineDashOffset = -offset;
            ctx.strokeStyle = '#00FF00'; // Ногоон гэрэлтсэн өнгө
            ctx.lineWidth = 4;
            ctx.moveTo(path[0][0], path[0][1]);
            ctx.lineTo(path[1][0], path[1][1]);
            ctx.stroke();
            ctx.setLineDash([]); // Буцааж хэвийн болгох
        }}
    }});

    // Дэд станцуудыг зурах (Дөрвөлжин)
    ctx.fillStyle = "white";
    ctx.fillRect(120, 150, 60, 40); ctx.fillText("АТП-2", 130, 210);
    ctx.fillRect(270, 150, 60, 40); ctx.fillText("АТП-1", 280, 210);
    ctx.fillRect(420, 150, 60, 40); ctx.fillText("КТП-1", 430, 210);

    offset += {speed};
    requestAnimationFrame(draw);
}}
draw();
</script>
"""

# Canvas-ийг Streamlit рүү оруулах
components.html(canvas_html, height=450)
