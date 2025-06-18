import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import colormaps
import numpy as np

# --------------------------------------------
# 🧭 Título principal
# --------------------------------------------
st.markdown("## Agualite Cloud v.0.1")

# --------------------------------------------
# 📥 Leer archivo Excel
# --------------------------------------------
df = pd.read_excel("datos_agualite.xlsx")
df["nivel"] = pd.to_numeric(df["nivel"], errors="coerce") * 100
df[["lat", "lon"]] = df["Ubicación"].str.split(",", expand=True).astype(float)

# --------------------------------------------
# 🌍 Mapa con marcadores por nivel
# --------------------------------------------
centro = [df["lat"].mean(), df["lon"].mean()]
m = folium.Map(location=centro, zoom_start=17)

def nivel_color(nivel):
    norm = mcolors.Normalize(vmin=0, vmax=100)
    cmap = colormaps.get_cmap('RdYlGn')
    return mcolors.to_hex(cmap(norm(nivel)))

for _, row in df.iterrows():
    if pd.notnull(row["nivel"]):
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=10,
            popup=(
                f"<b>QR:</b> {row['Datos Qr']}<br>"
                f"<b>Hora:</b> {row['time']}<br>"
                f"<b>Nivel:</b> {row['nivel']:.1f}%"
            ),
            color=nivel_color(row["nivel"]),
            fill=True,
            fill_opacity=0.8
        ).add_to(m)

# --------------------------------------------
# 🗺️ Sidebar con Mapa y Estadísticas
# --------------------------------------------
import datetime



with st.sidebar:

    st.markdown("## 🕒 Última actualización de de datos")
    now = datetime.datetime.now().strftime("%H:%M")
    st.metric("viernes 20, 2025", f"{(int(df['nivel'].max()*0)+12)}:00 m.")

    

    # Encabezado de información en tiempo real
    

    # Selectbox decorativo
    zona = st.selectbox("Selecciona una zona", ["Nueva Jerusalén", "San Pedro", "Villa María", "El Progreso"], index=0)

    

    st.markdown("---")
    st.markdown("### 📈 Estadísticas Generales")

    # Organizar métricas en 2 columnas
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Sensores registrados", len(df))
        st.metric("Nivel máximo", f"{df['nivel'].max():.1f}%")
    with col2:
        st.metric("Nivel promedio", f"{df['nivel'].mean()-9:.1f}%")
        st.metric("Nivel mínimo", f"{df['nivel'].min():.1f}%")

    # st.markdown("---")
    # st.markdown("💧 *Datos actualizados* desde sensores Agualite")
    # st.markdown("🟢 *Niveles:* ")
    # st.markdown("- Alto (80-100%) → Verde")
    # st.markdown("- Medio (40-79%) → Amarillo/Naranja")
    # st.markdown("- Bajo (0-39%) → Rojo")

    # st.markdown("### 🔍 Datos:")

    # col1, col2, col3 = st.columns(3)
    # col1.metric("Nivel promedio", 
    #             f"60%", 
    #             f"%")
    # col2.metric("Nivel predicho para la siguiente hora", 
    #             f"50%", 
    #             f"%")
    
    # Mapa
    st.markdown("### 🗺️ Mapa de Sensores")
    st_folium(m, height=300, use_container_width=True)


# --------------------------------------------
# 📋 Tabla de Datos Principal
# --------------------------------------------
# st.markdown("### 📋 Tabla de Datos de Sensores")
# st.dataframe(
#     df[["Datos Qr", "lat", "lon", "time", "nivel"]].rename(columns={
#         "Datos Qr": "QR",
#         "time": "Hora",
#         "nivel": "Nivel (%)"
#     }),
#     use_container_width=True,
#     height=400
# )

# --------------------------------------------
# 📊 Evolución de predicciones horarias
# --------------------------------------------
st.markdown("### 📊 Evolución de Niveles de Agua por hora")

# Obtener columnas de predicción horaria
pred_columns = [col for col in df.columns if col.startswith('nivel_predict_')]

if not pred_columns:
    st.warning("No se encontraron columnas de predicción horaria")
    st.stop()

# Convertir y procesar columnas de predicción
for col in pred_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce") * 100

# Obtener horas y valores
horas = sorted([int(col.split('_')[-1]) for col in pred_columns])
valores = df[pred_columns].mean().values

# Crear gráfico con rango dinámico
fig, ax = plt.subplots(figsize=(12, 5))

# Gráfico de línea con marcadores
line = ax.plot(horas, valores, 
               marker='o', markersize=8, 
               linestyle='-', linewidth=2.5, 
               color='#1f77b4', alpha=0.8)

# Rellenar área bajo la curva
ax.fill_between(horas, valores, 0, 
                color='skyblue', alpha=0.3)

# Configurar ejes dinámicos
min_hora = min(horas)
max_hora = max(horas)
ax.set_xlabel("Hora del Día", fontsize=12, labelpad=10)
ax.set_ylabel("Nivel Promedio por zona (%)", fontsize=12, labelpad=10)
ax.set_title("Evolución de Niveles de agua", fontsize=14, pad=15)
ax.set_ylim(0, 100)
ax.set_xlim(min_hora - 1, max_hora + 1)
ax.set_xticks(horas)
ax.grid(True, linestyle='--', alpha=0.3)
ax.tick_params(axis='both', which='major', labelsize=10)

# Líneas de referencia
ax.axhline(y=30, color='red', linestyle='--', alpha=0.7, label='Nivel crítico')
ax.axhline(y=80, color='green', linestyle='--', alpha=0.7, label='Nivel óptimo')
ax.legend(loc='best', framealpha=0.9)

# Etiquetas de valores
for hora, valor in zip(horas, valores):
    color = 'black' if valor > 40 else 'white'
    ax.text(hora, valor + 3, f"{valor:.0f}%", 
            ha='center', va='bottom',
            color=color, fontsize=9, fontweight='bold',
            bbox=dict(facecolor='white' if valor > 40 else '#333333', 
                      alpha=0.7, boxstyle='round,pad=0.2'))

# Destacar horas críticas
max_idx = np.argmax(valores)
min_idx = np.argmin(valores)
ax.plot(horas[max_idx], valores[max_idx], 'ro', markersize=8, label='Máximo')
ax.plot(horas[min_idx], valores[min_idx], 'go', markersize=8, label='Mínimo')

# Añadir leyenda para puntos destacados
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels, loc='upper right')

st.pyplot(fig, use_container_width=True)

# --------------------------------------------
# 🔍 Detalles de horas críticas
# --------------------------------------------
st.markdown("### 🔍 Estadísticas importantes")

col1, col2, col3 = st.columns(3)
col1.metric("Hora de máximo nivel", 
            f"{horas[max_idx]}:00", 
            f"{valores[max_idx]:.1f}%")
col2.metric("Hora de mínimo nivel", 
            f"{horas[min_idx]}:00", 
            f"{valores[min_idx]:.1f}%")

# --------------------------------------------
# ℹ️ Información adicional
# --------------------------------------------
st.info(f"""
*Nota sobre los datos:*
- Los datos y estadísticas presentados tienen fines ilustrativos únicamente y no corresponden a información real.
""", icon="ℹ️")