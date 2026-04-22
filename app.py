import streamlit as st
import feedparser
import pandas as pd
import os
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide")
st_autorefresh(interval=600000)

# =========================
# ESTILO
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

st.title("📊 Dashboard Acuerdo Mercosur - UE")

# =========================
# RSS NOTICIAS (CON BRIEF)
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

            resumen = entry.get("summary", "") or entry.get("description", "")
            resumen = resumen.replace("<p>", "").replace("</p>", "")
            resumen = resumen[:200] + "..." if len(resumen) > 200 else resumen

            if "mercosur" in titulo.lower() or "eu" in titulo.lower():
                noticias.append((titulo, resumen, link, fecha))

    return noticias

# =========================
# ANÁLISIS DESDE ARCHIVOS
# =========================
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

# =========================
# DATA
# =========================
noticias = obtener_noticias()
analisis = cargar_analisis()

# =========================
# KPIs
# =========================
k1, k2, k3 = st.columns(3)
k1.metric("Estado", "Negociación")
k2.metric("Noticias", len(noticias))
k3.metric("Análisis", len(analisis))

# =========================
# LAYOUT PRINCIPAL
# =========================
col1, col2, col3 = st.columns([1.3, 1, 1])

# =========================
# 📰 NOVEDADES
# =========================
with col1:
    st.subheader("📰 Novedades")

    for titulo, resumen, link, fecha in noticias[:6]:
        st.markdown(f"""
        <div class="panel">
            <div style="font-weight:600;">{titulo}</div>
            <div style="font-size:12px; color:#9da7b3;">{fecha}</div>
            <div style="margin-top:8px;">{resumen}</div>
            <a href="{link}" target="_blank">Leer más</a>
        </div>
        """, unsafe_allow_html=True)

# =========================
# 🏭 SECTORES
# =========================
with col2:
    st.subheader("🏭 Sectores")

    try:
        # Leer CSV automáticamente (detecta , o ;)
        df = pd.read_csv("sectores.csv", sep=None, engine="python")

        # Limpiar nombres columnas
        df.columns = df.columns.str.strip().str.lower()

        # Validar columnas
        columnas_esperadas = [
            "sector","resumen","oportunidad","arancel_actual",
            "arancel_futuro","cuotas","barreras",
            "oportunidad_uy","riesgo","comentario_estrategico"
        ]

        for col in columnas_esperadas:
            if col not in df.columns:
                st.error(f"Falta columna: {col}")
                st.write("Columnas detectadas:", df.columns)
                st.stop()

        # Render fichas
        for _, row in df.iterrows():

            color_oportunidad = "#3fb950" if row["oportunidad"] == "Alta" else "#d29922"
            color_riesgo = "#f85149" if row["riesgo"] == "Alto" else "#d29922"

            st.markdown(f"""
            <div class="panel">

                <div style="font-size:16px; font-weight:600;">
                    {row['sector']}
                </div>

                <div style="margin-top:6px;">
                    {row['resumen']}
                </div>

                <hr style="border:0.5px solid #30363d;">

                <div style="font-size:13px;">
                    <b>Arancel:</b> {row['arancel_actual']} → {row['arancel_futuro']}<br>
                    <b>Cuotas:</b> {row['cuotas']}<br>
                    <b>Barreras:</b> {row['barreras']}<br>
                    <b>Oportunidad Uruguay:</b> {row['oportunidad_uy']}<br>
                </div>

                <hr style="border:0.5px solid #30363d;">

                <div style="font-size:13px;">
                    <span style="color:{color_oportunidad}; font-weight:bold;">
                        Oportunidad: {row['oportunidad']}
                    </span> |
                    <span style="color:{color_riesgo}; font-weight:bold;">
                        Riesgo: {row['riesgo']}
                    </span>
                </div>

                <div style="margin-top:8px; font-size:13px;">
                    💡 {row['comentario_estrategico']}
                </div>

            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error("Error cargando sectores.csv")
        st.write(e)

# =========================
# 🧠 ANÁLISIS
# =========================
with col3:
    st.subheader("🧠 Análisis")

    if len(analisis) == 0:
        st.info("Cargar archivos en /analisis")

    for titulo, resumen, contenido in analisis[:5]:
        with st.expander(titulo):
            st.write(resumen)
            st.write("---")
            st.write(contenido)

# =========================
# 📂 DOCUMENTOS
# =========================
st.subheader("📂 Documentos")

colA, colB, colC = st.columns(3)

with colA:
    st.markdown("""
    <div class="panel">
    📜 <b>Texto del acuerdo</b><br>
    <a href="#">Ver documento</a>
    </div>
    """, unsafe_allow_html=True)

with colB:
    st.markdown("""
    <div class="panel">
    📊 <b>Anexos</b><br>
    <a href="#">Ver anexos</a>
    </div>
    """, unsafe_allow_html=True)

with colC:
    st.markdown("""
    <div class="panel">
    📅 <b>Cronograma</b><br>
    <a href="#">Ver fechas</a>
    </div>
    """, unsafe_allow_html=True)
