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
# ESTILO (UI MÁS PREMIUM)
# =========================
st.markdown("""
<style>
.block-container {
    background-color: #0e1117;
    color: #e6edf3;
    padding-top: 2rem;
}

.card {
    background-color: #161b22;
    border: 1px solid #30363d;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 12px;
}

.title {
    font-size: 28px;
    font-weight: 700;
}

.subtitle {
    color: #9da7b3;
    margin-bottom: 20px;
}

.badge {
    display:inline-block;
    padding:4px 8px;
    border-radius:6px;
    font-size:12px;
    margin-right:6px;
}

.badge.green { background:#1f6f3a; }
.badge.blue { background:#1f3a6f; }

a { color: #58a6ff; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER (MÁS INVITACIÓN)
# =========================
st.markdown('<div class="title">📊 UE–Mercosur Intelligence Brief</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Seguimiento estratégico del acuerdo comercial Unión Europea – Mercosur</div>', unsafe_allow_html=True)

# =========================
# FOCO SEMÁNTICO REAL
# =========================
def es_relevante(texto):

    texto = texto.lower()

    # explícito
    if "ue mercosur" in texto or "eu mercosur" in texto or "acuerdo ue mercosur" in texto:
        return True

    # ambos conceptos juntos
    ue = "eu" in texto or "ue" in texto or "unión europea" in texto
    mercosur = "mercosur" in texto

    return ue and mercosur

# =========================
# RSS
# =========================
RSS = [
    "https://www.elpais.com.uy/rss/portada.xml",
    "https://www.elobservador.com.uy/rss/portada.xml",
    "https://www.montevideo.com.uy/noticias/rss",
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

    for url in RSS:

        try:
            feed = feedparser.parse(url)

            for e in feed.entries:

                title = e.get("title", "")
                link = e.get("link", "")
                date = e.get("published", "Sin fecha")
                summary = (e.get("summary", "") or "")[:220]

                text = (title + " " + summary)

                if not es_relevante(text):
                    continue

                score = sum(k in text.lower() for k in ["eu", "ue", "mercosur", "acuerdo"])

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
# KPIs (GANCHO VISUAL)
# =========================
c1, c2, c3 = st.columns(3)

c1.markdown("""
<div class="card">
<div style="font-size:14px; color:#9da7b3;">Foco</div>
<div style="font-size:22px; font-weight:700;">UE–Mercosur</div>
</div>
""", unsafe_allow_html=True)

c2.markdown(f"""
<div class="card">
<div style="font-size:14px; color:#9da7b3;">Noticias relevantes</div>
<div style="font-size:22px; font-weight:700;">{len(news)}</div>
</div>
""", unsafe_allow_html=True)

c3.markdown(f"""
<div class="card">
<div style="font-size:14px; color:#9da7b3;">Documentos</div>
<div style="font-size:22px; font-weight:700;">{len(docs)}</div>
</div>
""", unsafe_allow_html=True)

# =========================
# LAYOUT
# =========================
left, right = st.columns([1.6, 1])

# =========================
# 📰 NOTICIAS (FOCO + UX MEJORADA)
# =========================
with left:

    st.subheader("📰 Últimas señales del acuerdo")

    if len(news) == 0:
        st.warning("No se encontraron noticias relevantes del acuerdo UE–Mercosur")
    else:

        for n in news[:12]:

            st.markdown(f"""
            <div class="card">

                <div style="font-size:18px; font-weight:600;">
                    {n['title']}
                </div>

                <div style="margin-top:6px; color:#9da7b3; font-size:12px;">
                    {n['date']} · score {n['score']}
                </div>

                <div style="margin-top:10px;">
                    {n['summary']}
                </div>

                <div style="margin-top:12px;">
                    <a href="{n['link']}" target="_blank">→ Abrir fuente</a>
                </div>

            </div>
            """, unsafe_allow_html=True)

# =========================
# 📄 ANÁLISIS (DESCARGABLES + MÁS LIMPIO)
# =========================
with right:

    st.subheader("📄 Análisis estratégicos")

    if len(docs) == 0:
        st.info("No hay documentos en /analisis")
    else:

        for d in docs:

            with st.expander("📄 " + d["name"]):

                st.write(d["content"][:600] + "...")

                st.download_button(
                    "⬇ Descargar documento",
                    d["content"],
                    file_name=d["name"] + ".txt"
                )
