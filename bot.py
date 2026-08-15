import os
import re
import time
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

PANEL_LOGIN_URL = "https://www.orangecarrier.com/login"
PANEL_CALLS_URL = "https://www.orangecarrier.com/live/calls"

USERNAME = "gmaixcom116@gmail.com"
PASSWORD = "Riad+@19"

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

def login_and_fetch_calls():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
    })
    try:
        login_page = session.get(PANEL_LOGIN_URL)
        soup = BeautifulSoup(login_page.text, 'html.parser')
        
        token_input = soup.find('input', {'name': '_token'})
        token = token_input['value'] if token_input else ""

        login_data = {
            "_token": token,
            "email": USERNAME,
            "password": PASSWORD
        }
        
        response = session.post(PANEL_LOGIN_URL, data=login_data, allow_redirects=True)
        time.sleep(3)
        
        if "login" in response.url or "Invalid" in response.text or (response.status_code != 200 and not response.history):
            print(f"❌ Login Failed! URL: {response.url} | Status Code: {response.status_code}")
            return []
        
        print("✅ Login Successful! Checking calls...")
        calls_response = session.get(PANEL_CALLS_URL)
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

async def send_startup_message():
    try:
        await bot.send_message(chat_id=CHAT_ID, text="Your bot active now", parse_mode="Markdown")
        print("✅ 'Your bot active now' message sent to group successfully!")
    except Exception as e:
        print(f"❌ Startup message send failed: {e}")

async def main():
    print("Orange Carrier Audio Bot started successfully...")
    
    # বোট চালু হওয়ার সাথে সাথে গ্রুপে মেসেজ পাঠাবে
    await send_startup_message()

    while True:
        try:
            calls_data = login_and_fetch_calls()
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
