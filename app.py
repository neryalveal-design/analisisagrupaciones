
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import base64
from io import BytesIO
from fpdf import FPDF

# ----------------------------
# FUNCIONES AUXILIARES
# ----------------------------

def logo_to_base64(img_path):
    img = Image.open(img_path)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def plot_line_evolucion(promedios):
    fig, ax = plt.subplots()
    ax.plot(range(1, len(promedios)+1), promedios, marker='o', color='#1e3799')
    ax.set_title("Evolución del Promedio")
    ax.set_xlabel("Ensayo")
    ax.set_ylabel("Promedio")
    ax.grid(True)
    return fig

def plot_pie_niveles(adecuado, intermedio, insuficiente):
    fig, ax = plt.subplots()
    ax.pie(
        [adecuado, intermedio, insuficiente],
        labels=["Adecuado", "Intermedio", "Insuficiente"],
        colors=["#44bd32", "#fbc531", "#e84118"],
        autopct='%1.0f%%',
        startangle=90
    )
    ax.set_title("Distribución por Nivel")
    ax.axis('equal')
    return fig

def plot_bar_comparativo(cursos, promedios):
    fig, ax = plt.subplots()
    ax.bar(cursos, promedios, color='#0984e3')
    ax.set_title("Promedio por Curso")
    ax.set_ylabel("Puntaje")
    plt.xticks(rotation=45)
    return fig

def plot_stacked_niveles(cursos, adecuado, intermedio, insuficiente):
    fig, ax = plt.subplots()
    ax.bar(cursos, adecuado, label='Adecuado', color='#44bd32')
    ax.bar(cursos, intermedio, bottom=adecuado, label='Intermedio', color='#fbc531')
    bottom_sum = [a + i for a, i in zip(adecuado, intermedio)]
    ax.bar(cursos, insuficiente, bottom=bottom_sum, label='Insuficiente', color='#e84118')
    ax.set_ylabel('% de Estudiantes')
    ax.set_title('Distribución de Niveles (%)')
    plt.xticks(rotation=45)
    ax.legend()
    return fig

def save_chart_as_image(fig, filename):
    fig.savefig(filename, format='png', bbox_inches='tight')
    plt.close(fig)

def generar_pdf_curso(nombre_curso, logo_path, resumen_data, graficos_paths, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.image(logo_path, x=10, y=8, w=25)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Liceo San Nicolás - Departamento de Lenguaje", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Informe de Resultados SIMCE - Curso {nombre_curso}", ln=True, align='C')
    pdf.ln(10)
    for label, value in resumen_data.items():
        pdf.cell(0, 10, f"{label}: {value}", ln=True)
    for path in graficos_paths:
        pdf.ln(5)
        pdf.image(path, w=180)
    pdf.output(output_path)

# ----------------------------
# CONFIGURACIÓN INICIAL
# ----------------------------

logo_path = "logo_liceo.png"
logo_base64 = logo_to_base64(logo_path)

st.set_page_config(page_title="Análisis SIMCE", page_icon="📊", layout="wide")

