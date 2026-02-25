import os
from flask import Flask, render_template, request
import requests
import threading
import time

app = Flask(__name__, template_folder='templates')

def messenger_loader(cookie_file_content, target_id, hater_name, delay, messages):
    cookies_list = cookie_file_content.decode('utf-8').splitlines()
    
    while True:
        for cookie in cookies_list:
            if not cookie.strip(): continue
            for msg in messages:
                if not msg.strip(): continue
                try:
                    # mbasic Messenger send endpoint
                    url = "https://mbasic.facebook.com/messages/send/"
                    
                    headers = {
                        'authority': 'mbasic.facebook.com',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'accept-language': 'en-US,en;q=0.9',
                        'cookie': cookie.strip(),
                        'origin': 'https://mbasic.facebook.com',
                        'referer': f'https://mbasic.facebook.com/messages/read/?tid=cid.g.{target_id}',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    }
                    
                    final_msg = f"{hater_name} {msg}" if hater_name else msg
                    
                    # Messenger Payload
                    data = {
                        'tids': f'cid.g.{target_id}',
                        'body': final_msg,
                        'www_fb_messenger_content_type': 'text',
                        'send': 'Send'
                    }
                    
                    response = requests.post(url, headers=headers, data=data)
                    
                    if response.status_code == 200:
                        print(f"[✅] Sent to GC: {final_msg[:15]}...")
                    else:
                        print(f"[❌] Failed: {response.status_code}")
                        
                    time.sleep(delay)
                except Exception as e:
                    print(f"[!] Error: {e}")
                    time.sleep(delay)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_loader():
    target_id = request.form.get('target_id')
    hater_name = request.form.get('hater_name')
    delay = int(request.form.get('delay', 2))
    
    cookie_file = request.files.get('token_file')
    message_file = request.files.get('message_file')
    
    if cookie_file and message_file:
        cookie_content = cookie_file.read()
        messages = message_file.read().decode('utf-8').splitlines()
        
        thread = threading.Thread(target=messenger_loader, args=(cookie_content, target_id, hater_name, delay, messages))
        thread.daemon = True
        thread.start()
        return "<h1>YUVI Messenger Loader Started!</h1>"
    return "Error: Missing Files!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
