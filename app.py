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
# CARGA ROBUSTA CSV
# =========================
def cargar_sectores():
    try:
        df = pd.read_csv(
            "sectores.csv",
            sep=",",
            quotechar='"',
            engine="python",
            on_bad_lines="skip"
        )

        # Si quedó todo en una columna, reintentar
        if len(df.columns) == 1:
            df = pd.read_csv(
                "sectores.csv",
                sep=";",
                engine="python",
                on_bad_lines="skip"
            )

        # Limpiar columnas
        df.columns = df.columns.str.strip().str.lower()

        return df

    except Exception as e:
        st.error("Error leyendo sectores.csv")
        st.write(e)
        return None

# =========================
# DATA
# =========================
noticias = obtener_noticias()
analisis = cargar_analisis()
df = cargar_sectores()

# =========================
# KPIs
# =========================
k1, k2, k3 = st.columns(3)
k1.metric("Estado", "Negociación")
k2.metric("Noticias", len(noticias))
k3.metric("Análisis", len(analisis))

# =========================
# LAYOUT
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
# =========================
# 🏭 SECTORES INTERACTIVO
# =========================
with col2:
    st.subheader("🏭 Sectores")

    if df is None or df.empty:
        st.warning("No hay datos en sectores.csv")
        st.stop()

    # Selector de sector
    sector_seleccionado = st.selectbox(
        "Seleccionar sector",
        df["sector"]
    )

    # Filtrar
    fila = df[df["sector"] == sector_seleccionado].iloc[0]

    # Colores
    color_oportunidad = "#3fb950" if fila["oportunidad"] == "Alta" else "#d29922"
    color_riesgo = "#f85149" if fila["riesgo"] == "Alto" else "#d29922"

    # Render ficha
    st.markdown(f"""
    <div class="panel">

        <div style="font-size:18px; font-weight:700;">
            {fila['sector']}
        </div>

        <div style="margin-top:8px;">
            {fila['resumen']}
        </div>

        <hr style="border:0.5px solid #30363d;">

        <div style="font-size:13px;">
            <b>Arancel:</b> {fila['arancel_actual']} → {fila['arancel_futuro']}<br>
            <b>Cuotas:</b> {fila['cuotas']}<br>
            <b>Barreras:</b> {fila['barreras']}<br>
            <b>Oportunidad Uruguay:</b> {fila['oportunidad_uy']}<br>
        </div>

        <hr style="border:0.5px solid #30363d;">

        <div style="font-size:14px;">
            <span style="color:{color_oportunidad}; font-weight:bold;">
                Oportunidad: {fila['oportunidad']}
            </span> |
            <span style="color:{color_riesgo}; font-weight:bold;">
                Riesgo: {fila['riesgo']}
            </span>
        </div>

        <div style="margin-top:10px; font-size:14px;">
            💡 <b>Insight estratégico:</b><br>
            {fila['comentario_estrategico']}
        </div>

    </div>
    """, unsafe_allow_html=True)

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
