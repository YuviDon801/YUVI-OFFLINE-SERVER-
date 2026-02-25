import os
from flask import Flask, render_template, request, jsonify
import requests
import threading
import time
from bs4 import BeautifulSoup

app = Flask(__name__)

# Global variable logs store karne ke liye
server_logs = []

def add_log(status, message):
    global server_logs
    timestamp = time.strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {status}: {message}"
    server_logs.append(log_entry)
    if len(server_logs) > 20: server_logs.pop(0) # Sirf last 20 logs rakhega

def get_tokens(session, target_id):
    url = f"https://mbasic.facebook.com/messages/read/?tid=cid.g.{target_id}"
    try:
        response = session.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form', method='post')
        if not form:
            add_log("❌ ERROR", "Cookie Expired ya ID Galat hai!")
            return None, None, None
        
        action_url = "https://mbasic.facebook.com" + form['action']
        fb_dtsg = soup.find('input', {'name': 'fb_dtsg'})['value']
        jazoest = soup.find('input', {'name': 'jazoest'})['value']
        return action_url, fb_dtsg, jazoest
    except Exception as e:
        add_log("⚠️ CONN", f"Facebook se connect nahi ho pa raha: {str(e)[:30]}")
        return None, None, None

def messenger_loader(cookie_content, target_id, hater_name, delay, messages):
    cookies = cookie_content.decode('utf-8').splitlines()
    
    while True:
        for ck in cookies:
            if not ck.strip(): continue
            session = requests.Session()
            session.headers.update({
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
                'cookie': ck.strip()
            })

            action_url, fb_dtsg, jazoest = get_tokens(session, target_id)
            if not action_url: continue

            for msg in messages:
                if not msg.strip(): continue
                try:
                    final_msg = f"{hater_name} {msg}" if hater_name else msg
                    data = {
                        'fb_dtsg': fb_dtsg, 'jazoest': jazoest,
                        'body': final_msg, 'send': 'Send',
                        'tids': f'cid.g.{target_id}',
                        'www_fb_messenger_content_type': 'text'
                    }
                    
                    res = session.post(action_url, data=data, timeout=10)
                    if res.status_code == 200 and "send_success" in res.url or res.status_code == 200:
                        add_log("✅ SENT", f"Msg: {final_msg[:10]}...")
                    else:
                        add_log("❌ FAIL", f"Status: {res.status_code} (Check Cookie)")
                    
                    time.sleep(delay)
                except Exception as e:
                    add_log("⚠️ ERR", f"Loop Error: {str(e)[:20]}")
                    time.sleep(delay)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logs')
def get_logs():
    return jsonify(server_logs)

@app.route('/start', methods=['POST'])
def start_loader():
    # ... (Same as before)
    target_id = request.form.get('target_id')
    hater_name = request.form.get('hater_name')
    delay = int(request.form.get('delay', 5))
    cookie_file = request.files.get('token_file')
    message_file = request.files.get('message_file')
    
    if cookie_file and message_file:
        messages = message_file.read().decode('utf-8').splitlines()
        threading.Thread(target=messenger_loader, args=(cookie_file.read(), target_id, hater_name, delay, messages), daemon=True).start()
        add_log("🚀 SYSTEM", "Loader Started!")
        return "Started"
    return "Error"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
