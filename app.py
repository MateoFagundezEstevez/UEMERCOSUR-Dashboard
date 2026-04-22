import streamlit as st
import feedparser
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
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

st.title("📊 Motor de Inteligencia Diplomática UE – Mercosur")

# =========================
# FILTROS CLAVE
# =========================
FILTROS = [
    "mercosur", "ue", "eu", "unión europea",
    "uruguay", "export", "comercio",
    "arancel", "acuerdo", "trade", "tariff"
]

# =========================
# RSS MEDIOS
# =========================
RSS_URUGUAY = [
    "https://www.elpais.com.uy/rss/portada.xml",
    "https://www.elobservador.com.uy/rss/portada.xml",
    "https://www.montevideo.com.uy/noticias/rss",
    "https://www.lr21.com.uy/feed",
    "https://www.teledoce.com/feed/",
    "https://www.subrayado.com.uy/rss"
]

RSS_INTERNACIONAL = [
    "https://www.ft.com/rss/world",
    "https://www.economist.com/latest/rss.xml",
    "https://www.reuters.com/rssFeed/worldNews",
    "https://ec.europa.eu/commission/presscorner/api/rss"
]

# =========================
# FUENTES INSTITUCIONALES
# =========================
FUENTES_INSTITUCIONALES = [
    {
        "nombre": "Cancillería Uruguay",
        "url": "https://www.gub.uy/ministerio-relaciones-exteriores/comunicacion/noticias/rss"
    },
    {
        "nombre": "Cámara de Industrias del Uruguay",
        "url": "https://ciu.com.uy/feed/"
    }
]

# =========================
# EXPERTOS (CURADO)
# =========================
EXPERTOS = [
    {
        "nombre": "Ignacio Bartesaghi",
        "rol": "Académico UCU",
        "idea": "Inserción internacional urgente de Uruguay en acuerdos globales."
    },
    {
        "nombre": "Valeria Csukasi",
        "rol": "Cancillería",
        "idea": "El acuerdo UE–Mercosur requiere implementación gradual y ratificación política."
    }
]

# =========================
# UTILIDAD SCORE
# =========================
def score(texto, prioridad):
    s = 0
    texto = texto.lower()

    if prioridad == 1:
        s += 3

    if any(k in texto for k in ["mercosur", "ue", "eu"]):
        s += 3

    if any(k in texto for k in ["export", "comercio", "arancel"]):
        s += 2

    return s

# =========================
# NOTICIAS
# =========================
@st.cache_data(ttl=600)
def obtener_noticias():

    noticias = []

    def procesar(url, fuente, prioridad):

        try:
            feed = feedparser.parse(url)

            for e in feed.entries:

                titulo = e.get("title", "")
                link = e.get("link", "")
                fecha = e.get("published", "Sin fecha")

                resumen = (e.get("summary", "") or "")[:250]

                texto = (titulo + " " + resumen).lower()

                if not any(f in texto for f in FILTROS):
                    continue

                noticias.append({
                    "titulo": titulo,
                    "resumen": resumen,
                    "link": link,
                    "fecha": fecha,
                    "fuente": fuente,
                    "prioridad": prioridad
                })

        except:
            pass

    for u in RSS_URUGUAY:
        procesar(u, "Uruguay", 1)

    for u in RSS_INTERNACIONAL:
        procesar(u, "Internacional", 2)

    return sorted(noticias, key=lambda x: score(x["titulo"], x["prioridad"]), reverse=True)

# =========================
# INSTITUCIONES
# =========================
@st.cache_data(ttl=600)
def obtener_instituciones():

    resultados = []

    for f in FUENTES_INSTITUCIONALES:

        try:
            feed = feedparser.parse(f["url"])

            for e in feed.entries:

                texto = (e.get("title","") + " " + e.get("summary","")).lower()

                if not any(k in texto for k in FILTROS):
                    continue

                resultados.append({
                    "titulo": e.get("title",""),
                    "link": e.get("link",""),
                    "fuente": f["nombre"],
                    "tipo": "institucional"
                })

        except:
            continue

    return resultados

# =========================
# DOCUMENTOS
# =========================
def cargar_docs():
    ruta = "analisis"
    docs = []

    if not os.path.exists(ruta):
        return []

    for f in os.listdir(ruta):
        if f.endswith(".txt"):
            with open(os.path.join(ruta, f), "r", encoding="utf-8") as file:
                docs.append({
                    "nombre": f.replace(".txt",""),
                    "contenido": file.read()
                })

    return docs

# =========================
# DATA
# =========================
noticias = obtener_noticias()
instituciones = obtener_instituciones()
docs = cargar_docs()

# =========================
# KPIs
# =========================
c1, c2, c3 = st.columns(3)
c1.metric("Estado", "UE–Mercosur")
c2.metric("Noticias", len(noticias))
c3.metric("Fuentes institucionales", len(instituciones))

# =========================
# LAYOUT
# =========================
col1, col2, col3 = st.columns([1.4, 1, 1])

# =========================
# 📰 NOTICIAS
# =========================
with col1:
    st.subheader("📰 Inteligencia de Noticias")

    for n in noticias[:10]:

        color = "#3fb950" if n["prioridad"] == 1 else "#9da7b3"

        st.markdown(f"""
        <div class="panel">

            <div style="font-weight:700; color:{color}">
                {n['titulo']}
            </div>

            <div style="font-size:11px; color:#9da7b3;">
                {n['fecha']} · {n['fuente']}
            </div>

            <div style="margin-top:8px;">
                {n['resumen']}
            </div>

            <a href="{n['link']}" target="_blank">Leer más</a>

        </div>
        """, unsafe_allow_html=True)

# =========================
# 🏛️ INSTITUCIONES + EXPERTOS
# =========================
with col2:

    st.subheader("🏛️ Instituciones")

    for i in instituciones[:8]:

        st.markdown(f"""
        <div class="panel">

            <div style="font-weight:700;">
                {i['titulo']}
            </div>

            <div style="font-size:11px; color:#9da7b3;">
                {i['fuente']}
            </div>

            <a href="{i['link']}" target="_blank">Ver fuente</a>

        </div>
        """, unsafe_allow_html=True)

    st.subheader("🧠 Expertos")

    for e in EXPERTOS:

        st.markdown(f"""
        <div class="panel">

            <div style="font-weight:700;">
                {e['nombre']}
            </div>

            <div style="font-size:11px; color:#9da7b3;">
                {e['rol']}
            </div>

            <div style="margin-top:8px;">
                {e['idea']}
            </div>

        </div>
        """, unsafe_allow_html=True)

# =========================
# 📄 DOCUMENTOS
# =========================
with col3:

    st.subheader("📄 Documentos")

    if len(docs) == 0:
        st.info("No hay documentos")

    for d in docs:

        with st.expander(d["nombre"]):

            st.write(d["contenido"][:300] + "...")

            st.download_button(
                "Descargar",
                d["contenido"],
                file_name=d["nombre"] + ".txt"
            )
