import streamlit as st
import feedparser
import pandas as pd
import os
from io import StringIO
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide")
st_autorefresh(interval=600000)

# =========================
# ESTILO GLOBAL
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
# UTILIDAD
# =========================
def limpiar_texto(texto):
    if pd.isna(texto):
        return ""
    return str(texto).replace("\\n", "\n")

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
# ANÁLISIS
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
# CSV SECTORES
# =========================
@st.cache_data
def cargar_sectores():
    ruta = "sectores.csv"

    if not os.path.exists(ruta):
        st.error("No se encontró sectores.csv")
        return pd.DataFrame()

    with open(ruta, "r", encoding="utf-8") as f:
        contenido = f.read()

    contenido = contenido.replace("\ufeff", "")

    df = pd.read_csv(StringIO(contenido))
    df.columns = df.columns.str.strip().str.lower()

    return df

# =========================
# DATA
# =========================
noticias = obtener_noticias()
analisis = cargar_analisis()
df = cargar_sectores()

if df.empty:
    st.warning("CSV vacío o no cargado correctamente")
    st.stop()

# =========================
# KPIs
# =========================
k1, k2, k3 = st.columns(3)
k1.metric("Estado", "Negociación")
k2.metric("Noticias", len(noticias))
k3.metric("Sectores", len(df))

# =========================
# LAYOUT
# =========================
col1, col2, col3 = st.columns([1.3, 1, 1])

# =========================
# 📰 NOTICIAS
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
# 🏭 SECTORES (SIMPLIFICADO)
# =========================
with col2:
    st.subheader("🏭 Sectores")

    sectores = df["sector"].dropna().unique()
    sector_sel = st.selectbox("Seleccionar sector", sectores)

    fila = df[df["sector"] == sector_sel].iloc[0]

    st.markdown(f"## {fila.get('sector','')}")

    st.write(limpiar_texto(fila.get("resumen","")))

    st.divider()

    # SOLO OPORTUNIDAD Y RIESGO
    colA, colB = st.columns(2)

    with colA:
        st.markdown("### Oportunidad Uruguay")
        st.write(limpiar_texto(fila.get("oportunidad_uy","")))

    with colB:
        st.markdown("### Nivel")
        st.write(f"**Oportunidad:** {fila.get('oportunidad','')}")
        st.write(f"**Riesgo:** {fila.get('riesgo','')}")

    st.divider()

    st.subheader("💡 Insight estratégico")
    st.write(limpiar_texto(fila.get("comentario_estrategico","")))

# =========================
# 🧠 ANÁLISIS
# =========================
with col3:
    st.subheader("🧠 Análisis")

    if len(analisis) == 0:
        st.info("No hay archivos en /analisis")

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
