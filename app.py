
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Función para clasificar el rendimiento
def clasificar_rendimiento(promedio):
    if promedio <= 250:
        return "Insuficiente"
    elif promedio <= 285:
        return "Intermedio"
    else:
        return "Adecuado"

# Función para normalizar grupos
def normalizar_grupo(grupo):
    return str(grupo).strip().upper()

# Título de la app
st.set_page_config(page_title="Resumen SIMCE", layout="wide")
st.title("📌 Resumen por Curso")

# Cargar archivo
uploaded_file = st.sidebar.file_uploader("📁 Subir archivo Excel o CSV", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    # Leer datos
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Normalizar nombres
    df["Grupo"] = df["Grupo"].apply(normalizar_grupo)
    df["Promedio"] = pd.to_numeric(df["Promedio"], errors="coerce")
    df["Nivel"] = df["Promedio"].apply(clasificar_rendimiento)

    # Selectbox de grupo
    grupos = sorted(df["Grupo"].unique())
    grupo_seleccionado = st.selectbox("Selecciona un grupo o curso", grupos)

    # Filtrar datos
    datos_grupo = df[df["Grupo"] == grupo_seleccionado]
    total = len(datos_grupo)
    promedio = datos_grupo["Promedio"].mean()
    nivel = clasificar_rendimiento(promedio)

    insuf = (datos_grupo["Nivel"] == "Insuficiente").mean() * 100
    inter = (datos_grupo["Nivel"] == "Intermedio").mean() * 100
    adec  = (datos_grupo["Nivel"] == "Adecuado").mean() * 100

    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Grupo", grupo_seleccionado)
    col2.metric("Promedio", f"{promedio:.2f} ({nivel})")
    col3.metric("Estudiantes", total)
    col4.metric("Adecuado", f"{adec:.1f}%")

    # Gráfico circular
    st.markdown(f"### Distribución por Nivel – {grupo_seleccionado}")
    fig, ax = plt.subplots()
    ax.pie(
        [insuf, inter, adec],
        labels=["Insuficiente", "Intermedio", "Adecuado"],
        colors=["#e84118", "#fbc531", "#44bd32"],
        autopct='%1.1f%%',
        startangle=90
    )
    ax.axis('equal')
    st.pyplot(fig)

else:
    st.info("Por favor sube un archivo para comenzar.")
