import requests
import pandas as pd
from datetime import datetime
import os

URL = "https://www.faza24.ir/api/apiweb/RetrieveAnnouncements?Ipaddress=&Origin=thr"

def get_data():
    r = requests.get(URL, timeout=30)
    r.raise_for_status()
    return r.json()

def process(data):
    df = pd.DataFrame(data)

    # فقط پروازهای خروجی مهرآباد
    df = df[df["Type"].str.contains("خروجی")]

    result = (
        df.groupby("AirlineName")
        .size()
        .reset_index(name="Flights")
        .sort_values("Flights", ascending=False)
    )

    return result

def save_excel(df):
    os.makedirs("reports", exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = f"reports/{date_str}.xlsx"

    df.to_excel(file_path, index=False)

    print(f"Saved: {file_path}")

if __name__ == "__main__":
    data = get_data()
    result = process(data)
    save_excel(result)

    print(result)
