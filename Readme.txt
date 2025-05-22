# 🎓 Sistema de Asignación de Materias Faltantes

Aplicación desarrollada en **Python con Streamlit** que permite al coordinador académico subir un archivo Excel con los historiales de los alumnos y determinar qué materias les faltan por cursar, respetando límites por tipo de materia y semestre.

---

## 📌 Funcionalidades principales

- Carga de archivo Excel con doble nivel de encabezado.
- Filtro por semestre.
- Selección de materias de **pregrado** e **institucionales** a abrir este semestre.
- Lógica automática para asignar materias faltantes, priorizando:
  1. Pregrado seleccionadas (máx 5 en toda la carrera).
  2. Institucionales seleccionadas (máx 3 en toda la carrera).
  3. Fundamentales faltantes.
- Descarga del resultado en un archivo Excel.
- Advertencias si un alumno ya ha cursado una materia seleccionada o ha alcanzado su límite.

---

## 🛠️ Requisitos

- Python 3.8+
- Paquetes:
  - `streamlit`
  - `pandas`
  - `openpyxl`
  - `xlsxwriter`

---

## 🚀 Instalación

### 1. Clonar el repositorio (opcional)
```bash
git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
