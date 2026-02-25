const fs = require("fs");
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
const wss = new WebSocket.Server({ server });

function sendLog(msg) {
  wss.clients.forEach(c => { if (c.readyState === WebSocket.OPEN) c.send(msg); });
}

const activeSessions = new Map();

// UI Code (Same as before)
app.get("/", (req, res) => {
  res.send(`... (Aapka purana HTML UI yahan rahega) ...`);
});

app.post("/start", upload.fields([{ name: 'cookieFile' }, { name: 'msgFile' }]), (req, res) => {
  const { group, hater_name, delay } = req.body;
  const cookieData = fs.readFileSync(req.files['cookieFile'][0].path, "utf8");
  const messages = fs.readFileSync(req.files['msgFile'][0].path, "utf8").split("\n").filter(l => l.trim() !== "");

  try {
    const appState = JSON.parse(cookieData);
    
    // YAHAN HAI ASLI POWER: Custom Options
    const options = {
      appState: appState,
      userAgent: "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    };

    fca(options, (err, api) => {
      if (err) {
        console.log(err);
        return sendLog("<b style='color:yellow'>[!] Login Error: " + (err.error || "Check your Cookie/2FA") + "</b>");
      }

      const sid = "YUVI_" + Math.random().toString(36).substr(2, 4).toUpperCase();
      sendLog("<b style='color:lime'>[SUCCESS] YUVI SERVER CONNECTED!</b>");

      let index = 0;
      const interval = setInterval(() => {
        if (index >= messages.length) index = 0;
        api.sendMessage(hater_name + " " + messages[index], group, (e) => {
          if (!e) {
            sendLog("[" + new Date().toLocaleTimeString() + "] ✅ Sent: " + messages[index].substring(0,10));
            index++;
          } else {
            sendLog("<b style='color:orange'>[!] Message Blocked by FB.</b>");
          }
        });
      }, delay * 1000);

      activeSessions.set(sid, { interval, api });
      res.json({ success: true });
    });
  } catch (e) {
    sendLog("<b style='color:red'>[X] JSON Format Error!</b>");
  }
});

server.listen(PORT, () => console.log("Server Live on " + PORT));
