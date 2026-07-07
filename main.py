import requests
import pandas as pd
from datetime import datetime
import os
import json

from config import API_URL

def fetch_flights():
    params = {"Ipaddress": "", "Origin": "thr"}
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    # ذخیره خام دیتا برای دیباگ
    with open("raw_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return data

def process_departures(data):
    announcements = data.get("Announcements", []) if isinstance(data, dict) else data
    if not announcements:
        print("⚠️ هیچ اعلامیه‌ای پیدا نشد!")
        return pd.DataFrame(), pd.DataFrame()
    
    flights = []
    for ann in announcements:
        flight_type = str(ann.get("FlightType", "")).upper()
        if flight_type in ["D", "DEPARTURE", "خروجی", "1"]:
            airline = (ann.get("AirlineName") or 
                      ann.get("Airline") or 
                      ann.get("company") or 
                      "نامشخص")
            
            flights.append({
                "airline": str(airline).strip(),
                "flight_number": ann.get("FlightNumber"),
                "destination": ann.get("Destination"),
                "time": ann.get("Time"),
                "status": ann.get("Status")
            })
    
    df = pd.DataFrame(flights)
    
    if df.empty:
        print("⚠️ هیچ پرواز خروجی پیدا نشد!")
        return pd.DataFrame(), pd.DataFrame()
    
    stats = (df.groupby("airline")
             .size()
             .reset_index(name="flight_count")
             .sort_values("flight_count", ascending=False))
    
    print(f"\n✅ آمار پروازهای خروجی مهرآباد - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"تعداد کل پروازها: {len(df)}")
    print("\n", stats.to_string(index=False))
    
    return stats, df

def save_results(stats, raw_df, date):
    os.makedirs("output", exist_ok=True)
    base = f"output/{date}"
    
    stats.to_csv(f"{base}.csv", index=False, encoding="utf-8-sig")
    
    with pd.ExcelWriter(f"{base}.xlsx") as writer:
        stats.to_excel(writer, sheet_name="آمار_شرکت‌ها", index=False)
        if not raw_df.empty:
            raw_df.to_excel(writer, sheet_name="جزئیات_پروازها", index=False)
    
    with open(f"{base}.md", "w", encoding="utf-8") as f:
        f.write(f"# آمار پروازهای خروجی مهرآباد\n\n**تاریخ:** {date}\n\n")
        f.write(f"**تعداد کل پروازها:** {stats['flight_count'].sum() if not stats.empty else 0}\n\n")
        f.write(stats.to_markdown(index=False) if not stats.empty else "هیچ داده‌ای موجود نیست.")
    
    print(f"📁 فایل‌ها در پوشه output ذخیره شدند.")

if __name__ == "__main__":
    try:
        date = datetime.now().strftime("%Y-%m-%d")
        print("در حال دریافت اطلاعات از faza24.ir ...")
        data = fetch_flights()
        stats, raw = process_departures(data)
        save_results(stats, raw, date)
        print("✅ عملیات با موفقیت تمام شد.")
    except Exception as e:
        print(f"❌ خطا: {e}")
        import traceback
        traceback.print_exc()
