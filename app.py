from flask import Flask, render_template, request
import requests
import time
import threading

app = Flask(__name__)

def cookie_loader(cookie_file_content, target_id, hater_name, delay, messages):
    cookies_list = cookie_file_content.decode('utf-8').splitlines()
    
    while True:
        for cookie in cookies_list:
            if not cookie.strip(): continue
            for msg in messages:
                if not msg.strip(): continue
                try:
                    final_msg = f"{hater_name} {msg}" if hater_name else msg
                    url = f"https://mbasic.facebook.com/a/comment.php?ft_ent_identifier={target_id}"
                    headers = {
                        'cookie': cookie.strip(),
                        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36'
                    }
                    data = {'comment_text': final_msg}
                    
                    response = requests.post(url, headers=headers, data=data)
                    print(f"[+] Status: {response.status_code} | Msg: {final_msg[:15]}...")
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
    delay = int(request.form.get('delay'))
    
    cookie_file = request.files['token_file']
    message_file = request.files['message_file']
    
    if cookie_file and message_file:
        cookie_content = cookie_file.read()
        messages = message_file.read().decode('utf-8').splitlines()
        
        thread = threading.Thread(target=cookie_loader, args=(cookie_content, target_id, hater_name, delay, messages))
        thread.daemon = True
        thread.start()
        return "<h1>Loader Started Successfully! System working in background.</h1>"
    return "Error: Files missing."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
