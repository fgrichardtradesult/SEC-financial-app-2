import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="SEC Income Statement Viewer", layout="centered")

st.title("🔍 SEC Income Statement Explorer")
cik = st.text_input("Enter a CIK number (e.g., 0000320193 for Apple)", value="0000320193")

def fetch_income_statement(cik: str):
    cik = cik.zfill(10)
    headers = {"User-Agent": "Mozilla/5.0 (Streamlit app educational example)"}
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response = requests.get(url, headers=headers)
    if not response.ok:
        return pd.DataFrame([{"Error": "Unable to fetch data from SEC API"}])
    
    data = response.json()
    us_gaap_facts = data.get("facts", {}).get("us-gaap", {})

    keywords = ["Revenue", "Sales", "Income", "Loss", "Expenses", "Profit", "Cost", "Tax"]
    results = []
    
    for tag, content in us_gaap_facts.items():
        if any(k.lower() in tag.lower() for k in keywords):
            for item in content.get("units", {}).get("USD", []):
                if "end" in item and item.get("form") in ["10-Q", "10-K"]:
                    results.append({
                        "Tag": tag,
                        "Value": item.get("val"),
                        "End Date": item.get("end"),
                        "Form": item.get("form"),
                        "FY": item.get("fy", ""),
                        "Quarter": item.get("fp", ""),
                        "Accession": item.get("accn", "")
                    })
                    break  # Only latest per tag

    df = pd.DataFrame(results)
    if not df.empty:
        latest_date = df["End Date"].max()
        df = df[df["End Date"] == latest_date]
        df = df.sort_values(by="Tag")
    return df

if cik:
    with st.spinner("Fetching data from SEC..."):
        df = fetch_income_statement(cik)
        if df.empty:
            st.warning("No income statement data found for this CIK.")
        else:
            st.success(f"Income Statement Data for filing ending {df['End Date'].iloc[0]}")
            st.dataframe(df, use_container_width=True)
