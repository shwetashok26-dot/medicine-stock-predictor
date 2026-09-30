import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Medicine Stock Predictor", page_icon="💊", layout="wide")
st.title("💊 AI Medicine Stock Predictor")
st.caption("Predict which medicines will run out and get reorder alerts. Track 3: Smart Health & Supply Chain Resilience")

SAMPLE = pd.DataFrame({
    "Medicine": ["Paracetamol", "Amoxicillin", "ORS Sachets", "Insulin", "Metformin", "Cetirizine", "Azithromycin", "Vitamin D3"],
    "Stock": [900, 250, 400, 60, 700, 500, 180, 600],
    "Lead_Time_Days": [7, 10, 5, 14, 7, 7, 10, 7],
    "M1": [300, 120, 150, 30, 200, 90, 60, 100],
    "M2": [320, 140, 170, 32, 205, 95, 70, 105],
    "M3": [350, 160, 210, 35, 210, 92, 85, 100],
    "M4": [380, 190, 260, 38, 212, 98, 100, 110],
    "M5": [420, 220, 330, 42, 215, 96, 120, 108],
    "M6": [460, 260, 420, 47, 220, 100, 150, 112],
})

st.sidebar.header("Your data")
file = st.sidebar.file_uploader("Upload CSV (optional)", type="csv")
st.sidebar.caption("Columns: Medicine, Stock, Lead_Time_Days, M1..M6 (last 6 months usage, oldest to newest)")
horizon = st.sidebar.slider("Cover target (months of stock)", 1, 4, 2)
df = pd.read_csv(file) if file else SAMPLE.copy()
if not file:
    st.info("Showing sample data. Upload your own CSV from the sidebar.")

months = [c for c in df.columns if c.startswith("M")]

def forecast(row):
    y = row[months].astype(float).values
    x = np.arange(len(y))
    slope, intercept = np.polyfit(x, y, 1)  # linear trend model
    nxt = max(0.0, slope * len(y) + intercept)
    daily = max(nxt / 30, 0.001)
    days_left = row["Stock"] / daily
    lead = row["Lead_Time_Days"]
    if days_left < lead:
        risk = "🔴 Critical"
    elif days_left < lead + 14:
        risk = "🟠 Warning"
    else:
        risk = "🟢 Safe"
    reorder = max(0, int(np.ceil(nxt * horizon - row["Stock"])))
    trend = "Rising ↑" if slope > 1 else ("Falling ↓" if slope < -1 else "Stable →")
    return pd.Series({"Next Month Demand": int(nxt), "Days Left": round(days_left, 1),
                      "Trend": trend, "Risk": risk, "Reorder Qty": reorder})

result = pd.concat([df[["Medicine", "Stock", "Lead_Time_Days"]], df.apply(forecast, axis=1)], axis=1)
order = {"🔴 Critical": 0, "🟠 Warning": 1, "🟢 Safe": 2}
result = result.sort_values("Risk", key=lambda s: s.map(order)).reset_index(drop=True)

c1, c2, c3 = st.columns(3)
c1.metric("Critical", int((result.Risk == "🔴 Critical").sum()))
c2.metric("Warning", int((result.Risk == "🟠 Warning").sum()))
c3.metric("Safe", int((result.Risk == "🟢 Safe").sum()))

st.subheader("Stock risk & reorder alerts")
st.dataframe(result, use_container_width=True, hide_index=True)

urgent = result[result.Risk != "🟢 Safe"]
if len(urgent):
    st.error("Reorder now: " + ", ".join(f"{r.Medicine} ({r['Reorder Qty']} units)" for _, r in urgent.iterrows()))

st.subheader("Demand forecast")
pick = st.selectbox("Choose a medicine", df["Medicine"])
row = df[df.Medicine == pick].iloc[0]
hist = list(row[months].astype(float))
pred = result[result.Medicine == pick]["Next Month Demand"].iloc[0]
chart = pd.DataFrame({"Usage": hist + [None], "Forecast": [None] * (len(hist) - 1) + [hist[-1], pred]},
                     index=[f"M{i+1}" for i in range(len(hist))] + ["Next"])
st.line_chart(chart)

st.download_button("Download report (CSV)", result.to_csv(index=False), "stock_report.csv")
