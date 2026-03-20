"""
app.py — EcoTrack: estimates daily CO2 emissions from natural language input.
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd

from parser import parse_activities
from emissions import estimate_emissions, total_co2, co2_context

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="EcoTrack", page_icon="🌱", layout="centered")

# ── Styles ───────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .block-container { max-width: 680px; padding-top: 2rem; }
    .metric-label { font-size: 0.85rem; color: #6b7280; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🌱 EcoTrack")
st.caption("Estima tus emisiones de CO₂ diarias a partir de texto libre.")

st.divider()

# ── Input ────────────────────────────────────────────────────────────────────
PLACEHOLDER = (
    "Ej: Hoy comí carne y viajé 20km en bus. "
    "También fui 5km en bici y almorcé pollo."
)

user_input = st.text_area(
    "¿Qué hiciste hoy?",
    placeholder=PLACEHOLDER,
    height=110,
    label_visibility="visible",
)

calculate = st.button("Calcular emisiones", type="primary", use_container_width=True)

# ── Calculation & results ─────────────────────────────────────────────────────
if calculate:
    if not user_input.strip():
        st.warning("Por favor escribe alguna actividad antes de calcular.")
        st.stop()

    activities = parse_activities(user_input)

    if not activities:
        st.info(
            "No se detectaron actividades reconocidas. "
            "Intenta mencionar alimentos (carne, pollo, verduras…) "
            "o medios de transporte con distancia (20km en bus, auto, avión…)."
        )
        st.stop()

    results = estimate_emissions(activities)
    total = total_co2(results)

    st.divider()

    # ── Summary metric ────────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label="Total CO₂ estimado", value=f"{total} kg")
    with col2:
        st.info(co2_context(total))

    st.divider()

    # ── Breakdown table ───────────────────────────────────────────────────────
    st.subheader("Desglose")

    df = pd.DataFrame(results)[["label", "category", "detail", "co2_kg"]]
    df.columns = ["Actividad", "Categoría", "Detalle", "CO₂ (kg)"]
    df["Categoría"] = df["Categoría"].map({"food": "🍽 Comida", "transport": "🚌 Transporte"})

    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Bar chart ─────────────────────────────────────────────────────────────
    if len(results) > 1:
        st.subheader("Comparativa")
        chart_df = pd.DataFrame(
            {"CO₂ (kg)": [r["co2_kg"] for r in results]},
            index=[r["label"] for r in results],
        )
        st.bar_chart(chart_df)

    # ── Tips ──────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Consejos")

    food_types = {r["label"] for r in results if r["category"] == "food"}
    transport_types = {r["label"] for r in results if r["category"] == "transport"}

    if "Carne de res" in food_types:
        st.write("🥗 Sustituir carne de res por pollo o legumbres puede reducir tus emisiones hasta un 75%.")
    if "Auto / Taxi" in transport_types:
        st.write("🚌 Cambiar el auto por bus o metro reduce emisiones por km hasta 7 veces.")
    if "Avión" in transport_types:
        st.write("✈️ Un vuelo corto puede generar más CO₂ que una semana de alimentación.")
    if total < 2:
        st.write("✅ ¡Buen trabajo! Tus emisiones de hoy están por debajo del promedio diario.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Los factores de emisión son estimaciones promedio. "
    "Fuentes: Our World in Data, IPCC, EEA."
)
