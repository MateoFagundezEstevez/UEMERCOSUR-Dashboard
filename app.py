import streamlit as st
import feedparser
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# CONFIG
st.set_page_config(layout="wide")

# AUTO REFRESH
st_autorefresh(interval=600000)

# =========================
# 🎨 ESTILO MILITAR (CSS)
# =========================
st.markdown("""
<style>
body {
    background-color: #0a0f0a;
}

.block-container {
    background-color: #0a0f0a;
    color: #00ff9c;
    font-family: "Courier New", monospace;
}

/* Títulos */
h1, h2, h3 {
    color: #00ff9c;
}

/* Cajas tipo panel */
.panel {
    border: 1px solid #00ff9c;
    padding: 15px;
    border-radius: 8px;
    background-color: #0d140d;
    margin-bottom: 10px;
}

/* Estados */
.green { color: #00ff9c; }
.red { color: #ff4d4d; }
.yellow { color: #ffd166; }

/* Links */
a {
    color: #00ff9c;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🧠 DATA
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
    return texto[:100] + "..."

noticias = obtener_noticias()

# =========================
# 🪖 HEADER
# =========================
st.title("🪖 CENTRO DE COMANDO | ACUERDO MERCOSUR - UE")

# =========================
# 📊 KPIs ARRIBA
# =========================
kpi1, kpi2, kpi3 = st.columns(3)

kpi1.metric("Estado", "En negociación")
kpi2.metric("Noticias activas", len(noticias))
kpi3.metric("Sectores cargados", "Manual")

# =========================
# 🧱 LAYOUT PRINCIPAL
# =========================

col1, col2, col3 = st.columns([1.3, 1, 1])

# 📰 NOVEDADES
with col1:
    st.subheader("📰 INTEL | NOVEDADES")

    for titulo, link, fecha in noticias[:5]:
        st.markdown(f"""
        <div class="panel">
            <b>{titulo}</b><br>
            <span class="yellow">{fecha}</span><br>
            <a href="{link}" target="_blank">Leer más</a>
        </div>
        """, unsafe_allow_html=True)

# 🏭 SECTORES
with col2:
    st.subheader("🏭 SECTORES ESTRATÉGICOS")

    try:
        df = pd.read_csv("sectores.csv")

        for _, row in df.iterrows():
            color = "green" if row["oportunidad"] == "Alta" else "yellow"

            st.markdown(f"""
            <div class="panel">
                <b>{row['sector']}</b><br>
                {row['resumen']}<br>
                <span class="{color}">Nivel: {row['oportunidad']}</span>
            </div>
            """, unsafe_allow_html=True)

    except:
        st.warning("Cargar archivo sectores.csv")

# 🧠 OPINIÓN
with col3:
    st.subheader("🧠 ANÁLISIS")

    for titulo, link, fecha in noticias[:5]:
        st.markdown(f"""
        <div class="panel">
            <b>{titulo}</b><br>
            {resumen_simple(titulo)}<br>
            <a href="{link}" target="_blank">Ver análisis</a>
        </div>
        """, unsafe_allow_html=True)

# =========================
# 📂 DOCUMENTOS
# =========================

st.subheader("📂 ARCHIVOS DEL ACUERDO")

colA, colB, colC = st.columns(3)

with colA:
    st.markdown("""
    <div class="panel">
    📜 <b>Texto del acuerdo</b><br>
    <a href="#">Descargar</a>
    </div>
    """, unsafe_allow_html=True)

with colB:
    st.markdown("""
    <div class="panel">
    📊 <b>Anexos</b><br>
    <a href="#">Ver documentos</a>
    </div>
    """, unsafe_allow_html=True)

with colC:
    st.markdown("""
    <div class="panel">
    📅 <b>Cronograma</b><br>
    <a href="#">Ver fechas</a>
    </div>
    """, unsafe_allow_html=True)
