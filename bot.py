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
        self.wfile.write(b"Active Call Audio Bot is Running Alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

BOT_TOKEN = "8564093311:AAE1wtnRDybV4oOH3HgmJbHplsBovYVtZm8"
CHAT_ID = "-1003178872820"

PANEL_ACTIVE_CALLS_URL = "https://www.orangecarrier.com/live/calls"

bot = Bot(token=BOT_TOKEN)
seen_active_calls = set()

COUNTRY_DATA = {
    "880": {"flag": "🇧🇩", "code": "#BD"}, "91": {"flag": "🇮🇳", "code": "#IN"},
    "1": {"flag": "🇺🇸", "code": "#US/CA"}, "44": {"flag": "🇬🇧", "code": "#UK"},
    "504": {"flag": "🇭🇳", "code": "#HN"}, "54": {"flag": "🇦🇷", "code": "#AR"}
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
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    })
    try:
        response = session.get(PANEL_ACTIVE_CALLS_URL)
        if response.status_code != 200:
            print(f"⚠️ Panel response status: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        call_list = []
        
        for row in soup.find_all('tr'):
            text_content = row.get_text(" ", strip=True)
            numbers = re.findall(r'(\+?\d{8,15})', text_content)
            if len(numbers) >= 2:
                did = numbers[0]
                cli = numbers[1]
                
                dur_match = re.search(r'\b(\d{1,3})\b', text_content)
                duration = dur_match.group(1) if dur_match else "0"
                
                did_clean = re.sub(r'\D', '', did)
                cli_clean = re.sub(r'\D', '', cli)
                
                if len(did_clean) >= 4 and len(cli_clean) >= 4:
                    call_id = f"{did_clean}_{cli_clean}"
                    
                    audio_link = None
                    for a_tag in row.find_all('a', href=True):
                        href = a_tag['href']
                        if any(x in href.lower() for x in ['play', 'listen', 'audio', 'stream', 'call']):
                            audio_link = href
                            break
                    
                    call_list.append({
                        'id': call_id,
                        'did': did_clean,
                        'cli': cli_clean,
                        'duration': duration,
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
            "📞 **DID:** `+5491171180334`\n"
            "📱 **CLI:** 🇦🇷 `+15627*****219`\n"
            "⏱️ **Duration:** `18s`\n"
            "✨ **Bot is running and monitoring calls successfully!**"
        )
        await bot.send_message(chat_id=CHAT_ID, text=demo_text, parse_mode="Markdown")
        print("✅ Startup Demo Notification sent to group successfully!")
    except Exception as e:
        print(f"❌ Demo notification failed: {e}")

async def main():
    print("🚀 Active Calls Monitor Bot started successfully...")
    await send_startup_notification()

    while type(True) == bool:
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
            
            if len(seen_active_calls) > 50:
                seen_active_calls.clear()
                
        except Exception as e:
            print(f"Loop error: {e}")
            
        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
