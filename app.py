import streamlit as st
import pandas as pd
import graphviz

st.set_page_config(layout="wide", page_title="DSEDN Circuit Lab")

# --- Сторын төлөв ---
if 'max_current' not in st.session_state:
    st.session_state.max_current = 0.0
if 'history' not in st.session_state:
    st.session_state.history = [45.0]
if 'breaker_on' not in st.session_state:
    st.session_state.breaker_on = True
if 'fuse_blown' not in st.session_state:
    st.session_state.fuse_blown = {"АТП-2": False, "АТП-1": False, "КТП-1": False}

st.title("⚡ 6/0.4кВ-ын Ухаалаг Симуляци (Найдвартай хувилбар)")

# --- Удирдлагын хэсэг ---
with st.sidebar:
    st.header("🕹 Удирдлага")
    if st.button("♻️ Систем Сэргээх"):
        st.session_state.max_current = 0.0
        st.session_state.history = [45.0]
        st.session_state.breaker_on = True
        st.session_state.fuse_blown = {"АТП-2": False, "АТП-1": False, "КТП-1": False}
        st.rerun()

    st.subheader("💥 Гэмтэл үүсгэх")
    target = st.selectbox("Байршил сонго:", ["Сонгох...", "6кВ Шугам", "АТП-2 (0.4кВ)", "АТП-1 (0.4кВ)", "КТП-1 (0.4кВ)"])
    
    if st.button("💥 ГЭМТЭЛ ҮҮСГЭХ") and target != "Сонгох...":
        fault_amp = 15400.5
        st.session_state.max_current = fault_amp
        st.session_state.history.append(fault_amp)
        st.session_state.history.append(0.0) 
        
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
    st.metric("⚠️ БҮРТГЭГДСЭН ИХ ГҮЙДЭЛ", f"{st.session_state.max_current} A")
with col3:
    status_color = "green" if st.session_state.breaker_on else "red"
    st.markdown(f"### Төлөв: :{status_color}[{'🟢 Хэвийн' if st.session_state.breaker_on else '🔴 ТАСАРСАН'}]")

# --- Схем зурах (Graphviz - Хамгийн найдвартай) ---
st.subheader("📊 Системийн нэг шугамын схем")
dot = graphviz.Digraph()
dot.attr(rankdir='LR', size='10,5', bgcolor='#262730')

# Зангилаануудын өнгө тодорхойлох
main_color = 'green' if st.session_state.breaker_on else 'red'

# 6кВ Шин ба Толгойн таслуур
dot.node('Bus', '6кВ ШИН', shape='box', color='white', fontcolor='white')
dot.node('Breaker', 'Толгойн таслуур', shape='diamond', color=main_color, fontcolor='white')
dot.edge('Bus', 'Breaker', color=main_color)

# Шугам №1
dot.node('Line', 'АС-50 Шугам №1', shape='none', fontcolor='white')
dot.edge('Breaker', 'Line', color=main_color)

# Дэд станцууд
for name, kva in [("АТП-2", "100кВА"), ("АТП-1", "160кВА"), ("КТП-1", "630кВА")]:
    is_blown = st.session_state.fuse_blown[name]
    sub_color = 'red' if is_blown or not st.session_state.breaker_on else 'green'
    label = f"{name}\n({kva})\n{'🔥 ШАТСАН' if is_blown else '🟢 OK'}"
    
    dot.node(name, label, shape='component', color=sub_color, fontcolor='white')
    dot.edge('Line', name, color=sub_color, label="Fuse")

st.graphviz_chart(dot)

# --- Гүйдлийн график ---
if len(st.session_state.history) > 1:
    st.subheader("📈 Гүйдлийн бичлэг (Fault Record)")
    st.line_chart(st.session_state.history)