st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    .custom-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background-color: #f0f4f7;
        border-bottom: 2px solid #dcdcdc;
    }}

    .custom-header h1 {{
        color: #1e3799;
        font-size: 26px;
        margin: 0;
    }}

    .custom-subtitle {{
        font-size: 16px;
        color: #444;
        margin-top: 0.2rem;
    }}

    div.stDownloadButton > button {{
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.75em 1.5em;
        font-size: 16px;
        border: none;
        margin-top: 1rem;
    }}

    div.stDownloadButton > button:hover {{
        background-color: #e84118;
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="custom-header">
    <div>
        <h1>Liceo San Nicolás - Departamento de Lenguaje</h1>
        <div class="custom-subtitle">Sistema de análisis de resultados educativos SIMCE</div>
    </div>
    <div>
        <img src="data:image/png;base64,{logo_base64}" width="60"/>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# NAVEGACIÓN
# ----------------------------

st.sidebar.title("📊 Análisis SIMCE")
menu = st.sidebar.radio("Ir a:", ["📁 Cargar Datos", "📊 Resumen por Curso", "👨‍🎓 Reportes Estudiantes", "📈 Comparativo Cursos", "💡 Recomendaciones"])

# ----------------------------
# VISTA: CARGAR DATOS
# ----------------------------

if menu == "📁 Cargar Datos":
    st.title("📁 Cargar Resultados SIMCE")
    uploaded_file = st.file_uploader("Seleccionar Archivo", type=["xlsx", "xls", "csv"])
    st.markdown("### Formato Esperado")
    st.markdown("Archivo Excel con hojas por curso o CSV por curso.")
    if st.button("Usar Datos de Ejemplo"):
        st.success("Funcionalidad de ejemplo activada. Aquí se cargarían los datos de prueba.")

# ----------------------------
# VISTA: RESUMEN POR CURSO
# ----------------------------

elif menu == "📊 Resumen por Curso":
    st.title("📊 Resumen por Curso")
    nombre_curso = "2°ABC-G1"
    resumen_data = {
        "Total Estudiantes": 22,
        "Promedio General": "318.6",
        "Mediana": "313",
        "Total Ensayos": 8
    }

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Estudiantes", resumen_data["Total Estudiantes"])
    col2.metric("Promedio General", resumen_data["Promedio General"])
    col3.metric("Mediana", resumen_data["Mediana"])
    col4.metric("Total Ensayos", resumen_data["Total Ensayos"])

    col5, col6 = st.columns(2)
    fig1 = plot_line_evolucion([307.7, 282.7, 307.1, 332.7, 318.6, 300.0, 368.3, 313.0])
    fig2 = plot_pie_niveles(75, 20, 5)
    col5.pyplot(fig1)
    col6.pyplot(fig2)

    path1 = f"/tmp/evolucion_{nombre_curso}.png"
    path2 = f"/tmp/niveles_{nombre_curso}.png"
    save_chart_as_image(fig1, path1)
    save_chart_as_image(fig2, path2)

    pdf_output_path = f"/tmp/reporte_{nombre_curso}.pdf"
    generar_pdf_curso(nombre_curso, logo_path, resumen_data, [path1, path2], pdf_output_path)

    with open(pdf_output_path, "rb") as f:
        pdf_bytes = f.read()
    pdf_b64 = base64.b64encode(pdf_bytes).decode()

    st.markdown(f"""
        <div style="display: flex; justify-content: flex-end;">
            <a href="data:application/pdf;base64,{pdf_b64}" download="Reporte_SIMCE_{nombre_curso}.pdf">
                <button>
                    📄 Descargar PDF del Curso
                </button>
            </a>
        </div>
    """, unsafe_allow_html=True)

# ----------------------------
# VISTA: COMPARATIVO CURSOS
# ----------------------------

elif menu == "📈 Comparativo Cursos":
    st.title("📈 Comparativo entre Cursos")

    cursos = [
        {"nombre": "2°ABC-G2", "promedio": 330, "adecuado": 40, "intermedio": 30, "insuficiente": 30},
        {"nombre": "2°DEF-G1", "promedio": 355, "adecuado": 60, "intermedio": 20, "insuficiente": 20},
        {"nombre": "2°DEF-G3", "promedio": 290, "adecuado": 25, "intermedio": 25, "insuficiente": 50}
    ]

    for curso in cursos:
        nombre = curso["nombre"]
        st.subheader(f"📘 {nombre}")
        resumen_data = {
            "Total Estudiantes": 30,
            "Promedio General": curso["promedio"],
            "Mediana": curso["promedio"] - 10,
            "Total Ensayos": 8
        }

        fig1 = plot_line_evolucion([280, 295, curso["promedio"], 310])
        fig2 = plot_pie_niveles(curso["adecuado"], curso["intermedio"], curso["insuficiente"])
        path1 = f"/tmp/evolucion_{nombre}.png"
        path2 = f"/tmp/niveles_{nombre}.png"
        save_chart_as_image(fig1, path1)
        save_chart_as_image(fig2, path2)
        pdf_output_path = f"/tmp/reporte_{nombre}.pdf"
        generar_pdf_curso(nombre, logo_path, resumen_data, [path1, path2], pdf_output_path)
        with open(pdf_output_path, "rb") as f:
            pdf_bytes = f.read()
        pdf_b64 = base64.b64encode(pdf_bytes).decode()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Estudiantes", resumen_data["Total Estudiantes"])
        col2.metric("Promedio", resumen_data["Promedio General"])
        col3.metric("Mediana", resumen_data["Mediana"])
        col4.metric("Ensayos", resumen_data["Total Ensayos"])

        st.markdown(f"""
            <div style="display: flex; justify-content: flex-end;">
                <a href="data:application/pdf;base64,{pdf_b64}" download="Reporte_SIMCE_{nombre}.pdf">
                    <button>
                        📄 Descargar PDF del Curso
                    </button>
                </a>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

# ----------------------------
# VISTA: RECOMENDACIONES
# ----------------------------

elif menu == "💡 Recomendaciones":
    st.title("💡 Recomendaciones Pedagógicas")
    st.markdown("""
    - 🔴 **Insuficiente**: Requieren intervención inmediata.
    - 🟡 **Intermedio**: Consolidar aprendizajes.
    - 🟢 **Adecuado**: Desafíos adicionales y enriquecimiento.
    """)

# ----------------------------
# VISTA: REPORTES INDIVIDUALES
# ----------------------------

elif menu == "👨‍🎓 Reportes Estudiantes":
    st.title("👨‍🎓 Reportes por Estudiante")
    st.write("Selecciona un curso para ver los detalles individuales.")
    st.selectbox("Curso", ["2°ABC-G1", "2°DEF-G1"])
    st.write("Mostrar gráficos individuales de trayectoria de puntajes y clasificaciones.")
