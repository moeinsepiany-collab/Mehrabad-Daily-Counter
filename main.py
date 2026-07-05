import requests
import pandas as pd

url = "https://www.faza24.ir/api/apiweb/RetrieveAnnouncements?Ipaddress=&Origin=thr"

data = requests.get(url).json()

df = pd.DataFrame(data)

# فقط خروجی مهرآباد
df = df[df["Type"].str.contains("خروجی")]

result = df["AirlineName"].value_counts().reset_index()
result.columns = ["Airline", "Flights"]

print(result)
