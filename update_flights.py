import os
import requests
from datetime import datetime, timedelta

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

routes = [
    {"origin": "DMK", "destination": "CNX", "country": "Thailand", "days": 3},
    {"origin": "DMK", "destination": "HKT", "country": "Thailand", "days": 3},
    {"origin": "DMK", "destination": "KIX", "country": "Japan", "days": 4},
    {"origin": "BKK", "destination": "TPE", "country": "Taiwan", "days": 5},
]

dep_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")

for r in routes:
    ret_date = (datetime.now() + timedelta(days=60 + r["days"])).strftime("%Y-%m-%d")
    url = f"https://serpapi.com/search.json?engine=google_flights&departure_id={r['origin']}&arrival_id={r['destination']}&outbound_date={dep_date}&return_date={ret_date}&currency=THB&hl=th&gl=th&api_key={SERPAPI_KEY}"
    
    # สร้างลิงก์ตรงไปยัง Google Flights สำหรับจองตั๋ว
    booking_url = f"https://www.google.com/travel/flights?q=Flights%20to%20{r['destination']}%20from%20{r['origin']}%20on%20{dep_date}%20through%20{ret_date}"
    
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            best_flights = data.get("best_flights", []) or data.get("other_flights", [])
                
            if best_flights:
                flight = best_flights[0]
                price = flight.get("price", 0)
                airline = flight["flights"][0].get("airline", "Multiple Airlines")
                
                payload = {
                    "origin": r["origin"],
                    "destination": r["destination"],
                    "destination_country": r["country"],
                    "airline": airline,
                    "departure_date": dep_date,
                    "return_date": ret_date,
                    "trip_days": r["days"],
                    "total_price": price,
                    "booking_url": booking_url,
                    "checked_at": datetime.now().isoformat()
                }
                
                requests.post(f"{SUPABASE_URL}/rest/v1/flight_prices", headers=headers, json=payload)
                print(f"✅ Updated {r['origin']} -> {r['destination']}: ฿{price}")
    except Exception as e:
        print(f"❌ Error fetching {r['origin']} -> {r['destination']}: {e}")

print("🚀 Finished updating flight prices!")
