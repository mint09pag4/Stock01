import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

st.set_page_config(page_title="Data Forecasting Analyzer", layout="wide")
st.title("📊 Excel Data Analyzer & Forecasting Checker")

# --- SIDEBAR: STOCK DATA GENERATOR ---
st.sidebar.header("🚀 Stock Data Generator")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL, MSFT, TSLA)", value="AAPL")

if st.sidebar.button("Fetch 5-Year Stock Data"):
    with st.sidebar:
        with st.spinner("Fetching data..."):
            try:
                stock_df = yf.Ticker(ticker).history(period="5y").reset_index()
                stock_df['Date'] = stock_df['Date'].dt.date
                stock_df = stock_df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
                
                # Convert to Excel bytes so user can download it
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    stock_df.to_excel(writer, index=False, sheet_name='Data')
                processed_data = output.getvalue()
                
                st.success(f"Loaded {ticker} Data!")
                st.download_button(
                    label=f"📥 Download {ticker} Excel File",
                    data=processed_data,
                    file_name=f"{ticker}_5year_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Error fetching ticker: {e}")

# --- MAIN APP: FILE UPLOADER & ANALYZER ---
st.write("Upload an Excel file to analyze numerical columns, view histograms, and check if the data is ready for forecasting.")
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("File uploaded successfully!")
        
        with st.expander("👀 View Raw Data Preview"):
            st.dataframe(df.head())

        numerical_cols = df.select_dtypes(include=['number']).columns.tolist()

        if not numerical_cols:
            st.warning("No numerical columns found in the uploaded Excel file.")
        else:
            st.subheader("📈 Statistical Analysis & Histograms")
            
            for col in numerical_cols:
                st.write(f"---")
                st.markdown(f"### Column: **{col}**")
                
                mean_val = df[col].mean()
                median_val = df[col].median()
                
                col1, col2 = st.columns(2)
                col1.metric(label="Mean", value=f"{mean_val:.2f}")
                col2.metric(label="Median", value=f"{median_val:.2f}")
                
                if median_val != 0:
                    percentage_diff = abs(mean_val - median_val) / abs(median_val)
                else:
                    percentage_diff = abs(mean_val - median_val)

                if percentage_diff <= 0.05:
                    st.success("✅ The mean and median are close. **The data can be used for forecasting.**")
                else:
                    st.info("⚠️ The mean and median have a notable variance. This data might have skewness/outliers.")

                fig, ax = plt.subplots(figsize=(7, 3))
                ax.hist(df[col].dropna(), bins=20, color='skyblue', edgecolor='black', alpha=0.7)
                ax.axvline(mean_val, color='red', linestyle='dashed', linewidth=1.5, label=f'Mean: {mean_val:.2f}')
                ax.axvline(median_val, color='green', linestyle='dashed', linewidth=1.5, label=f'Median: {median_val:.2f}')
                ax.set_title(f'Histogram of {col}')
                ax.set_xlabel('Value')
                ax.set_ylabel('Frequency')
                ax.legend()
                
                st.pyplot(fig)
                
    except Exception as e:
        st.error(f"Error processing the file: {e}")
