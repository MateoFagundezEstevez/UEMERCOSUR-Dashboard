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
# CSV SECTORES
# =========================
@st.cache_data
def cargar_sectores():
    ruta = "sectores.csv"

    if not os.path.exists(ruta):
        st.error("No se encontró sectores.csv")
        return pd.DataFrame()

    df = pd.read_csv(ruta)
    df.columns = df.columns.str.strip().str.lower()

    return df

# =========================
# DOCUMENTOS (TXT)
# =========================
def cargar_documentos():
    ruta = "analisis"
    docs = []

    if not os.path.exists(ruta):
        return []

    for archivo in os.listdir(ruta):
        if archivo.endswith(".txt"):
            path = os.path.join(ruta, archivo)

            with open(path, "r", encoding="utf-8") as f:
                contenido = f.read()

            docs.append({
                "nombre": archivo.replace(".txt", ""),
                "contenido": contenido
            })

    return docs

# =========================
# DATA
# =========================
noticias = obtener_noticias()
df = cargar_sectores()
docs = cargar_documentos()

if df.empty:
    st.warning("No se cargó el CSV de sectores")
    st.stop()

# =========================
# KPIs
# =========================
c1, c2, c3 = st.columns(3)
c1.metric("Estado", "Negociación")
c2.metric("Noticias", len(noticias))
c3.metric("Sectores", len(df))

# =========================
# LAYOUT PRINCIPAL
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
# 🏭 SECTORES
# =========================
with col2:
    st.subheader("🏭 Sectores")

    sector_sel = st.selectbox(
        "Seleccionar sector",
        df["sector"].dropna().unique()
    )

    fila = df[df["sector"] == sector_sel].iloc[0]

    st.markdown(f"## {fila['sector']}")

    st.write(limpiar_texto(fila.get("resumen","")))

    st.divider()

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
# 📄 DOCUMENTOS DESCARGABLES
# =========================
with col3:
    st.subheader("📄 Documentos")

    if len(docs) == 0:
        st.info("No hay documentos en /analisis")

    for doc in docs:
        with st.expander(doc["nombre"]):

            st.write(doc["contenido"][:300] + "...")

            st.download_button(
                label="⬇️ Descargar",
                data=doc["contenido"],
                file_name=doc["nombre"] + ".txt",
                mime="text/plain"
            )
