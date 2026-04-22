import streamlit as st
import feedparser
import os
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide")
st_autorefresh(interval=600000)

# =========================
# ESTILO SIMPLE
# =========================
st.markdown("""
<style>
.block-container {
    background-color: #0e1117;
    color: #e6edf3;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Inteligencia UE–Mercosur")

# =========================
# FOCO ESTRATÉGICO
# =========================
KEYWORDS = [
    "mercosur", "unión europea", "ue", "eu",
    "acuerdo", "trade", "comercio",
    "arancel", "tariff", "negociación",
    "ratificación"
]

# =========================
# RSS (ajustado y estable)
# =========================
RSS_FEEDS = [
    "https://www.elpais.com.uy/rss/portada.xml",
    "https://www.elobservador.com.uy/rss/portada.xml",
    "https://www.montevideo.com.uy/noticias/rss",
    "https://www.lr21.com.uy/feed",
    "https://www.teledoce.com/feed/",
    "https://www.ft.com/rss/world",
    "https://www.economist.com/latest/rss.xml",
    "https://ec.europa.eu/commission/presscorner/api/rss"
]

# =========================
# NOTICIAS
# =========================
@st.cache_data(ttl=600)
def obtener_noticias():

    noticias = []

    for url in RSS_FEEDS:

        try:
            feed = feedparser.parse(url)

            for e in feed.entries:

                titulo = e.get("title", "")
                link = e.get("link", "")
                fecha = e.get("published", "Sin fecha")

                resumen = (e.get("summary", "") or "")[:250]

                texto = (titulo + " " + resumen).lower()

                # filtro fuerte UE–Mercosur
                if not any(k in texto for k in KEYWORDS):
                    continue

                score = sum(k in texto for k in KEYWORDS)

                noticias.append({
                    "titulo": titulo,
                    "resumen": resumen,
                    "link": link,
                    "fecha": fecha,
                    "score": score
                })

        except:
            continue

    return sorted(noticias, key=lambda x: x["score"], reverse=True)

# =========================
# DOCUMENTOS
# =========================
def cargar_docs():

    ruta = "analisis"
    docs = []

    if not os.path.exists(ruta):
        return docs

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
docs = cargar_docs()

# =========================
# KPIs
# =========================
c1, c2 = st.columns(2)
c1.metric("Foco", "UE–Mercosur")
c2.metric("Noticias relevantes", len(noticias))

# =========================
# LAYOUT
# =========================
col1, col2 = st.columns([1.6, 1])

# =========================
# 📰 NOTICIAS
# =========================
with col1:

    st.subheader("📰 Noticias relevantes")

    if len(noticias) == 0:
        st.warning("No se encontraron noticias relevantes")
    else:
        for n in noticias[:15]:

            st.markdown(f"### {n['titulo']}")
            st.caption(f"{n['fecha']} · score {n['score']}")
            st.write(n["resumen"])
            st.link_button("Abrir fuente", n["link"])
            st.divider()

# =========================
# 📄 ANÁLISIS
# =========================
with col2:

    st.subheader("📄 Análisis")

    if len(docs) == 0:
        st.info("No hay archivos en /analisis")
    else:

        for d in docs:

            with st.expander(d["nombre"]):

                st.write(d["contenido"][:600] + "...")

                st.download_button(
                    "⬇️ Descargar",
                    d["contenido"],
                    file_name=d["nombre"] + ".txt"
                )
