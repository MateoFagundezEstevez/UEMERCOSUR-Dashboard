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
# ESTILO BÁSICO
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
# FOCO ESTRATÉGICO (CLAVE)
# =========================
KEYWORDS_CORE = [
    "ue mercosur",
    "eu mercosur",
    "unión europea mercosur",
    "acuerdo ue mercosur",
    "trade agreement mercosur eu",
    "free trade agreement mercosur",
    "ratificación ue mercosur",
    "negociación ue mercosur"
]

KEYWORDS_CONTEXT = [
    "mercosur",
    "unión europea",
    "european union",
    "arancel",
    "tariff",
    "comercio",
    "trade",
    "acuerdo"
]

# =========================
# RSS
# =========================
RSS_URUGUAY = [
    "https://www.elpais.com.uy/rss/portada.xml",
    "https://www.elobservador.com.uy/rss/portada.xml",
    "https://www.montevideo.com.uy/noticias/rss",
    "https://www.lr21.com.uy/feed",
    "https://www.teledoce.com/feed/"
]

RSS_GLOBAL = [
    "https://www.ft.com/rss/world",
    "https://www.economist.com/latest/rss.xml",
    "https://www.reuters.com/rssFeed/worldNews",
    "https://ec.europa.eu/commission/presscorner/api/rss"
]

# =========================
# NOTICIAS (FOCUS ENGINE)
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

                # =========================
                # FILTRO INTELIGENTE
                # =========================
                core_hit = any(k in texto for k in KEYWORDS_CORE)
                context_hits = sum(k in texto for k in KEYWORDS_CONTEXT)

                if not (core_hit or context_hits >= 2):
                    continue

                noticias.append({
                    "titulo": titulo,
                    "resumen": resumen,
                    "link": link,
                    "fecha": fecha,
                    "fuente": fuente,
                    "prioridad": prioridad,
                    "score": (5 if core_hit else 0) + context_hits
                })

        except:
            pass

    for u in RSS_URUGUAY:
        procesar(u, "Uruguay", 1)

    for u in RSS_GLOBAL:
        procesar(u, "Internacional", 2)

    return sorted(noticias, key=lambda x: x["score"], reverse=True)

# =========================
# SECTORES
# =========================
@st.cache_data
def cargar_sectores():

    if not os.path.exists("sectores.csv"):
        return pd.DataFrame()

    df = pd.read_csv("sectores.csv")
    df.columns = df.columns.str.strip().str.lower()

    return df

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
df = cargar_sectores()
docs = cargar_docs()

# =========================
# KPIs
# =========================
c1, c2, c3 = st.columns(3)
c1.metric("Foco", "UE–Mercosur")
c2.metric("Noticias relevantes", len(noticias))
c3.metric("Sectores", len(df))

# =========================
# LAYOUT
# =========================
col1, col2, col3 = st.columns([1.4, 1, 1])

# =========================
# 📰 NOTICIAS (FOCO REAL)
# =========================
with col1:

    st.subheader("📰 Acuerdo UE–Mercosur")

    for n in noticias[:12]:

        st.markdown(f"### {n['titulo']}")
        st.caption(f"{n['fecha']} · {n['fuente']} · score {n['score']}")
        st.write(n["resumen"])
        st.link_button("Abrir fuente", n["link"])
        st.divider()

# =========================
# 🏭 SECTORES
# =========================
with col2:

    st.subheader("🏭 Sectores")

    if df.empty:
        st.warning("No hay sectores.csv")
    else:

        sector = st.selectbox("Seleccionar sector", df["sector"].dropna().unique())

        row = df[df["sector"] == sector].iloc[0]

        st.markdown(f"## {row['sector']}")
        st.write(row.get("resumen",""))

        st.divider()

        st.write("### Oportunidad Uruguay")
        st.write(row.get("oportunidad_uy",""))

        st.write("### Evaluación")
        st.write(f"Oportunidad: {row.get('oportunidad','')}")
        st.write(f"Riesgo: {row.get('riesgo','')}")

        st.divider()

        st.write("💡 Insight estratégico")
        st.write(row.get("comentario_estrategico",""))

# =========================
# 📄 DOCUMENTOS
# =========================
with col3:

    st.subheader("📄 Documentos")

    if len(docs) == 0:
        st.info("No hay documentos")

    for d in docs:

        with st.expander(d["nombre"]):

            st.write(d["contenido"][:500] + "...")

            st.download_button(
                "⬇️ Descargar",
                d["contenido"],
                file_name=d["nombre"] + ".txt"
            )
