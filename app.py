# app.py
import os
import streamlit as st
import pandas as pd

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
EXCEL_FILENAME = "PRUEBAS MOVILIDAD.xlsx"  # Asegúrate que este archivo esté en la misma carpeta que app.py

# -----------------------
# FUNCIONES
# -----------------------
def cargar_excel(path):
    """Lee el Excel y devuelve un DataFrame o None si hay error."""
    try:
        df = pd.read_excel(path)
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

    # Convertir numéricos (int/float) si vienen como texto para las columnas de regla
    for c in reglas.keys():
        if c in df_e.columns:
            df_e[c] = pd.to_numeric(df_e[c], errors="coerce")

    # Reemplazar por emojis de color (solo emoji, sin número)
    for col, umbral in reglas.items():
        if col in df_e.columns:
            df_e[col] = df_e[col].apply(
                lambda v: "🟢👍" if pd.notna(v) and v > umbral else ("🔴👎" if pd.notna(v) else "")
            )

    # Seleccionar columnas a mostrar:
    mostrar = []

    # Priorizar columnas de identificación que quieras siempre ver (incluye JUGADOR)
    id_columns = ["JUGADOR", "ID", "NOMBRE", "APELLIDO", "NOMBRE_COMPLETO", "NOMBRE Y APELLIDO", "NOMBRE_APELLIDO"]
    for col in id_columns:
        if col in df_e.columns and col not in mostrar:
            mostrar.append(col)

    # Aseguramos que CATEGORÍA esté al comienzo si existe
    if "CATEGORÍA" in df_e.columns and "CATEGORÍA" not in mostrar:
        mostrar.insert(0, "CATEGORÍA")

    # Añadir las columnas emoji en el orden deseado
    for col in reglas.keys():
        if col in df_e.columns:
            mostrar.append(col)

    # Si no hay columnas identificadas, al menos mostramos las que tenemos
    if not mostrar:
        mostrar = df_e.columns.tolist()

    # Si CATEGORÍA no existe, avisar y devolver lo que haya
    if "CATEGORÍA" not in df_e.columns:
        st.warning("No encontré la columna 'CATEGORÍA'. Se mostrarán todos los registros (sin filtro).")
        # Devolver las columnas calculadas en 'mostrar' si existen
        cols_existentes = [c for c in mostrar if c in df_e.columns]
        return df_e.loc[:, cols_existentes] if cols_existentes else df_e

    # Devolver DataFrame con el orden de columnas seleccionado
    cols_existentes = [c for c in mostrar if c in df_e.columns]
    return df_e.loc[:, cols_existentes]


def altura_segura(num_filas, min_h=120, max_h=1200, row_px=30, header_px=40):
    """
    Calcula una altura adecuada en píxeles para st.dataframe
    """
    h = header_px + num_filas * row_px
    if h < min_h:
        return min_h
    if h > max_h:
        return max_h
    return h


# -----------------------
# LÓGICA PRINCIPAL
# -----------------------

# 1) Verificar existencia del archivo local
if not os.path.exists(EXCEL_FILENAME):
    st.error(f"No encontré el archivo local '{EXCEL_FILENAME}'. Colócalo en la misma carpeta que app.py y vuelve a ejecutar.")
    st.stop()

# 2) Cargar datos
df_raw = cargar_excel(EXCEL_FILENAME)
if df_raw is None:
    st.stop()

# 3) Convertir a solo emojis (y seleccionar columnas a mostrar)
df_emojis = solo_emojis(df_raw)

# 4) Filtrado por CATEGORÍA (si existe)
if "CATEGORÍA" in df_emojis.columns:
    # Convertir todas las categorías a texto antes de ordenar para evitar TypeError
    categorias_raw = df_emojis["CATEGORÍA"].dropna().astype(str)
    categorias_unicas = sorted(categorias_raw.unique().tolist())
    categorias = ["Todas"] + categorias_unicas
    seleccion = st.selectbox("🔎 Filtrar por CATEGORÍA", categorias)
    if seleccion != "Todas":
        # Comparar como string para mayor robustez
        df_mostrar = df_emojis[df_emojis["CATEGORÍA"].astype(str) == seleccion].copy()
    else:
        df_mostrar = df_emojis.copy()
else:
    df_mostrar = df_emojis.copy()

# 5) Mostrar tabla con altura ajustada y sin área gris sobrante
num_filas = len(df_mostrar)
height_px = altura_segura(num_filas)
st.markdown(f"**Registros mostrados:** {num_filas}")
st.dataframe(df_mostrar.reset_index(drop=True), use_container_width=True, height=height_px)

# 6) Botón manual para refrescar (releer archivo)
if st.button("🔄 Refrescar datos (releer archivo local)"):
    st.experimental_rerun()

# 7) Nota sobre despliegue
st.info("Para que el link público funcione sin uploader, sube 'PRUEBAS MOVILIDAD.xlsx' al repositorio junto con app.py y requirements.txt.")
