import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_pandas_profiling import st_profile_report
from ydata_profiling import ProfileReport  
from pathlib import Path


# --- Page Configuration ---
st.set_page_config(
    page_title="Live Trading Dashboard",
    page_icon="🚀",
)

# --- Title and Description ---
st.title("Historical Market Data & Predictions")
st.markdown(""" Access real-time historical market data and detailed analytics for your selected stock.
Use the sidebar below to choose a ticker and date range, then click the **'Load Data'** button to see historical data.
""")

# --- Sidebar Inputs ---
tickers = ["AAPL", "MSFT", "AMZN", "TSLA", "META"]
selected_ticker = st.sidebar.selectbox("Select Stock Ticker", tickers)
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.Timestamp.today())

# --- Load Data Button ---
if st.sidebar.button("Load Data"):
    # --- Load Dataset ---
    # --- Define the Path to Your Data File ---
    BASE_DIR = Path(__file__).resolve().parent.parent  # Two levels up from 'pages/' to the root folder

    merged_data_path = BASE_DIR / "data" / "merged_data.csv"

    # --- Load the Dataset Safely ---
    if merged_data_path.exists():
        df = pd.read_csv(merged_data_path, parse_dates=["Date"])
        st.write(df.head())  # Display the data to confirm it's loaded correctly
    else:
        st.error(f"File not found: {merged_data_path}")

    # --- Filter Dataset ---
    df_filtered = df[
        (df["Ticker"] == selected_ticker) & 
        (df["Date"] >= pd.to_datetime(start_date)) & 
        (df["Date"] <= pd.to_datetime(end_date))
    ]

    # --- Display Summary Metrics for the Selected Ticker ---
    st.subheader(f"Closing Price Metrics for {selected_ticker}")

    if df_filtered.empty:
        st.warning(f"No data available for {selected_ticker}.")
    else:
        # Calculate metrics for the 'Close' price from the filtered data
        low_price = df_filtered["Close"].min()
        high_price = df_filtered["Close"].max()
        mean_price = df_filtered["Close"].mean()

        # Calculate deltas relative to the mean
        delta_low = low_price - mean_price    # Expected to be negative
        delta_high = high_price - mean_price  # Expected to be positive

        # Create three columns for Low, Mean, and High
        col1, col2, col3 = st.columns(3)
        col1.metric(
            label="Low", 
            value=f"${low_price:.2f}", 
            delta=f"${delta_low:.2f}", 
            delta_color="inverse",  # negative delta in green
            border=True
        )
        col2.metric(
            label="Mean", 
            value=f"${mean_price:.2f}", 
            border=True
        )
        col3.metric(
            label="High", 
            value=f"${high_price:.2f}", 
            delta=f"${delta_high:.2f}",
            border=True
        )

        # --- Stock Price Chart ---
        st.subheader("Stock Price Chart")
        fig = px.line(
            df_filtered, 
            x="Date", 
            y="Close", 
            title=f"{selected_ticker} Closing Prices Over Time", 
            labels={"Date": "Date", "Close": "Closing Price ($)"}
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Closing Price ($)",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

BASE_DIR = Path(__file__).resolve().parent.parent  # Moves two levels up from pages/ to the root folder

# Define the path to your CSV file
ml_predictions_path = BASE_DIR / "data" / "ml_predictions_2.csv"

# Check if the file exists
if ml_predictions_path.exists():
    df_preds = pd.read_csv(ml_predictions_path, parse_dates=["Date"])
else:
    st.error(f"File not found: {ml_predictions_path}")

st.subheader("Predicted vs Actual Closing Price")

st.markdown("""
Here choose a ticker and you will see a graph comparing the actual closing prices versus the predicted ones from our
            proprietary Machine Learning model.
""")

# --- User Selection ---
selected_ticker = st.selectbox("Select a Ticker", sorted(df_preds["Ticker"].unique()))

# --- Filter ML Predictions ---
df_preds_filtered = df_preds[df_preds["Ticker"] == selected_ticker]

fig = px.line(
    df_preds_filtered,
    x="Date",
    y=["Close", "Predicted_Close"],
    title=f"{selected_ticker} Actual vs Predicted Closing Prices",
    labels={"Date": "Date", "value": "Closing Price ($)", "variable": "Legend"}
)
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Closing Price ($)",
    template="plotly_white"
)
st.plotly_chart(fig, use_container_width=True)
