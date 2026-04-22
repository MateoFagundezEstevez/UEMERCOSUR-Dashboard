import streamlit as st
import feedparser

st.title("📰 Novedades Mercosur - UE")

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

noticias = obtener_noticias()

for titulo, link, fecha in noticias:
    st.subheader(titulo)
    st.write(fecha)
    st.markdown(f"[Leer más]({link})")
    st.divider()
