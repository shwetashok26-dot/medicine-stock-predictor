# 💊 AI Medicine Stock Predictor
Track 3: Smart Health & Supply Chain Resilience

## Problem
Clinics and pharmacies often run out of essential medicines because reordering is guesswork, causing patient harm and waste.

## Solution
Upload 6 months of usage per medicine. The app fits a trend-based ML forecast (linear regression) to predict next month's demand, estimates days until stockout, compares it with supplier lead time, and flags Critical / Warning / Safe with a suggested reorder quantity.

## Features
- Demand forecasting per medicine
- Stockout risk alerts based on lead time
- Reorder quantity suggestions
- CSV upload and downloadable report

## Tech stack
Python, Streamlit, Pandas, NumPy

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```

## CSV format
`Medicine, Stock, Lead_Time_Days, M1, M2, M3, M4, M5, M6` (M1 = oldest month)
