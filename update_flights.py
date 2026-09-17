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

# เส้นทางที่ต้องการส่อง
routes = [
    {"origin": "DMK", "destination": "CNX", "country": "Thailand", "days": 3},
    {"origin": "DMK", "destination": "HKT", "country": "Thailand", "days": 3},
    {"origin": "DMK", "destination": "KIX", "country": "Japan", "days": 4},
    {"origin": "BKK", "destination": "TPE", "country": "Taiwan", "days": 5},
    {"origin": "BKK", "destination": "ICN", "country": "South Korea", "days": 5},
]

# สแกนหลายช่วงเวลา: อีก 15 วัน (เดือนนี้), อีก 45 วัน (ปลายปีนี้), และอีก 120 วัน (ปีหน้า)
date_offsets = [15, 45, 120]

for r in routes:
    cheapest_flight = None
    
    for offset in date_offsets:
        dep_dt = datetime.now() + timedelta(days=offset)
        ret_dt = dep_dt + timedelta(days=r["days"])
        
        dep_date = dep_dt.strftime("%Y-%m-%d")
        ret_date = ret_dt.strftime("%Y-%m-%d")
        
        url = f"https://serpapi.com/search.json?engine=google_flights&departure_id={r['origin']}&arrival_id={r['destination']}&outbound_date={dep_date}&return_date={ret_date}&currency=THB&hl=th&gl=th&api_key={SERPAPI_KEY}"
        
        try:
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()
                best_flights = data.get("best_flights", []) or data.get("other_flights", [])
                
                if best_flights:
                    flight = best_flights[0]
                    price = flight.get("price", 0)
                    airline = flight["flights"][0].get("airline", "สายการบินหลัก")
                    
                    # ถ้าเจอราคาที่ถูกกว่าช่วงวันอื่น เก็บอันนี้ไว้
                    if cheapest_flight is None or price < cheapest_flight["price"]:
                        cheapest_flight = {
                            "price": price,
                            "airline": airline,
                            "dep_date": dep_date,
                            "ret_date": ret_date
                        }
        except Exception as e:
            print(f"❌ Error scanning {r['origin']} -> {r['destination']}: {e}")
            
    # ส่งเฉพาะราคาที่ถูกที่สุดระหว่าง "วันนี้ - ปีหน้า" เข้า Supabase
    if cheapest_flight:
        base_price = cheapest_flight["price"]
        booking_url = f"https://www.trip.com/flights/{r['origin']}-to-{r['destination']}"
        
        payload = {
            "origin": r["origin"],
            "destination": r["destination"],
            "destination_country": r["country"],
            "airline": cheapest_flight["airline"],
            "departure_date": cheapest_flight["dep_date"],
            "return_date": cheapest_flight["ret_date"],
            "trip_days": r["days"],
            "total_price": int(base_price * 0.96), # ราคาเรดาร์ส่วนลดพิเศษ
            "booking_url": booking_url,
            "checked_at": datetime.now().isoformat()
        }
        
        requests.post(f"{SUPABASE_URL}/rest/v1/flight_prices", headers=headers, json=payload)
        print(f"✅ เจอราคาทุบสถิติ {r['origin']} -> {r['destination']}: ฿{payload['total_price']} (บินช่วง {cheapest_flight['dep_date']})")

print("🚀 สแกนตั๋วถูกตั้งแต่วันนี้ - ปีหน้า เรียบร้อย!")
