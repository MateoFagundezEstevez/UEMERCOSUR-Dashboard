import streamlit as st
import feedparser
import os
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="UE–Mercosur Intelligence", layout="wide")
st_autorefresh(interval=600000)

# =========================
# ESTILO SIMPLE PERO LIMPIO
# =========================
st.markdown("""
<style>
.block-container {
    background-color: #0e1117;
    color: #e6edf3;
}

.card {
    background-color: #161b22;
    border: 1px solid #30363d;
    padding: 14px;
    border-radius: 12px;
    margin-bottom: 12px;
}

h1, h2, h3 {
    color: #e6edf3;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 UE–Mercosur Intelligence Brief")

# =========================
# FOCO REALISTA (NO ULTRA RÍGIDO)
# =========================
def es_relevante(texto):

    t = texto.lower()

    # 🎯 caso fuerte (acuerdo explícito)
    if "mercosur" in t and ("eu" in t or "ue" in t or "european union" in t):
        return True

    if "ue mercosur" in t or "eu mercosur" in t:
        return True

    # 🎯 caso medio (temática comercio + regiones)
    score = 0

    keywords = [
        "mercosur",
        "european union",
        "unión europea",
        "eu",
        "ue",
        "trade",
        "comercio",
        "tariff",
        "arancel",
        "agreement",
        "acuerdo"
    ]

    for k in keywords:
        if k in t:
            score += 1

    return score >= 3

# =========================
# RSS (realistas y suficientes)
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
def get_news():

    news = []

    for url in RSS_FEEDS:

        try:
            feed = feedparser.parse(url)

            for e in feed.entries:

                title = e.get("title", "")
                link = e.get("link", "")
                date = e.get("published", "Sin fecha")
                summary = (e.get("summary", "") or "")[:220]

                text = title + " " + summary

                if not es_relevante(text):
                    continue

                score = sum(k in text.lower() for k in ["mercosur", "eu", "ue", "trade", "agreement"])

                news.append({
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "date": date,
                    "score": score
                })

        except:
            continue

    return sorted(news, key=lambda x: x["score"], reverse=True)

# =========================
# DOCUMENTOS
# =========================
def get_docs():

    path = "analisis"
    docs = []

    if not os.path.exists(path):
        return docs

    for f in os.listdir(path):
        if f.endswith(".txt"):
            with open(os.path.join(path, f), "r", encoding="utf-8") as file:
                docs.append({
                    "name": f.replace(".txt",""),
                    "content": file.read()
                })

    return docs

# =========================
# DATA
# =========================
news = get_news()
docs = get_docs()

# =========================
# KPIs
# =========================
c1, c2 = st.columns(2)

c1.markdown(f"""
<div class="card">
<h3>📌 Foco</h3>
<p>UE–Mercosur Intelligence System</p>
</div>
""", unsafe_allow_html=True)

c2.markdown(f"""
<div class="card">
<h3>📰 Noticias relevantes</h3>
<p style="font-size:22px;"><b>{len(news)}</b></p>
</div>
""", unsafe_allow_html=True)

# =========================
# LAYOUT
# =========================
left, right = st.columns([1.6, 1])

# =========================
# 📰 NOTICIAS
# =========================
with left:

    st.subheader("📰 Señales del acuerdo UE–Mercosur")

    if len(news) == 0:
        st.warning("No se encontraron señales claras del acuerdo en este momento.")
    else:

        for n in news[:12]:

            st.markdown(f"""
            <div class="card">

                <h3>{n['title']}</h3>

                <small style="color:#9da7b3;">
                    {n['date']} · score {n['score']}
                </small>

                <p style="margin-top:10px;">
                    {n['summary']}
                </p>

                <a href="{n['link']}" target="_blank">→ Abrir fuente</a>

            </div>
            """, unsafe_allow_html=True)

# =========================
# 📄 ANÁLISIS
# =========================
with right:

    st.subheader("📄 Análisis estratégicos")

    if len(docs) == 0:
        st.info("No hay documentos cargados")
    else:

        for d in docs:

            with st.expander(d["name"]):

                st.write(d["content"][:600] + "...")

                st.download_button(
                    "⬇ Descargar",
                    d["content"],
                    file_name=d["name"] + ".txt"
                )
