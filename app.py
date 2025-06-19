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
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.markdown("### 📊 Evolución de Niveles de Agua por hora")

# Obtener columnas de predicción horaria
pred_columns = [col for col in df.columns if col.startswith('nivel_predict_')]

if not pred_columns:
    st.warning("No se encontraron columnas de predicción horaria")
    st.stop()

# Convertir y procesar columnas de predicción
for col in pred_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce") * 100

# Obtener horas y valores promedio
horas = sorted([int(col.split('_')[-1]) for col in pred_columns])
valores = df[pred_columns].mean().values

# Índices de máximo y mínimo
max_idx = np.argmax(valores)
min_idx = np.argmin(valores)

# Crear figura
fig = go.Figure()

# Línea de evolución
fig.add_trace(go.Scatter(
    x=horas,
    y=valores,
    mode='lines+markers',
    name='Nivel promedio',
    line=dict(color='#1f77b4', width=3),
    marker=dict(size=8)
))

# Área bajo la curva
fig.add_trace(go.Scatter(
    x=horas + horas[::-1],
    y=list(valores) + [0]*len(valores),
    fill='toself',
    fillcolor='rgba(135, 206, 250, 0.3)',
    line=dict(color='rgba(255,255,255,0)'),
    hoverinfo="skip",
    showlegend=False
))

# Líneas de referencia
fig.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Nivel óptimo (80%)", annotation_position="top left")
fig.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Nivel crítico (30%)", annotation_position="bottom left")

# Puntos destacados
fig.add_trace(go.Scatter(
    x=[horas[max_idx]], 
    y=[valores[max_idx]],
    mode='markers+text',
    marker=dict(color='green', size=10),
    text=["Máximo"],
    textposition="top center",
    name='Máximo'
))
fig.add_trace(go.Scatter(
    x=[horas[min_idx]], 
    y=[valores[min_idx]],
    mode='markers+text',
    marker=dict(color='red', size=10),
    text=["Mínimo"],
    textposition="bottom center",
    name='Mínimo'
))

# Layout sin -1 ni 24
fig.update_layout(
    xaxis=dict(
        title='Hora del Día',
        tickmode='linear',
        dtick=1,
        range=[min(horas), max(horas)]
    ),
    yaxis=dict(title='Nivel Promedio por zona (%)', range=[0, 100]),
    title='Evolución de Niveles de Agua',
    height=450,
    template='plotly_white'
)

# Mostrar el gráfico
st.plotly_chart(fig, use_container_width=True)

# Métricas
st.markdown("### 🔍 Estadísticas importantes")
col1, col2, col3 = st.columns(3)
col1.metric("Hora de máximo nivel", f"{horas[max_idx]}:00", f"{valores[max_idx]:.1f}%")
col2.metric("Hora de mínimo nivel", f"{horas[min_idx]}:00", f"{valores[min_idx]:.1f}%")


# --------------------------------------------
# ℹ️ Información adicional
# --------------------------------------------
st.info(f"""
*Nota sobre los datos:*
- Los datos y estadísticas presentados tienen fines ilustrativos únicamente y no corresponden a información real.
""", icon="ℹ️")