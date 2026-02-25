const fs = require("fs");
const path = require("path");
const express = require("express");
const http = require("http");
const WebSocket = require("ws");
const fca = require("fca-mafiya");
const multer = require("multer");

const app = express();
const upload = multer({ dest: "uploads/" });
const server = http.createServer(app);
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const wss = new WebSocket.Server({ server });
function sendLog(msg) {
  wss.clients.forEach(c => { if (c.readyState === WebSocket.OPEN) c.send(msg); });
}

const activeSessions = new Map();

// ---------------- UI (BADMOSH LOOK) ----------------
app.get("/", (req, res) => {
  res.send(`
<!DOCTYPE html>
<html>
<head>
<title>YUVI BADMOSH SERVER</title>
<style>
    body{margin:0;background:#000;color:#fff;font-family:'Courier New',monospace;text-align:center}
    .box{max-width:450px;margin:20px auto;padding:20px;background:#0a0a0a;border-radius:10px;border:2px solid #ff0000;box-shadow:0 0 15px #ff0000}
    h1{color:#ff0000;text-shadow:2px 2px #550000;letter-spacing:3px;margin-bottom:5px}
    p.owner{font-size:12px;color:#888;margin-top:0}
    label{display:block;text-align:left;font-size:10px;color:#ff4444;margin:10px 0 2px 5px;font-weight:bold}
    input, button{width:100%;padding:12px;margin-bottom:10px;border-radius:5px;border:none;box-sizing:border-box}
    input{background:#1a1a1a;color:#fff;border:1px solid #333}
    input:focus{border:1px solid #ff0000;outline:none}
    .btn-start{background:#ff0000;color:#fff;font-weight:bold;cursor:pointer;font-size:16px;text-transform:uppercase}
    .btn-stop{background:#444;color:#fff;font-weight:bold;cursor:pointer;margin-top:5px}
    .logs{background:#050505;height:280px;overflow:auto;color:#ff3333;padding:15px;font-size:11px;text-align:left;border:1px solid #222;border-radius:5px;line-height:1.5}
    .status{color:#ff0000;font-size:12px;margin-bottom:15px;font-weight:bold}
</style>
</head>
<body>
<div class="box">
    <h1>YUVI BADMOSH</h1>
    <p class="owner">OFFICIAL LUXURY SERVER</p>
    <div class="status">
        [ SYSTEM: ONLINE ] | [ LOADERS: <span id="count">0</span> ]
    </div>
    <form id="loaderForm">
        <label>TARGET CONVO ID</label>
        <input type="text" name="group" placeholder="Enter Thread ID" required>
        
        <label>HATER NAME</label>
        <input type="text" name="hater_name" value="YUVI BADMOSH">
        
        <label>SELECT COOKIE (AppState JSON)</label>
        <input type="file" name="cookieFile" accept=".txt" required>
        
        <label>SELECT GALI FILE (.txt)</label>
        <input type="file" name="msgFile" accept=".txt" required>
        
        <label>DELAY (SECONDS)</label>
        <input type="number" name="delay" value="10" min="1">
        
        <button type="submit" class="btn-start">🔥 START ATTACK 🔥</button>
    </form>
    <button onclick="stopAll()" class="btn-stop">STOP ALL PROCESS</button>
    <div class="logs" id="logs">>> Waiting for Yuvi's Command...</div>
</div>
<script>
    const logs = document.getElementById("logs");
    const count = document.getElementById("count");
    const ws = new WebSocket((location.protocol === "https:" ? "wss://" : "ws://") + location.host);
    
    ws.onmessage = e => { 
        if(e.data.startsWith("COUNT:")){
            count.innerText = e.data.split(":")[1];
        } else {
            logs.innerHTML += e.data + "<br>"; 
            logs.scrollTop = logs.scrollHeight; 
        }
    };

    document.getElementById("loaderForm").onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        logs.innerHTML += "<b style='color:#fff'>[SYS] Badmosh Connection Building...</b><br>";
        await fetch("/start", { method: "POST", body: formData });
    };

    async function stopAll() {
        if(confirm("Band kar dein saare loaders?")){
            await fetch("/stop-all", { method: "POST" });
            logs.innerHTML += "<b style='color:#fff'>[STOP] Saare Loaders Rok Diye Gaye!</b><br>";
        }
    }
</script>
</body>
</html>`);
});

// ---------------- SERVER LOGIC ----------------
app.post("/start", upload.fields([{ name: 'cookieFile' }, { name: 'msgFile' }]), (req, res) => {
  const { group, hater_name, delay } = req.body;
  const hater = hater_name || "YUVI BADMOSH";
  
  const cookieData = fs.readFileSync(req.files['cookieFile'][0].path, "utf8");
  const messages = fs.readFileSync(req.files['msgFile'][0].path, "utf8").split("\n").filter(l => l.trim() !== "");

  try {
    const appState = JSON.parse(cookieData);
    fca.login({ appState }, (err, api) => {
      if (err) return sendLog("<b style='color:red'>[X] Login Fail! Cookie Check Kar.</b>");

      const sid = "YUVI_" + Math.random().toString(36).substr(2, 4).toUpperCase();
      sendLog("<b style='color:#ff0000'>[!] BADMOSH LOADER STARTED | GC: " + group + "</b>");

      let index = 0;
      const interval = setInterval(() => {
        if (index >= messages.length) index = 0;
        
        const fullMsg = hater + " " + messages[index];
        const time = new Date().toLocaleTimeString();

        api.sendMessage(fullMsg, group, (e) => {
          if (!e) {
            sendLog(\`[\${time}] ✅ \${hater} -> \${messages[index].substring(0,15)}...\`);
            index++;
          } else {
            sendLog(\`[\${time}] ❌ FAILED! Account/GC Issue.\`);
          }
        });
      }, delay * 1000);

      activeSessions.set(sid, { interval, api });
      sendLog("COUNT:" + activeSessions.size);
      res.json({ success: true });
    });
  } catch (e) {
    sendLog("<b style='color:red'>[X] ERROR: Cookie JSON format mein nahi hai!</b>");
  }
});

app.post("/stop-all", (req, res) => {
  activeSessions.forEach(s => clearInterval(s.interval));
  activeSessions.clear();
  sendLog("COUNT:0");
  res.json({ success: true });
});

server.listen(PORT, () => console.log("YUVI BADMOSH Server Live"));
