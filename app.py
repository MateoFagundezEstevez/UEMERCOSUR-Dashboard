import streamlit as st
import feedparser
import pandas as pd
import os
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")
st_autorefresh(interval=600000)

# =========================
# ESTILO (LEGIBLE)
# =========================
st.markdown("""
<style>
.block-container {
    background-color: #0e1117;
    color: #e6edf3;
}
.panel {
    border: 1px solid #30363d;
    padding: 14px;
    border-radius: 10px;
    background-color: #161b22;
    margin-bottom: 12px;
}
a { color: #58a6ff; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Mercosur - UE")

# =========================
# RSS
# =========================
RSS_FEEDS = [
    "https://ec.europa.eu/commission/presscorner/api/rss",
    "https://www.ft.com/rss/world"
]

@st.cache_data(ttl=600)
def obtener_noticias():
    noticias = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            titulo = entry.get("title", "")
            link = entry.get("link", "")
            fecha = entry.get("published", "Sin fecha")

            # 👇 CLAVE: summary o description
            resumen = entry.get("summary", "") or entry.get("description", "")

            # limpieza básica
            resumen = resumen.replace("<p>", "").replace("</p>", "")
            resumen = resumen[:200] + "..." if len(resumen) > 200 else resumen

            if "mercosur" in titulo.lower() or "eu" in titulo.lower():
                noticias.append((titulo, resumen, link, fecha))

    return noticias

noticias = obtener_noticias()

# =========================
# LAYOUT
# =========================
col1, col2 = st.columns([2, 1])

# 📰 NOVEDADES CON BRIEF
with col1:
    st.subheader("📰 Novedades")

    for titulo, resumen, link, fecha in noticias[:6]:
        st.markdown(f"""
        <div class="panel">
            <div style="font-weight:600;">{titulo}</div>
            <div style="font-size:13px; color:#9da7b3;">{fecha}</div>
            <div style="margin-top:8px;">{resumen}</div>
            <a href="{link}" target="_blank">Leer más</a>
        </div>
        """, unsafe_allow_html=True)

# 🧠 ANÁLISIS (ARCHIVOS)
def cargar_analisis():
    ruta = "analisis"
    analisis_list = []

    if os.path.exists(ruta):
        for archivo in os.listdir(ruta):
            if archivo.endswith(".txt"):
                with open(os.path.join(ruta, archivo), "r", encoding="utf-8") as f:
                    contenido = f.read()

                titulo = archivo.replace(".txt", "")
                resumen = contenido[:150] + "..."

                analisis_list.append((titulo, resumen, contenido))

    return analisis_list

with col2:
    st.subheader("🧠 Análisis")

    analisis = cargar_analisis()

    for titulo, resumen, contenido in analisis[:5]:
        with st.expander(titulo):
            st.write(resumen)
            st.write("---")
            st.write(contenido)
