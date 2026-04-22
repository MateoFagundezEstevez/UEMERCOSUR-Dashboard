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
# CSV CARGA ROBUSTA
# =========================
@st.cache_data
def cargar_csv():
    try:
        df = pd.read_csv("sectores.csv", encoding="utf-8")

        # normalización de columnas
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        return df

    except Exception as e:
        st.error("Error cargando sectores.csv")
        st.exception(e)
        return pd.DataFrame()

df = cargar_csv()

# =========================
# VALIDACIÓN
# =========================
if df.empty:
    st.warning("No hay datos en sectores.csv")
    st.stop()

# =========================
# KPIs
# =========================
k1, k2, k3 = st.columns(3)
k1.metric("Filas", len(df))
k2.metric("Columnas", len(df.columns))
k3.metric("Dataset", "Activo")

# =========================
# 🔎 EXPLORADOR DE DATOS (INTERACTIVO)
# =========================
st.subheader("📊 Explorador del dataset")

# Selector de columnas para filtrar
columnas = df.columns.tolist()

col_filtro = st.selectbox("Filtrar por columna (opcional)", ["(ninguno)"] + columnas)

df_filtrado = df.copy()

if col_filtro != "(ninguno)":
    valores = df[col_filtro].dropna().unique().tolist()
    seleccion = st.multiselect("Valores", valores)

    if seleccion:
        df_filtrado = df[df[col_filtro].isin(seleccion)]

# Mostrar tabla interactiva
st.dataframe(df_filtrado, use_container_width=True)

# =========================
# 🧠 PANEL INTELIGENTE SECTOR (SOLO SI EXISTE)
# =========================
if "sector" in df.columns:
    st.subheader("🏭 Vista por sector")

    sector = st.selectbox("Seleccionar sector", df["sector"].dropna().unique())

    fila = df[df["sector"] == sector].iloc[0]

    st.markdown(f"""
    <div class="panel">
        <h3>{fila.get('sector','')}</h3>

        <p>{fila.get('resumen','')}</p>

        <hr>

        <b>Arancel:</b> {fila.get('arancel_actual','?')} → {fila.get('arancel_futuro','?')}<br>
        <b>Cuotas:</b> {fila.get('cuotas','?')}<br>
        <b>Barreras:</b> {fila.get('barreras','?')}<br>
        <b>Oportunidad:</b> {fila.get('oportunidad','?')}<br>
        <b>Riesgo:</b> {fila.get('riesgo','?')}<br>

        <hr>

        💡 <b>Insight:</b><br>
        {fila.get('comentario_estrategico','')}
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("No existe columna 'sector' en el CSV. Se muestra solo explorador general.")

# =========================
# DESCARGA
# =========================
st.download_button(
    "⬇️ Descargar dataset filtrado",
    df_filtrado.to_csv(index=False).encode("utf-8"),
    "sectores_filtrado.csv",
    "text/csv"
)
