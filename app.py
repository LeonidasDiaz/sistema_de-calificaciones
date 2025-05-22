import streamlit as st
import pandas as pd
import os
import time
from io import BytesIO

# ================================
# Configuración inicial de la app
# ================================
st.set_page_config(page_title="Asignación de Materias Faltantes", layout="wide")
st.title("Sistema de Asignación de Materias")

# ================================
# Funciones auxiliares
# ================================

# Cuenta cuántas materias ha cursado un estudiante en una lista de materias dada
def contar_materias_cursadas(row, materias):
    return sum(pd.notna(row[mat]) and row[mat] != "EQ" and row[mat] != 5 for mat in materias)

# Retorna una lista de materias faltantes priorizando:
# 1. Pregrado, 2. Institucionales, 3. Fundamentales
def obtener_materias_faltantes(row, max_materias):
    faltantes = []

    # Contar materias ya cursadas por tipo
    pregrado_cursadas = contar_materias_cursadas(row, pregrado)
    institucionales_cursadas = contar_materias_cursadas(row, institucionales)

    # Inicializar contadores para este semestre
    pregrado_asignadas = 0
    institucionales_asignadas = 0

    # Paso 1: Prioridad pregrado
    for mat in seleccion_pregrado_cols:
        if pd.isna(row[mat]) and (pregrado_cursadas + pregrado_asignadas < 5):
            faltantes.append(f"Pregrado: {mat[1]}")
            pregrado_asignadas += 1
        if len(faltantes) == max_materias:
            return faltantes

    # Paso 2: Prioridad institucionales
    for mat in seleccion_institucionales_cols:
        if pd.isna(row[mat]) and (institucionales_cursadas + institucionales_asignadas < 3):
            faltantes.append(f"Institucional: {mat[1]}")
            institucionales_asignadas += 1
        if len(faltantes) == max_materias:
            return faltantes

    # Paso 3: Completar con fundamentales
    for mat in fundamentales:
        if pd.isna(row[mat]):
            faltantes.append(f"Fundamental: {mat[1]}")
        if len(faltantes) == max_materias:
            return faltantes

    return faltantes

# Muestra advertencias si el estudiante ya alcanzó su límite o ya cursó alguna materia seleccionada
def mostrar_advertencias(fila):
    pregrado_cursadas = contar_materias_cursadas(fila, pregrado)
    institucionales_cursadas = contar_materias_cursadas(fila, institucionales)

    if pregrado_cursadas >= 5:
        st.warning("⚠️ Ya alcanzó el límite de materias de pregrado (5).")
    if institucionales_cursadas >= 3:
        st.warning("⚠️ Ya alcanzó el límite de materias institucionales (3).")

    # Verificar si ya cursó alguna de las seleccionadas
    for mat in seleccion_pregrado_cols:
        valor = fila[mat]
        if pd.notna(valor) and valor != "EQ" and valor != 5:
            st.warning(f"⚠️ Ya cursó la materia de pregrado: {mat[1]}")

    for mat in seleccion_institucionales_cols:
        valor = fila[mat]
        if pd.notna(valor) and valor != "EQ" and valor != 5:
            st.warning(f"⚠️ Ya cursó la materia institucional: {mat[1]}")

# ================================
# Subida del archivo Excel
# ================================
archivo = st.file_uploader("Sube el archivo Excel con el historial académico", type=["xlsx"])

if archivo:
    # Leer el archivo con encabezado multinivel
    df = pd.read_excel(archivo, header=[0, 1])

    # ================================
    # Sección de parámetros del sidebar
    # ================================
    st.sidebar.header("Parámetros de selección")

    # Selección del semestre y máximo de materias según el mismo
    semestre = st.sidebar.selectbox("Selecciona el semestre del estudiante:", list(range(1, 9)), index=7)
    max_materias = 7 if semestre in [1, 2] else 6

    # Filtrar estudiantes por semestre
    df_filtrado = df[df[("Tipo de Ingreso", "Normal")] == semestre].copy()

    # Separar columnas según el tipo de materia
    fundamentales = [col for col in df.columns if col[0] == "Asignaturas del Area Fundamental"]
    pregrado = [col for col in df.columns if col[0] == "Asignaturas del Area Pregrado"]
    institucionales = [col for col in df.columns if col[0] == "Asignaturas del Area Institucional"]

    # Selección de materias que se abrirán este semestre
    seleccion_pregrado = st.sidebar.multiselect(
        "Selecciona materias de pregrado que se abrirán este semestre:",
        options=[mat[1] for mat in pregrado]
    )
    seleccion_pregrado_cols = [mat for mat in pregrado if mat[1] in seleccion_pregrado]

    seleccion_institucionales = st.sidebar.multiselect(
        "Selecciona materias institucionales que se abrirán este semestre:",
        options=[mat[1] for mat in institucionales]
    )
    seleccion_institucionales_cols = [mat for mat in institucionales if mat[1] in seleccion_institucionales]

    # ================================
    # Cálculo de materias faltantes
    # ================================
    df_filtrado["Materias Faltantes"] = df_filtrado.apply(
        lambda row: obtener_materias_faltantes(row, max_materias), axis=1
    )

    # ================================
    # Visualización de resultados
    # ================================
    st.subheader("Resultados")
    st.write(f"Listado de materias faltantes por alumno (máx {max_materias}):")

    for _, fila in df_filtrado.iterrows():
        nombre = fila[('Nombre', 'Unnamed: 3_level_1')]
        matricula = fila[('Matricula', 'Unnamed: 2_level_1')]
        st.markdown(f"**{nombre} ({matricula})**")

        mostrar_advertencias(fila)

        for i, mat in enumerate(fila["Materias Faltantes"], start=1):
            st.write(f"{i}. {mat}")
        st.markdown("---")

    # ================================
    # Exportación de resultados
    # ================================
    # Expandir materias faltantes en columnas individuales
    faltantes_expandidas = df_filtrado["Materias Faltantes"].apply(
        lambda x: pd.Series(x, index=[f"Materia {i+1}" for i in range(len(x))])
    )

    # Seleccionar columnas básicas para exportar
    columnas_basicas = [
        ("No.", "Unnamed: 0_level_1"),
        ("Matricula", "Unnamed: 2_level_1"),
        ("Nombre", "Unnamed: 3_level_1"),
        ("Tipo de Ingreso", "Normal")
    ]

    # Combinar con materias faltantes
    df_export = pd.concat([df_filtrado[columnas_basicas], faltantes_expandidas], axis=1)

    # Guardar en un archivo Excel temporal
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_export.to_excel(writer, index=False, sheet_name="Materias Faltantes")
    output.seek(0)

    # Botón de descarga
    st.download_button(
        label="📥 Descargar Concentrado de Asignaciones",
        data=output,
        file_name=f"materias_faltantes_semestre_{semestre}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ================================
# Botón para cerrar la app
# ================================
if st.button("Salir"):
    st.success("Cerrando la aplicación... puedes cerrar esta pestaña del navegador.")
    # Redirige a Google como "pantalla final"
    st.markdown("<meta http-equiv='refresh' content='0; url=https://www.google.com'>", unsafe_allow_html=True)
    # Espera para que se vea el mensaje antes de cerrar
    time.sleep(1.5)
    os._exit(0)
