
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import datetime

# Función para normalizar nombres de grupos
def normalizar_grupo(grupo):
    return str(grupo).strip().upper()

# Función para clasificar rendimiento
def clasificar_rendimiento(promedio):
    if promedio <= 250:
        return "Insuficiente"
    elif promedio <= 285:
        return "Intermedio"
    else:
        return "Adecuado"

# Portada PDF con logo
def portada_pdf(pdf, logo_path):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    if logo_path:
        pdf.image(logo_path, x=70, y=30, w=70)
    pdf.ln(120)
    pdf.cell(0, 10, "Informe de Agrupaciones y Rendimiento SIMCE", 0, 1, "C")
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Departamento de Lenguaje", 0, 1, "C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Fecha: {datetime.date.today().strftime('%d/%m/%Y')}", 0, 1, "C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 10, "Generado automáticamente con la aplicación de consolidación SIMCE", 0, 1, "C")

# Función para exportar PDF
def generar_pdf(resultados, logo_path):
    pdf = FPDF()
    portada_pdf(pdf, logo_path)

    for grupo, data in resultados.items():
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, f"Grupo {grupo}", 0, 1, "L")
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, f"Promedio: {data['promedio']:.2f} - {data['rendimiento']}", 0, 1, "L")

        # Insertar gráfico
        if "grafico" in data:
            img_bytes = BytesIO()
            data["grafico"].savefig(img_bytes, format="PNG")
            img_bytes.seek(0)
            img_path = f"/tmp/{grupo}.png"
            with open(img_path, "wb") as f:
                f.write(img_bytes.read())
            pdf.image(img_path, x=30, y=60, w=150)
            os.remove(img_path)

        # Top 5 alumnos más bajos
        pdf.ln(100)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Top 5 alumnos con menor puntaje:", 0, 1)
        pdf.set_font("Helvetica", "", 11)
        for alumno in data["peores"]:
            pdf.cell(0, 8, alumno, 0, 1)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

st.set_page_config(page_title="Agrupaciones SIMCE", layout="wide")
st.title("📊 Generador de Agrupaciones y Reporte SIMCE")

archivo = st.file_uploader("Sube el archivo consolidado (cursos 2º A - 2º F)", type=["xlsx"])
logo_path = "logo_liceo.png"  # Logo embebido en el proyecto

if archivo:
    xls = pd.ExcelFile(archivo)
    hojas = {"ABC": ["2º A", "2º B", "2º C"], "DEF": ["2º D", "2º E", "2º F"]}

    # Crear Excel de salida
    writer_buffer = BytesIO()
    writer = pd.ExcelWriter(writer_buffer, engine="xlsxwriter")
    resultados = {}

    for grupo_tipo, cursos in hojas.items():
        df_total = pd.concat([xls.parse(h) for h in cursos], ignore_index=True)
        df_total["GRUPO"] = df_total["GRUPO"].apply(normalizar_grupo)

        for grupo in ["1", "2", "3", "4", "5", "STEM", "RET", "PIE"]:
            df_grupo = df_total[df_total["GRUPO"] == grupo]
            if not df_grupo.empty:
                hoja_nombre = f"2°{grupo_tipo}-G{grupo}" if grupo.isdigit() else f"2°{grupo_tipo}-G{grupo}"
                df_grupo.to_excel(writer, sheet_name=hoja_nombre, index=False)

                # Calcular promedio (último ensayo disponible)
                ensayos = [c for c in df_grupo.columns if c.startswith("Puntaje Ensayo")]
                if ensayos:
                    promedios = df_grupo[ensayos].mean(axis=1, skipna=True)
                    promedio_grupo = promedios.mean()
                    clasificacion = clasificar_rendimiento(promedio_grupo)

                    # Gráfico circular
                    fig, ax = plt.subplots()
                    sizes = [1]  # solo un segmento representando el grupo
                    colors = {"Insuficiente": "red", "Intermedio": "yellow", "Adecuado": "blue"}
                    ax.pie(sizes, labels=[clasificacion], colors=[colors[clasificacion]], autopct='%1.1f%%')
                    ax.set_title(f"Rendimiento Grupo {hoja_nombre}")

                    # Peores 5 alumnos
                    peores = df_grupo.loc[promedios.nsmallest(5).index, "Nombre Estudiante"].tolist()

                    resultados[hoja_nombre] = {
                        "promedio": promedio_grupo,
                        "rendimiento": clasificacion,
                        "grafico": fig,
                        "peores": peores
                    }

    writer.close()
    writer_buffer.seek(0)

    st.download_button("📥 Descargar AGRUPACIONES.xlsx", data=writer_buffer, file_name="AGRUPACIONES.xlsx")

    # Mostrar resumen y gráficos
    st.header("📌 Resumen por Grupo")
    cols = st.columns(3)
    i = 0
    for grupo, data in resultados.items():
        with cols[i % 3]:
            st.subheader(grupo)
            st.write(f"Promedio: {data['promedio']:.2f} ({data['rendimiento']})")
            st.pyplot(data["grafico"])
        i += 1

    # Botón para generar PDF bajo demanda
    if st.button("📑 Generar Reporte PDF"):
        pdf_buffer = generar_pdf(resultados, logo_path)
        st.download_button("📥 Descargar Reporte PDF", data=pdf_buffer, file_name="Reporte_SIMCE.pdf")
