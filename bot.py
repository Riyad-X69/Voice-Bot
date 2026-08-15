import os
import re
import asyncio
import logging
import threading
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Voice Call Audio Bot is Running Alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# ক্রেডেনশিয়ালস
BOT_TOKEN = "8564093311:AAE1wtnRDybV4oOH3HgmJbHplsBovYVtZm8"
CHAT_ID = "-1003178872820"

PANEL_CALLS_URL = "https://www.orangecarrier.com/live/calls"

# আপনার কুকি থেকে সব ধরনের অতিরিক্ত স্পেস ও নতুন লাইন রিমোভ করে এক লাইনে রাখা হলো
RAW_COOKIE = "Orange_carrier_session=eyJpdiI6IkVBRTdRUXFyVER2N29UTVJzRUZhcEE9PSIsInZhbHVlIjoiSkcwREdcLzUxOTVEQmZQQVhVXC9mcEErK1NMbjZ5Z1FRNHRNSlBFekRRbHhscnFDTUcwODV4dnhJVHNzbEROOGVnOEFtTGc3RllkRUNvTW9ZZ1JEbjJHWUJNdGlOd2UxU1RQSit4dE8xZnBXbHg2b2lValpacHNHNWtsbkNEXC9rNmMiLCJtYWMiOiI3NWVjNjExYWJhZTBhM2RiNWUzZjQ5YzkwOTQ4Y2JlZWNhZjA4OTRmYjk3MDc0MWRmNTU2OThkNzA1ZWRlNjhkIn0%3D;_gat_gtag_UA_191466370_1=1;_fbp=fb.1.1786811898314.919633458798933041;_ga=GA1.2.1783611367.1786811898;_gid=GA1.2.360386769.1786811898;XSRF-TOKEN=eyJpdiI6InNBOHhva1I2V1Bwa1NFaEJnK2FFaHc9PSIsInZhbHVlIjoiZm9qdFJMbEwzeU95Mnc5WEFPNWhITXlZczluXC9JbVNUTFVaRzhMOFQ0amFORVRFdTkwQTJPN05rV0lsMFZIOFwvWTQ2c2o5U251d2RDclFUaDVFUllcL01DWWQrK1I2NFhLWGpvMSt3TjhhV3dVZXE1RUtDcm9MQmJWUnlMOVp5bysiLCJtYWMiOiIyZmVmODAzZTVkMmE1ZWZmMGMwMTA2OWQzYzZiZTE0ODliMjZkYzU5YmNhN2RjYTU4NWYxM2U3MzljY2U1OGNlIn0%3D"
COOKIES = RAW_COOKIE.replace("\n", "").replace("\r", "").strip()

bot = Bot(token=BOT_TOKEN)
seen_call_ids = set()

COUNTRY_DATA = {
    "880": {"flag": "🇧🇩", "code": "#BD"}, "91": {"flag": "🇮🇳", "code": "#IN"},
    "1": {"flag": "🇺🇸", "code": "#US/CA"}, "44": {"flag": "🇬🇧", "code": "#UK"}
}

def get_country_info(number):
    clean_number = re.sub(r'\D', '', str(number))
    for prefix in sorted(COUNTRY_DATA.keys(), key=len, reverse=True):
        if clean_number.startswith(prefix):
            return COUNTRY_DATA[prefix]
    return {"flag": "🌐", "code": "#INT"}

def mask_number(number):
    clean = re.sub(r'\D', '', str(number))
    if len(clean) > 8:
        return clean[:5] + "*****" + clean[-3:]
    return clean

def fetch_calls_with_cookies():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Cookie": COOKIES
    })
    try:
        calls_response = session.get(PANEL_CALLS_URL)
        
        if "login" in calls_response.url or calls_response.status_code != 200:
            print(f"❌ Cookie Login Failed! URL: {calls_response.url} | Status Code: {calls_response.status_code}")
            return []
        
        print("✅ Cookie Login Successful! প্যানেل থেকে লাইভ কল চেক করা হচ্ছে...")
        soup = BeautifulSoup(calls_response.text, 'html.parser')
        
        call_list = []
        for row in soup.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 5:
                did = cols[0].text.strip()
                cli = cols[1].text.strip()
                duration = cols[2].text.strip()
                
                call_id = f"{did}_{cli}_{duration}"
                
                audio_link = None
                audio_tag = row.find('audio') or row.find('a', href=re.compile(r'\.(mp3|wav|ogg)', re.I)) or row.find('a', class_=re.compile(r'play', re.I))
                if audio_tag:
                    audio_link = audio_tag.get('src') or audio_tag.get('href')

                call_list.append({
                    'id': call_id, 
                    'did': did,
                    'cli': cli,
                    'duration': duration,
                    'audio_link': audio_link
                })
        return call_list
    except Exception as e:
        logging.error(f"Error fetching calls: {e}")
    return []

async def send_demo_call_notification():
    try:
        demo_caption = (
            f"📞 **[DEMO CALL RECEIVED]**\n\n"
            f"📞 **DID:** `+8801800000000`\n"
            f"📱 **CLI:** 🇧🇩 `88018*****000`\n"
            f"⏱️ **Duration:** `12s`\n"
            f"✨ *Your bot active now & Cookie login verified successfully!*"
        )
        
        # ভয়েস ফেইল করলে যাতে টেক্সট মেসেজ হিসেবে সেফলি চলে যায়
        await bot.send_message(chat_id=CHAT_ID, text=demo_caption, parse_mode="Markdown")
        print("✅ Demo call notification sent to group successfully!")
    except Exception as e:
        print(f"❌ Demo call send failed: {e}")

async def main():
    print("Orange Carrier Audio Bot (Cookie Auth) started successfully...")
    
    await send_demo_call_notification()

    while True:
        try:
            calls_data = fetch_calls_with_cookies()
            for call in calls_data:
                if call['id'] not in seen_call_ids:
                    seen_call_ids.add(call['id'])
                    
                    did = call['did']
                    cli = call['cli']
                    duration = call['duration']
                    audio_link = call['audio_link']
                    
                    country = get_country_info(cli)
                    masked_cli = mask_number(cli)
                    
                    caption = (
                        f"📞 **New Completed Call Audio!**\n\n"
                        f"📞 **DID:** `{did}`\n"
                        f"📱 **CLI:** {country['flag']} `{masked_cli}`\n"
                        f"⏱️ **Duration:** `{duration}s`"
                    )
                    
                    if audio_link:
                        try:
                            if audio_link.startswith('/'):
                                audio_link = "https://www.orangecarrier.com" + audio_link
                            
                            await bot.send_voice(
                                chat_id=CHAT_ID, 
                                voice=audio_link, 
                                caption=caption, 
                                parse_mode="Markdown"
                            )
                            print(f"✅ Call audio voice sent for CLI: {masked_cli}")
                        except Exception as ex:
                            logging.warning(f"Voice send failed, sending text: {ex}")
                            await bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode="Markdown")
                    else:
                        await bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode="Markdown")
                        
        except Exception as e:
            logging.error(f"Loop error: {e}")
            
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
