import streamlit as st
import feedparser
import pandas as pd
import os
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(layout="wide")
st_autorefresh(interval=600000)  # 10 min

# =========================
# ESTILO (LEGIBLE + OSCURO)
# =========================
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.block-container {
    background-color: #0e1117;
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}
h1 { color: #ffffff; }
h2, h3 { color: #c9d1d9; }

.panel {
    border: 1px solid #30363d;
    padding: 14px;
    border-radius: 10px;
    background-color: #161b22;
    margin-bottom: 12px;
}

.badge-green { color: #3fb950; font-weight: bold; }
.badge-yellow { color: #d29922; font-weight: bold; }
.badge-red { color: #f85149; font-weight: bold; }

a { color: #58a6ff; text-decoration: none; }
a:hover { text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

# =========================
# TÍTULO
# =========================
st.title("📊 Dashboard Acuerdo Mercosur - UE")

# =========================
# RSS NOTICIAS
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
            titulo = entry.title
            link = entry.link
            fecha = entry.get("published", "Sin fecha")

            if "mercosur" in titulo.lower() or "eu" in titulo.lower():
                noticias.append((titulo, link, fecha))
    return noticias

def resumen_simple(texto):
    return texto[:120] + "..."

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
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Estado", "Negociación")
kpi2.metric("Noticias", len(noticias))
kpi3.metric("Análisis", len(analisis))

# =========================
# LAYOUT PRINCIPAL
# =========================
col1, col2, col3 = st.columns([1.3, 1, 1])

# =========================
# 📰 NOVEDADES
# =========================
with col1:
    st.subheader("📰 Novedades")

    for titulo, link, fecha in noticias[:5]:
        st.markdown(f"""
        <div class="panel">
            <div style="font-size:16px; font-weight:600;">{titulo}</div>
            <div style="font-size:12px; color:#8b949e;">{fecha}</div>
            <a href="{link}" target="_blank">Leer más</a>
        </div>
        """, unsafe_allow_html=True)

# =========================
# 🏭 SECTORES (CSV)
# =========================
with col2:
    st.subheader("🏭 Sectores")

    try:
        df = pd.read_csv("sectores.csv")

        for _, row in df.iterrows():
            color = "badge-green" if row["oportunidad"] == "Alta" else "badge-yellow"

            st.markdown(f"""
            <div class="panel">
                <div style="font-weight:600;">{row['sector']}</div>
                <div style="font-size:14px;">{row['resumen']}</div>
                <div class="{color}">Nivel: {row['oportunidad']}</div>
            </div>
            """, unsafe_allow_html=True)

    except:
        st.info("Cargar archivo sectores.csv")

# =========================
# 🧠 ANÁLISIS (DESDE CARPETA)
# =========================
with col3:
    st.subheader("🧠 Análisis")

    if len(analisis) == 0:
        st.info("Cargar archivos en carpeta /analisis")

    for titulo, resumen, contenido in analisis[:5]:
        with st.expander(titulo):
            st.write(resumen)
            st.write("---")
            st.write(contenido)

# =========================
# 📂 DOCUMENTOS
# =========================
st.subheader("📂 Documentos del acuerdo")

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
