import streamlit as st
import feedparser
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# CONFIGURACIÓN PANTALLA COMPLETA
st.set_page_config(layout="wide")

# AUTO REFRESH (10 min)
st_autorefresh(interval=600000)

# TÍTULO
st.title("🪖 Dashboard Acuerdo Mercosur - UE")

# RSS
RSS_FEEDS = [
    "https://ec.europa.eu/commission/presscorner/api/rss",
    "https://www.ft.com/rss/world"
]

# FUNCIÓN NOTICIAS
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

noticias = obtener_noticias()

# FUNCIÓN RESUMEN SIMPLE
def resumen_simple(texto):
    return texto[:120] + "..."

# =========================
# 🧱 LAYOUT PRINCIPAL
# =========================

col1, col2, col3 = st.columns([1.3, 1, 1])

# 📰 NOVEDADES (IZQUIERDA)
with col1:
    st.subheader("📰 Novedades")

    for titulo, link, fecha in noticias[:5]:
        st.markdown(f"**{titulo}**")
        st.caption(fecha)
        st.markdown(f"[Leer más]({link})")
        st.divider()

# 🏭 SECTORES (CENTRO)
with col2:
    st.subheader("🏭 Sectores")

    try:
        df = pd.read_csv("sectores.csv")

        for _, row in df.iterrows():
            st.markdown(f"**{row['sector']}**")
            st.write(row["resumen"])
            st.caption(f"Nivel: {row['oportunidad']}")
            st.divider()

    except:
        st.info("Subí un archivo sectores.csv")

# 🧠 OPINIÓN (DERECHA)
with col3:
    st.subheader("🧠 Opinión")

    for titulo, link, fecha in noticias[:5]:
        st.markdown(f"**{titulo}**")
        st.write(resumen_simple(titulo))
        st.markdown(f"[Ver análisis]({link})")
        st.divider()

# =========================
# 📂 DOCUMENTOS (ABAJO)
# =========================

st.subheader("📂 Documentos del acuerdo")

colA, colB, colC = st.columns(3)

with colA:
    st.markdown("### 📜 Acuerdo")
    st.markdown("[Texto completo](https://example.com)")

with colB:
    st.markdown("### 📊 Anexos")
    st.markdown("[Listas arancelarias](https://example.com)")

with colC:
    st.markdown("### 📅 Cronograma")
    st.markdown("[Fechas clave](https://example.com)")
