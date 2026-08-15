import os
import re
import json
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
        self.wfile.write(b"Active Call Audio Bot is Running Alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# ক্রেডেনশিয়ালস
BOT_TOKEN = "8564093311:AAE1wtnRDybV4oOH3HgmJbHplsBovYVtZm8"
CHAT_ID = "-1003178872820"

PANEL_ACTIVE_CALLS_URL = "https://www.orangecarrier.com/live/calls"

# আপনার কুকি ডাটা
COOKIE_JSON = [
    {
        "name": "orange_carrier_session",
        "value": "eyJpdiI6Ildybk9qdWYyV1BRWnNHdWcwNVpzdEE9PSIsInZhbHVlIjoiNFR3WllhMUprXC93OUxWOXRUQ0lJelwvbjQrQ05oUnFTNVBadThQeFwvSlpZOWRtY1JibjFwRlNZQ2w0STNUbVwvcmIwOFFXaTdXTmVKNitCU1VTQXlKTnVPMXo4emFYZjVXQkZFaXhkczNqUU81T3JHbWJJSTljMW5jSVR5Vlk2aVVTIiwibWFjIjoiNDM2ZTAwZjFhNGViZjg5ZDVhY2EwMTllZjUwOGE4MDUzMGVlMGVmYTdkNTE0MDE1Nzg1MTEyMGQ1YTZhZjMyMiJ9",
        "domain": "www.orangecarrier.com",
        "hostOnly": True,
        "path": "/",
        "secure": False,
        "httpOnly": True,
        "sameSite": None,
        "session": False,
        "firstPartyDomain": "",
        "partitionKey": None,
        "expirationDate": 1786827863.322,
        "storeId": None
    },
    {
        "name": "_gat_gtag_UA_191466370_1",
        "value": "1",
        "domain": ".orangecarrier.com",
        "hostOnly": False,
        "path": "/",
        "secure": False,
        "httpOnly": False,
        "sameSite": None,
        "session": False,
        "firstPartyDomain": "",
        "partitionKey": None,
        "expirationDate": 1786820200,
        "storeId": None
    },
    {
        "name": "_fbp",
        "value": "fb.1.1786811898314.919633458798933041",
        "domain": ".orangecarrier.com",
        "hostOnly": False,
        "path": "/",
        "secure": False,
        "httpOnly": False,
        "sameSite": None,
        "session": False,
        "firstPartyDomain": "",
        "partitionKey": None,
        "expirationDate": 1794596162,
        "storeId": None
    },
    {
        "name": "_ga",
        "value": "GA1.2.1783611367.1786811898",
        "domain": ".orangecarrier.com",
        "hostOnly": False,
        "path": "/",
        "secure": False,
        "httpOnly": False,
        "sameSite": None,
        "session": False,
        "firstPartyDomain": "",
        "partitionKey": None,
        "expirationDate": 1821380153.487,
        "storeId": None
    },
    {
        "name": "_gid",
        "value": "GA1.2.360386769.1786811898",
        "domain": ".orangecarrier.com",
        "hostOnly": False,
        "path": "/",
        "secure": False,
        "httpOnly": False,
        "sameSite": None,
        "session": False,
        "firstPartyDomain": "",
        "partitionKey": None,
        "expirationDate": 1786906553,
        "storeId": None
    },
    {
        "name": "XSRF-TOKEN",
        "value": "eyJpdiI6Im5lMkZhb1ZJR2crREtaRlh4VDdyNlE9PSIsInZhbHVlIjoiOTlld0hlZzNIR0ZrSTJBUGxIcElsK0hEcTIxSnN5R1VaOG5lWTMrVXRlWjQxNStHVW1vRWhrUDFYTXBWUGZGUHQzYXpNb0h5bXZzSFphdDVpWk41OGZwT2dZR21MSnZxMzZPQWJEbktYNmVkUHorblZ3dHlyUURpRWRWd3lMN1giLCJtYWMiOiI5NDAwNDk5NDZkOGZmMTg1YzA4ZGEwMTgyYjI5OTBkYzc2OGE3MjlmMTM1NGYwOTBmZjk5N2ZiYjgwMmY5MzhlIn0%3D",
        "domain": "www.orangecarrier.com",
        "hostOnly": True,
        "path": "/",
        "secure": False,
        "httpOnly": False,
        "sameSite": None,
        "session": False,
        "firstPartyDomain": "",
        "partitionKey": None,
        "expirationDate": 1786827863.322,
        "storeId": None
    }
]

COOKIES = "; ".join([f"{c['name']}={c['value']}" for c in COOKIE_JSON])

bot = Bot(token=BOT_TOKEN)
seen_active_calls = set()

COUNTRY_DATA = {
    "880": {"flag": "🇧🇩", "code": "#BD"}, "91": {"flag": "🇮🇳", "code": "#IN"},
    "1": {"flag": "🇺🇸", "code": "#US/CA"}, "44": {"flag": "🇬🇧", "code": "#UK"},
    "504": {"flag": "🇭🇳", "code": "#HN"} # Honduras
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

def fetch_active_calls():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Cookie": COOKIES,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    })
    try:
        response = session.get(PANEL_ACTIVE_CALLS_URL)
        if "login" in response.url or response.status_code != 200:
            print(f"❌ Cookie Login Failed! URL: {response.url}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        call_list = []
        
        # প্যানেলের টেবিল রো খুঁজে বের করা
        for row in soup.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 3:
                did = cols[0].text.strip()
                cli = cols[1].text.strip()
                duration = cols[2].text.strip()
                
                # যদি DID এবং CLI তে সংখ্যা থাকে
                if any(char.isdigit() for char in did) and any(char.isdigit() for char in cli):
                    # ক্লিন নম্বর নেওয়া
                    did_clean = re.sub(r'\D', '', did)
                    cli_clean = re.sub(r'\D', '', cli)
                    
                    if len(did_clean) >= 4 and len(cli_clean) >= 4:
                        call_id = f"{did_clean}_{cli_clean}"
                        
                        audio_link = None
                        audio_tag = row.find('audio') or row.find('a', href=True)
                        if audio_tag:
                            href = audio_tag.get('href', '')
                            if any(x in href for x in ['listen', 'stream', 'audio', 'play', 'call']):
                                audio_link = href

                        call_list.append({
                            'id': call_id,
                            'did': did_clean,
                            'cli': cli_clean,
                            'duration': duration if duration else "0",
                            'audio_link': audio_link
                        })
        return call_list
    except Exception as e:
        print(f"Fetch error: {e}")
    return []

async def send_startup_notification():
    try:
        demo_text = (
            "📞 **DEMO CALL RECEIVED**\n\n"
            "📞 **DID:** `+8801800000000`\n"
            "📱 **CLI:** 🇧🇩 `88018*****000`\n"
            "⏱️ **Duration:** `12s`\n"
            "✨ **Your bot active now & Cookie login verified successfully!**"
        )
        await bot.send_message(chat_id=CHAT_ID, text=demo_text, parse_mode="Markdown")
        print("✅ Startup Demo Notification sent to group successfully!")
    except Exception as e:
        print(f"❌ Demo notification failed: {e}")

async def main():
    print("🚀 Active Calls Monitor Bot started successfully...")
    
    # বোট চালু হওয়ার সাথে সাথে আপনার পছন্দমতো ডেমো মেসেজ পাঠাবে
    await send_startup_notification()

    while True:
        try:
            active_calls = fetch_active_calls()
            for call in active_calls:
                if call['id'] not in seen_active_calls:
                    seen_active_calls.add(call['id'])
                    
                    did = call['did']
                    cli = call['cli']
                    duration = call['duration']
                    audio_link = call['audio_link']
                    
                    country = get_country_info(cli)
                    masked_cli = mask_number(cli)
                    
                    caption = (
                        f"📞 **LIVE CALL RECEIVED**\n\n"
                        f"📞 **DID:** `{did}`\n"
                        f"📱 **CLI:** {country['flag']} `{masked_cli}`\n"
                        f"⏱️ **Duration:** `{duration}s`"
                    )
                    
                    if audio_link:
                        if audio_link.startswith('/'):
                            audio_link = "https://www.orangecarrier.com" + audio_link
                        try:
                            await bot.send_voice(chat_id=CHAT_ID, voice=audio_link, caption=caption, parse_mode="Markdown")
                        except:
                            await bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode="Markdown")
                    else:
                        await bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode="Markdown")
                    
                    print(f"✅ Real call sent to Telegram: {masked_cli}")
            
            if len(seen_active_calls) > 40:
                seen_active_calls.clear()
                
        except Exception as e:
            print(f"Loop error: {e}")
            
        # প্রতি ৫ সেকেন্ড পরপর চেক লুপ
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
