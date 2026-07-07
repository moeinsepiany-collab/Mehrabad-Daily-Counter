import requests
import json
from datetime import datetime

print("در حال اتصال به API...")

try:
    response = requests.get(
        "https://www.faza24.ir/api/apiweb/RetrieveAnnouncements?Ipaddress=&Origin=thr",
        timeout=30
    )
    
    print(f"وضعیت: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # ذخیره خام دیتا
        with open("raw_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ دیتا با موفقیت دریافت شد!")
        print(f"نوع دیتا: {type(data)}")
        
        if isinstance(data, dict):
            print("کلیدهای اصلی:", list(data.keys()))
            for k, v in data.items():
                if isinstance(v, list):
                    print(f"→ کلید '{k}' شامل {len(v)} آیتم")
                    if len(v) > 0 and isinstance(v[0], dict):
                        print(f"   کلیدهای آیتم: {list(v[0].keys())}")
                    break
        elif isinstance(data, list):
            print(f"دیتا لیست است با {len(data)} آیتم")
            if len(data) > 0:
                print("کلیدهای آیتم اول:", list(data[0].keys()))
        
        print("\nفایل raw_data.json در پوشه اصلی ساخته شد.")
    else:
        print("❌ خطا در دریافت دیتا")
        print(response.text[:500])
        
except Exception as e:
    print(f"❌ خطای کلی: {e}")
