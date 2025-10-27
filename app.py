# app.py
import os
import streamlit as st
import pandas as pd
import subprocess
import sys

# -----------------------
# CONFIGURACIÓN INICIAL
# -----------------------
st.set_page_config(page_title="Tabla Interactiva (solo emojis)", layout="wide")
st.title("📊 Tabla interactiva — solo emojis")
st.markdown(
    "La app lee el archivo local **'PRUEBAS MOVILIDAD.xlsx'** (debe estar en la misma carpeta que `app.py`). "
    "No hay opción para subir archivos en la interfaz (ideal para link público)."
)

# -----------------------
# Ruta del archivo local
# -----------------------
EXCEL_FILENAME = "PRUEBAS MOVILIDAD.xlsx"

# -----------------------
# FUNCIONES
# -----------------------
def asegurar_openpyxl():
    """Verifica si openpyxl está instalado; si no, lo instala automáticamente."""
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        st.warning("No encontré 'openpyxl', instalando automáticamente...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
        st.success("openpyxl instalado correctamente. Recarga la página.")
        st.stop()

def cargar_excel(path):
    """Lee el Excel y devuelve un DataFrame o None si hay error."""
    asegurar_openpyxl()
    try:
        df = pd.read_excel(path, engine="openpyxl")
        return df
    except Exception as e:
        st.error(f"No pude leer '{path}': {e}")
        return None

def solo_emojis(df):
    """
    Reemplaza los valores numéricos por emojis según umbrales.
    Devuelve un DataFrame con SOLO las columnas deseadas (sin valores numéricos),
    pero manteniendo columnas de identificación como JUGADOR, ID, NOMBRE, etc.
    """
    df_e = df.copy()
    reglas = {
        "THOMAS PSOAS (D)": 10,
        "THOMAS PSOAS (I)": 10,
        "THOMAS CUADRICEPS (D)": 50,
        "THOMAS CUADRICEPS (I)": 50,
        "THOMAS SARTORIO (D)": 80,
        "THOMAS SARTORIO (I)": 80,
        "JURDAN (D)": 75,
        "JURDAN (I)": 75
    }

    for c in reglas.keys():
        if c in df_e.columns:
            df_e[c] = pd.to_numeric(df_e[c], errors="coerce")

    for col, umbral in reglas.items():
        if col in df_e.columns:
            df_e[col] = df_e[col].apply(
                lambda v: "🟢👍" if pd.notna(v) and v > umbral else ("🔴👎" if pd.notna(v) else "")
            )

    mostrar = []

    id_columns = ["JUGADOR", "ID", "NOMBRE", "APELLIDO", "NOMBRE_COMPLETO", "NOMBRE Y APELLIDO", "NOMBRE_APELLIDO"]
    for col in id_columns:
        if col in df_e.columns and col not in mostrar:
            mostrar.append(col)

    if "CATEGORÍA" in df_e.columns and "CATEGORÍA" not in mostrar:
        mostrar.insert(0, "CATEGORÍA")

    for col in reglas.keys():
        if col in df_e.columns:
            mostrar.append(col)

    if not mostrar:
        mostrar = df_e.columns.tolist()

    if "CATEGORÍA" not in df_e.columns:
        st.warning("No encontré la columna 'CATEGORÍA'. Se mostrarán todos los registros (sin filtro).")
        cols_existentes = [c for c in mostrar if c in df_e.columns]
        return df_e.loc[:, cols_existentes] if cols_existentes else df_e

    cols_existentes = [c for c in mostrar if c in df_e.columns]
    return df_e.loc[:, cols_existentes]

def altura_segura(num_filas, min_h=120, max_h=1200, row_px=30, header_px=40):
    h = header_px + num_filas * row_px
    if h < min_h:
        return min_h
    if h > max_h:
        return max_h
    return h

# -----------------------
# LÓGICA PRINCIPAL
# -----------------------

if not os.path.exists(EXCEL_FILENAME):
    st.error(f"No encontré el archivo local '{EXCEL_FILENAME}'. Colócalo en la misma carpeta que app.py y vuelve a ejecutar.")
    st.stop()

df_raw = cargar_excel(EXCEL_FILENAME)
if df_raw is None:
    st.stop()

df_emojis = solo_emojis(df_raw)

if "CATEGORÍA" in df_emojis.columns:
    categorias_raw = df_emojis["CATEGORÍA"].dropna().astype(str)
    categorias_unicas = sorted(categorias_raw.unique().tolist())
    categorias = ["Todas"] + categorias_unicas
    seleccion = st.selectbox("🔎 Filtrar por CATEGORÍA", categorias)
    if seleccion != "Todas":
        df_mostrar = df_emojis[df_emojis["CATEGORÍA"].astype(str) == seleccion].copy()
    else:
        df_mostrar = df_emojis.copy()
else:
    df_mostrar = df_emojis.copy()

num_filas = len(df_mostrar)
height_px = altura_segura(num_filas)
st.markdown(f"**Registros mostrados:** {num_filas}")
st.dataframe(df_mostrar.reset_index(drop=True), use_container_width=True, height=height_px)

if st.button("🔄 Refrescar datos (releer archivo local)"):
    st.experimental_rerun()

st.info("Para que el link público funcione sin uploader, sube 'PRUEBAS MOVILIDAD.xlsx' al repositorio junto con app.py y requirements.txt.")

