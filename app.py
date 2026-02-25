import os
import requests
import threading
import time
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)
server_logs = []

def add_log(status, message):
    global server_logs
    t = time.strftime("%H:%M:%S")
    server_logs.append(f"[{t}] {status}: {message}")
    if len(server_logs) > 25: server_logs.pop(0)

def messenger_loader(cookie_content, target_id, hater_name, delay, messages):
    cookies = cookie_content.decode('utf-8').splitlines()
    
    while True:
        for ck in cookies:
            if not ck.strip(): continue
            
            session = requests.Session()
            # Professional Headers: Taki Facebook ko lage aap mobile se hain
            session.headers.update({
                'authority': 'mbasic.facebook.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'en-US,en;q=0.9',
                'cookie': ck.strip(),
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            })

            try:
                # Step 1: Check Login and Get Tokens
                res = session.get(f"https://mbasic.facebook.com/messages/read/?tid=cid.g.{target_id}", timeout=15)
                
                if "login_form" in res.text or "checkpoint" in res.text:
                    add_log("❌ FAIL", "Cookie Expire ya Checkpoint lag gaya!")
                    continue

                soup = BeautifulSoup(res.text, 'html.parser')
                form = soup.find('form', method='post')
                
                if not form:
                    add_log("⚠️ WARN", "Form nahi mila. Group ID check karein.")
                    continue

                action_url = "https://mbasic.facebook.com" + form['action']
                fb_dtsg = soup.find('input', {'name': 'fb_dtsg'})['value']
                jazoest = soup.find('input', {'name': 'jazoest'})['value']

                # Step 2: Send Messages
                for msg in messages:
                    if not msg.strip(): continue
                    final_msg = f"{hater_name} {msg}" if hater_name else msg
                    
                    data = {
                        'fb_dtsg': fb_dtsg,
                        'jazoest': jazoest,
                        'body': final_msg,
                        'send': 'Send'
                    }
                    
                    post_res = session.post(action_url, data=data, timeout=15)
                    
                    if post_res.status_code == 200:
                        add_log("✅ SENT", f"ID: {target_id} | Msg: {msg[:15]}...")
                    else:
                        add_log("❌ ERR", f"Failed Status: {post_res.status_code}")
                    
                    time.sleep(delay)

            except Exception as e:
                add_log("⚠️ SYSTEM", f"Error: {str(e)[:30]}")
                time.sleep(delay)

@app.route('/')
def index(): return render_template('index.html')

@app.route('/logs')
def get_logs(): return jsonify(server_logs)

@app.route('/start', methods=['POST'])
def start_loader():
    target_id = request.form.get('target_id')
    hater_name = request.form.get('hater_name')
    delay = int(request.form.get('delay', 5))
    cookie_file = request.files.get('token_file')
    message_file = request.files.get('message_file')
    
    if cookie_file and message_file:
        messages = message_file.read().decode('utf-8').splitlines()
        cookie_data = cookie_file.read()
        threading.Thread(target=messenger_loader, args=(cookie_data, target_id, hater_name, delay, messages), daemon=True).start()
        add_log("🚀 START", "Loader Active Ho Gaya!")
        return "Success"
    return "Error"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
