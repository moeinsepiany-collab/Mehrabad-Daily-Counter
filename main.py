import requests
import pandas as pd
from datetime import datetime
import os

from config import API_URL

def fetch_flights():
    params = {
        "Ipaddress": "",
        "Origin": "thr"
    }
    
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def process_departures(data):
    # پیدا کردن لیست اعلامیه‌ها (Announcements)
    announcements = data.get("Announcements", []) if isinstance(data, dict) else data
    
    flights = []
    for ann in announcements:
        # فیلتر فقط پروازهای خروجی (Departure)
        if str(ann.get("FlightType", "")).upper() in ["D", "DEPARTURE", "خروجی"]:
            airline = ann.get("AirlineName") or ann.get("Airline") or ann.get("company", "نامشخص")
            flights.append({
                "airline": str(airline).strip(),
                "flight_number": ann.get("FlightNumber"),
                "destination": ann.get("Destination"),
                "time": ann.get("Time"),
                "status": ann.get("Status")
            })
    
    df = pd.DataFrame(flights)
    
    if df.empty:
        print("هیچ پرواز خروجی پیدا نشد!")
        return pd.DataFrame(), df
    
    # شمارش تعداد پرواز هر شرکت
    stats = (df.groupby("airline")
             .size()
             .reset_index(name="flight_count")
             .sort_values("flight_count", ascending=False))
    
    total = len(df)
    print(f"\n📊 آمار پروازهای خروجی مهرآباد - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"تعداد کل پروازهای خروجی: {total}\n")
    print(stats.to_string(index=False))
    
    return stats, df

def save_results(stats, raw_df, date):
    os.makedirs("output", exist_ok=True)
    
    base = f"output/{date}"
    
    # CSV
    stats.to_csv(f"{base}.csv", index=False, encoding="utf-8-sig")
    
    # اکسل
    with pd.ExcelWriter(f"{base}.xlsx") as writer:
        stats.to_excel(writer, sheet_name="آمار_شرکت‌ها", index=False)
        raw_df.to_excel(writer, sheet_name="جزئیات_پروازها", index=False)
    
    # Markdown (قشنگ برای GitHub)
    with open(f"{base}.md", "w", encoding="utf-8") as f:
        f.write(f"# آمار پروازهای خروجی مهرآباد\n\n**تاریخ:** {date}\n\n")
        f.write(f"**تعداد کل پروازها:** {stats['flight_count'].sum()}\n\n")
        f.write(stats.to_markdown(index=False))
    
    print(f"\n✅ فایل‌ها ذخیره شدند:")
    print(f"   • {base}.csv")
    print(f"   • {base}.xlsx")
    print(f"   • {base}.md")

if __name__ == "__main__":
    try:
        date = datetime.now().strftime("%Y-%m-%d")
        data = fetch_flights()
        stats, raw = process_departures(data)
        save_results(stats, raw, date)
    except Exception as e:
        print(f"خطا: {e}")
