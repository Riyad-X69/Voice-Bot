import os
import re
import asyncio
import logging
import threading
from bs4 import BeautifulSoup
from telegram import Bot
from curl_cffi import requests
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

# কনফিগারেশন এবং ক্রেডেনশিয়ালস
BOT_TOKEN = "8564093311:AAH55oqI6UmMfXycsEtxtIMjOHNN6atuVoo"
CHAT_ID = "-1003178872820"

PANEL_LOGIN_URL = "https://www.orangecarrier.com/login"
PANEL_CALLS_URL = "https://www.orangecarrier.com/live/calls"

USERNAME = "gmaixcom116@gmail.com"
PASSWORD = "Riad+@19"

bot = Bot(token=BOT_TOKEN)
seen_call_ids = set()

COUNTRY_DATA = {
    "93": {"flag": "🇦🇫", "code": "#AF"}, "358": {"flag": "🇦🇽", "code": "#AX"}, "355": {"flag": "🇦🇱", "code": "#AL"},
    "213": {"flag": "🇩🇿", "code": "#DZ"}, "1684": {"flag": "🇦🇸", "code": "#AS"}, "376": {"flag": "🇦🇩", "code": "#AD"},
    "244": {"flag": "🇦🇴", "code": "#AO"}, "1264": {"flag": "🇦🇮", "code": "#AI"}, "672": {"flag": "🇦🇶", "code": "#AQ"},
    "1268": {"flag": "🇦🇬", "code": "#AG"}, "54": {"flag": "🇦🇷", "code": "#AR"}, "374": {"flag": "🇦🇲", "code": "#AM"},
    "297": {"flag": "🇦🇼", "code": "#AW"}, "61": {"flag": "🇦🇺", "code": "#AU"}, "43": {"flag": "🇦🇹", "code": "#AT"},
    "994": {"flag": "🇦🇿", "code": "#AZ"}, "1242": {"flag": "🇧🇸", "code": "#BS"}, "973": {"flag": "🇧🇭", "code": "#BH"},
    "880": {"flag": "🇧🇩", "code": "#BD"}, "1246": {"flag": "🇧🇧", "code": "#BB"}, "375": {"flag": "🇧🇾", "code": "#BY"},
    "32": {"flag": "🇧🇪", "code": "#BE"}, "501": {"flag": "🇧🇿", "code": "#BZ"}, "229": {"flag": "🇧🇯", "code": "#BJ"},
    "1441": {"flag": "🇧🇲", "code": "#BM"}, "975": {"flag": "🇧🇹", "code": "#BT"}, "591": {"flag": "🇧🇴", "code": "#BO"},
    "387": {"flag": "🇧🇦", "code": "#BA"}, "267": {"flag": "🇧🇼", "code": "#BW"}, "55": {"flag": "🇧🇷", "code": "#BR"},
    "246": {"flag": "🇮🇴", "code": "#IO"}, "673": {"flag": "🇧🇳", "code": "#BN"}, "359": {"flag": "🇧🇬", "code": "#BG"},
    "226": {"flag": "🇧🇫", "code": "#BF"}, "257": {"flag": "🇧🇮", "code": "#BI"}, "855": {"flag": "🇰🇭", "code": "#KH"},
    "237": {"flag": "🇨🇲", "code": "#CM"}, "1": {"flag": "🇺🇸", "code": "#US/CA"}, "238": {"flag": "🇨🇻", "code": "#CV"},
    "345": {"flag": "🇰🇾", "code": "#KY"}, "236": {"flag": "🇨🇫", "code": "#CF"}, "235": {"flag": "🇹🇩", "code": "#TD"},
    "56": {"flag": "🇨🇱", "code": "#CL"}, "86": {"flag": "🇨🇳", "code": "#CN"}, "61": {"flag": "🇨🇽", "code": "#CX"},
    "57": {"flag": "🇨🇴", "code": "#CO"}, "269": {"flag": "🇰🇲", "code": "#KM"}, "242": {"flag": "🇨🇬", "code": "#CG"},
    "243": {"flag": "🇨🇩", "code": "#CD"}, "682": {"flag": "🇨🇰", "code": "#CK"}, "506": {"flag": "🇨🇷", "code": "#CR"},
    "225": {"flag": "🇨🇮", "code": "#CI"}, "385": {"flag": "🇭🇷", "code": "#HR"}, "53": {"flag": "🇨🇺", "code": "#CU"},
    "357": {"flag": "🇨🇾", "code": "#CY"}, "420": {"flag": "🇨🇿", "code": "#CZ"}, "45": {"flag": "🇩🇰", "code": "#DK"},
    "253": {"flag": "🇩🇯", "code": "#DJ"}, "1767": {"flag": "🇩🇲", "code": "#DM"}, "1809": {"flag": "🇩🇴", "code": "#DO"},
    "593": {"flag": "🇪🇨", "code": "#EC"}, "20": {"flag": "🇪🇬", "code": "#EG"}, "503": {"flag": "🇸🇻", "code": "#SV"},
    "240": {"flag": "🇬🇶", "code": "#GQ"}, "291": {"flag": "🇪🇷", "code": "#ER"}, "372": {"flag": "🇪🇪", "code": "#EE"},
    "251": {"flag": "🇪🇹", "code": "#ET"}, "500": {"flag": "🇫🇰", "code": "#FK"}, "298": {"flag": "🇫🇴", "code": "#FO"},
    "679": {"flag": "🇫🇯", "code": "#FJ"}, "358": {"flag": "🇫🇮", "code": "#FI"}, "33": {"flag": "🇫🇷", "code": "#FR"},
    "594": {"flag": "🇬🇫", "code": "#GF"}, "689": {"flag": "🇵🇫", "code": "#PF"}, "241": {"flag": "🇬🇦", "code": "#GA"},
    "220": {"flag": "🇬🇲", "code": "#GM"}, "995": {"flag": "🇬🇪", "code": "#GE"}, "49": {"flag": "🇩🇪", "code": "#DE"},
    "233": {"flag": "🇬🇭", "code": "#GH"}, "350": {"flag": "🇬🇮", "code": "#GI"}, "30": {"flag": "🇬🇷", "code": "#GR"},
    "299": {"flag": "🇬🇱", "code": "#GL"}, "1473": {"flag": "🇬🇩", "code": "#GD"}, "590": {"flag": "🇬🇵", "code": "#GP"},
    "1671": {"flag": "🇬🇺", "code": "#GU"}, "502": {"flag": "🇬🇹", "code": "#GT"}, "44": {"flag": "🇬🇧", "code": "#UK"},
    "224": {"flag": "🇬🇳", "code": "#GN"}, "245": {"flag": "🇬🇼", "code": "#GW"}, "592": {"flag": "🇬🇾", "code": "#GY"},
    "509": {"flag": "🇭🇹", "code": "#HT"}, "504": {"flag": "🇭🇳", "code": "#HN"}, "852": {"flag": "🇭🇰", "code": "#HK"},
    "36": {"flag": "🇭🇺", "code": "#HU"}, "354": {"flag": "🇮🇸", "code": "#IS"}, "91": {"flag": "🇮🇳", "code": "#IN"},
    "62": {"flag": "🇮🇩", "code": "#ID"}, "98": {"flag": "🇮🇷", "code": "#IR"}, "964": {"flag": "🇮🇶", "code": "#IQ"},
    "353": {"flag": "🇮🇪", "code": "#IE"}, "972": {"flag": "🇮🇱", "code": "#IL"}, "39": {"flag": "🇮🇹", "code": "#IT"},
    "1876": {"flag": "🇯🇲", "code": "#JM"}, "81": {"flag": "🇯🇵", "code": "#JP"}, "962": {"flag": "🇯🇴", "code": "#JO"},
    "7": {"flag": "🇰🇿", "code": "#KZ"}, "254": {"flag": "🇰🇪", "code": "#KE"}, "686": {"flag": "🇰🇮", "code": "#KI"},
    "850": {"flag": "🇰🇵", "code": "#KP"}, "82": {"flag": "🇰🇷", "code": "#KR"}, "965": {"flag": "🇰🇼", "code": "#KW"},
    "996": {"flag": "🇰🇬", "code": "#KG"}, "856": {"flag": "🇱🇦", "code": "#LA"}, "371": {"flag": "🇱🇻", "code": "#LV"},
    "961": {"flag": "🇱🇧", "code": "#LB"}, "266": {"flag": "🇱🇸", "code": "#LS"}, "231": {"flag": "🇱🇷", "code": "#LR"},
    "218": {"flag": "🇱🇾", "code": "#LY"}, "423": {"flag": "🇱🇮", "code": "#LI"}, "370": {"flag": "🇱🇹", "code": "#LT"},
    "352": {"flag": "🇱🇺", "code": "#LU"}, "853": {"flag": "🇲🇴", "code": "#MO"}, "389": {"flag": "🇲🇰", "code": "#MK"},
    "261": {"flag": "🇲🇬", "code": "#MG"}, "265": {"flag": "🇲🇼", "code": "#MW"}, "60": {"flag": "🇲🇾", "code": "#MY"},
    "960": {"flag": "🇲🇻", "code": "#MV"}, "223": {"flag": "🇲🇱", "code": "#ML"}, "356": {"flag": "🇲🇹", "code": "#MT"},
    "692": {"flag": "🇲🇭", "code": "#MH"}, "596": {"flag": "🇲🇶", "code": "#MQ"}, "222": {"flag": "🇲🇷", "code": "#MR"},
    "230": {"flag": "🇲🇺", "code": "#MU"}, "52": {"flag": "🇲🇽", "code": "#MX"}, "691": {"flag": "🇫🇲", "code": "#FM"},
    "373": {"flag": "🇲🇩", "code": "#MD"}, "377": {"flag": "🇲🇨", "code": "#MC"}, "976": {"flag": "🇲🇳", "code": "#MN"},
    "382": {"flag": "🇲🇪", "code": "#ME"}, "212": {"flag": "🇲🇦", "code": "#MA"}, "258": {"flag": "🇲🇿", "code": "#MZ"},
    "95": {"flag": "🇲🇲", "code": "#MM"}, "264": {"flag": "🇳🇦", "code": "#NA"}, "674": {"flag": "🇳🇷", "code": "#NR"},
    "977": {"flag": "🇳🇵", "code": "#NP"}, "31": {"flag": "🇳🇱", "code": "#NL"}, "64": {"flag": "🇳🇿", "code": "#NZ"},
    "505": {"flag": "🇳🇮", "code": "#NI"}, "227": {"flag": "🇳🇪", "code": "#NE"}, "234": {"flag": "🇳🇬", "code": "#NG"},
    "47": {"flag": "🇳🇴", "code": "#NO"}, "968": {"flag": "🇴🇲", "code": "#OM"}, "92": {"flag": "🇵🇰", "code": "#PK"},
    "970": {"flag": "🇵🇸", "code": "#PS"}, "507": {"flag": "🇵🇦", "code": "#PA"}, "675": {"flag": "🇵🇬", "code": "#PG"},
    "595": {"flag": "🇵🇾", "code": "#PY"}, "51": {"flag": "🇵🇪", "code": "#PE"}, "63": {"flag": "🇵🇭", "code": "#PH"},
    "48": {"flag": "🇵🇱", "code": "#PL"}, "351": {"flag": "🇵🇹", "code": "#PT"}, "974": {"flag": "🇶🇦", "code": "#QA"},
    "40": {"flag": "🇷🇴", "code": "#RO"}, "7": {"flag": "🇷🇺", "code": "#RU"}, "250": {"flag": "🇷🇼", "code": "#RW"},
    "966": {"flag": "🇸🇦", "code": "#SA"}, "221": {"flag": "🇸🇳", "code": "#SN"}, "381": {"flag": "🇷🇸", "code": "#RS"},
    "65": {"flag": "🇸🇬", "code": "#SG"}, "421": {"flag": "🇸🇰", "code": "#SK"}, "386": {"flag": "🇸🇮", "code": "#SI"},
    "27": {"flag": "🇿🇦", "code": "#ZA"}, "34": {"flag": "🇪🇸", "code": "#ES"}, "94": {"flag": "🇱🇰", "code": "#LK"},
    "46": {"flag": "🇸🇪", "code": "#SE"}, "41": {"flag": "🇨🇭", "code": "#CH"}, "963": {"flag": "🇸🇾", "code": "#SY"},
    "886": {"flag": "🇹🇼", "code": "#TW"}, "992": {"flag": "🇹🇯", "code": "#TJ"}, "255": {"flag": "🇹🇿", "code": "#TZ"},
    "66": {"flag": "🇹🇭", "code": "#TH"}, "216": {"flag": "🇹🇳", "code": "#TN"}, "90": {"flag": "🇹🇷", "code": "#TR"},
    "380": {"flag": "🇺🇦", "code": "#UA"}, "971": {"flag": "🇦🇪", "code": "#UAE"}, "598": {"flag": "🇺🇾", "code": "#UY"},
    "998": {"flag": "🇺🇿", "code": "#UZ"}, "58": {"flag": "🇻🇪", "code": "#VE"}, "84": {"flag": "🇻🇳", "code": "#VN"},
    "967": {"flag": "🇾🇪", "code": "#YE"}, "260": {"flag": "🇿🇲", "code": "#ZM"}, "263": {"flag": "🇿🇼", "code": "#ZW"}
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

def get_service_name(message):
    msg_lower = message.lower()
    if "telegram" in msg_lower or "تلجرام" in msg_lower:
        return "Telegram"
    elif "facebook" in msg_lower or "فيسبوك" in msg_lower or "fb" in msg_lower:
        return "Facebook"
    elif "imo" in msg_lower:
        return "IMO"
    elif "tiktok" in msg_lower:
        return "TikTok"
    elif "google" in msg_lower:
        return "Google"
    elif "whatsapp" in msg_lower or "واتساب" in msg_lower:
        return "WhatsApp"
    else:
        return "Voice OTP Call"

def login_and_fetch_calls():
    session = requests.Session(impersonate="chrome120")
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
        
        response = session.post(PANEL_LOGIN_URL, data=login_data)
        
        if response.status_code == 200 or response.history:
            calls_response = session.get(PANEL_CALLS_URL)
            soup = BeautifulSoup(calls_response.text, 'html.parser')
            
            call_list = []
            for row in soup.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) >= 3:
                    call_id = cols[0].text.strip()
                    number = cols[1].text.strip()
                    message = cols[2].text.strip()
                    
                    audio_link = None
                    audio_tag = row.find('audio') or row.find('a', href=re.compile(r'\.(mp3|wav|ogg)', re.I))
                    if audio_tag:
                        audio_link = audio_tag.get('src') or audio_tag.get('href')

                    call_list.append({
                        'id': call_id, 
                        'number': number, 
                        'message': message,
                        'audio_link': audio_link
                    })
            return call_list
        else:
            logging.error(f"Login failed with status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error fetching calls: {e}")
    return []

async def main():
    print("Orange Carrier Audio/Voice Forwarder Bot started...")

    while True:
        try:
            calls_data = login_and_fetch_calls()
            for call in calls_data:
                if call['id'] not in seen_call_ids:
                    seen_call_ids.add(call['id'])
                    
                    number = call['number']
                    message = call['message']
                    audio_link = call['audio_link']
                    
                    country = get_country_info(number)
                    service = get_service_name(message)
                    masked_num = mask_number(number)
                    
                    caption = (
                        f"📞 **Call Received & Ended**\n\n"
                        f"| {country['flag']} `{masked_num}`\n"
                        f"| 🔹 **Service:** {service}\n"
                        f"| 💬 **OTP / Info:** `{message}`"
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
                        except Exception as ex:
                            logging.warning(f"Could not send direct voice, sending text: {ex}")
                            await bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode="Markdown")
                    else:
                        await bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode="Markdown")
                        
        except Exception as e:
            logging.error(f"Loop error: {e}")
            
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
