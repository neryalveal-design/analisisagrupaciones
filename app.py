
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import datetime

# Función para normalizar nombres de grupos
def normalizar_grupo(grupo):
    return str(grupo).strip().upper()

# Función para clasificar rendimiento individual
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

# Página de resumen general
def resumen_general(pdf, resultados):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Resumen General por Grupo", 0, 1, "L")
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(60, 10, "Grupo", 1)
    pdf.cell(40, 10, "Promedio", 1)
    pdf.cell(40, 10, "Estudiantes", 1)
    pdf.cell(50, 10, "Rendimiento", 1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 12)
    for grupo, data in resultados.items():
        pdf.cell(60, 10, grupo, 1)
        pdf.cell(40, 10, f"{data['promedio']:.2f}", 1)
        pdf.cell(40, 10, str(data['n_estudiantes']), 1)
        pdf.cell(50, 10, data['rendimiento'], 1)
        pdf.ln()

# Función para exportar PDF
def generar_pdf(resultados, logo_path):
    pdf = FPDF()
    portada_pdf(pdf, logo_path)
    resumen_general(pdf, resultados)

    for grupo, data in resultados.items():
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, f"Grupo {grupo}", 0, 1, "L")
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, f"Promedio: {data['promedio']:.2f} - {data['rendimiento']}", 0, 1, "L")
        pdf.cell(0, 10, f"Número de estudiantes: {data['n_estudiantes']}", 0, 1, "L")

        # Distribución porcentual
        pdf.cell(0, 10, "Distribución de rendimiento:", 0, 1, "L")
        for nivel, porcentaje in data["porcentajes"].items():
            pdf.cell(0, 10, f"{nivel}: {porcentaje:.1f}%", 0, 1, "L")

        # Insertar gráfico de distribución
        if "grafico" in data:
            img_bytes = BytesIO()
            data["grafico"].savefig(img_bytes, format="PNG")
            img_bytes.seek(0)
            img_path = f"/tmp/{grupo}.png"
            with open(img_path, "wb") as f:
                f.write(img_bytes.read())
            pdf.image(img_path, x=30, y=100, w=150)
            os.remove(img_path)

        # Top 5 alumnos más bajos
        pdf.ln(120)
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
logo_path = "logo_liceo.png"

if archivo:
    xls = pd.ExcelFile(archivo)
    hojas = {"ABC": ["2º A", "2º B", "2º C"], "DEF": ["2º D", "2º E", "2º F"]}

    writer_buffer = BytesIO()
    writer = pd.ExcelWriter(writer_buffer, engine="xlsxwriter")
    resultados = {}

    for grupo_tipo, cursos in hojas.items():
        df_total = pd.concat([xls.parse(h) for h in cursos], ignore_index=True)
        df_total["GRUPO"] = df_total["GRUPO"].apply(normalizar_grupo)

        for grupo in ["1", "2", "3", "4", "5", "STEM", "RET", "PIE"]:
            df_grupo = df_total[df_total["GRUPO"] == grupo]
            if not df_grupo.empty:
                hoja_nombre = f"2°{grupo_tipo}-G{grupo}"
                df_grupo.to_excel(writer, sheet_name=hoja_nombre, index=False)

                ensayos = [c for c in df_grupo.columns if c.startswith("Puntaje Ensayo")]
                if ensayos:
                    # Promedios individuales por alumno
                    promedios_ind = df_grupo[ensayos].mean(axis=1, skipna=True)

                    # Clasificación por alumno
                    clasificaciones = promedios_ind.apply(clasificar_rendimiento)
                    dist = clasificaciones.value_counts(normalize=True) * 100

                    # Promedio del grupo
                    promedio_grupo = promedios_ind.mean()
                    clasificacion_grupo = clasificar_rendimiento(promedio_grupo)

                    # Gráfico de distribución
                    fig, ax = plt.subplots()
                    labels = ["Insuficiente", "Intermedio", "Adecuado"]
                    values = [dist.get(l, 0) for l in labels]
                    colors = ["red", "yellow", "blue"]
                    ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%')
                    ax.set_title(f"Distribución Grupo {hoja_nombre}")

                    # Peores 5 alumnos
                    peores = df_grupo.loc[promedios_ind.nsmallest(5).index, "Nombre Estudiante"].tolist()

                    resultados[hoja_nombre] = {
                        "promedio": promedio_grupo,
                        "rendimiento": clasificacion_grupo,
                        "grafico": fig,
                        "peores": peores,
                        "n_estudiantes": len(df_grupo),
                        "porcentajes": {l: dist.get(l, 0) for l in labels}
                    }

    writer.close()
    writer_buffer.seek(0)

    st.download_button("📥 Descargar AGRUPACIONES.xlsx", data=writer_buffer, file_name="AGRUPACIONES.xlsx")

    st.header("📌 Resumen por Grupo")
    cols = st.columns(3)
    i = 0
    for grupo, data in resultados.items():
        with cols[i % 3]:
            st.subheader(grupo)
            st.write(f"Promedio: {data['promedio']:.2f} ({data['rendimiento']})")
            st.write(f"Estudiantes: {data['n_estudiantes']}")
            for nivel, porcentaje in data["porcentajes"].items():
                st.write(f"{nivel}: {porcentaje:.1f}%")
            st.pyplot(data["grafico"])
        i += 1

    if st.button("📑 Generar Reporte PDF"):
        pdf_buffer = generar_pdf(resultados, logo_path)
        st.download_button("📥 Descargar Reporte PDF", data=pdf_buffer, file_name="Reporte_SIMCE.pdf")
