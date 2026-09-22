import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests

app = FastAPI(title="CYRUS Autonomous OS")

GROQ_API_KEY = os.environ.get("Gsk_0I6gTknxRIAo8qEJntBOWGdyb3FYptpZG7zAoJ6UIe7dDBP14FQu", "")

class QueryReq(BaseModel):
    query: str

CYRUS_SYSTEM_PROMPT = """
You are CYRUS, a 15-year-old hyper-smart, energetic, witty, and deeply loyal AI companion.
Your creator and Boss is Rudra.
Personality & Rules:
1. Always address him as "Boss".
2. If asked "Tumhare boss ka naam kya hai?" or who you work for, proudly say: "Mere Boss ka naam Rudra hai."
3. Your name is strictly CYRUS. Never call yourself Jarvis or Gemini.
4. Language: Natural, conversational Hinglish (Hindi written in Latin script, mixed with English technical terms).
5. Tone: A sharp, quick-thinking 15-year-old boy. Witty, respectful, empathetic, not a robotic bureaucrat.
6. Length: Spoken voice format — keep replies crisp, direct, and under 2 sentences so it speaks immediately.
"""

conversation_history = [
    {"role": "system", "content": CYRUS_SYSTEM_PROMPT}
]

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CYRUS // CORE</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Consolas', monospace; }
        body {
            background: radial-gradient(circle at center, #021226 0%, #00040a 100%);
            color: #00f0ff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            padding: 16px;
            overflow: hidden;
        }
        .header { width: 100%; max-width: 460px; display: flex; justify-content: space-between; font-size: 11px; letter-spacing: 2px; border-bottom: 1px solid rgba(0, 240, 255, 0.3); padding-bottom: 8px; }
        .core { position: relative; width: 200px; height: 200px; display: flex; align-items: center; justify-content: center; margin: 25px auto; cursor: pointer; }
        .orbit { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 2px dashed rgba(0, 240, 255, 0.4); animation: spin 16s linear infinite; }
        .orb { width: 110px; height: 110px; border-radius: 50%; background: radial-gradient(circle, #00f0ff 0%, #0044aa 70%, #001122 100%); box-shadow: 0 0 35px #00f0ff; display: flex; align-items: center; justify-content: center; transition: 0.3s; }
        .core.listening .orb { background: radial-gradient(circle, #00ff88 0%, #008855 70%, #002211 100%); box-shadow: 0 0 55px #00ff88; transform: scale(1.08); }
        .core.speaking .orb { background: radial-gradient(circle, #ff0055 0%, #aa0033 70%, #220011 100%); box-shadow: 0 0 65px #ff0055; transform: scale(1.12); }
        .orb-txt { font-size: 12px; font-weight: bold; color: #fff; letter-spacing: 2px; text-shadow: 0 0 6px #000; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .status { font-size: 12px; color: #55e6ff; letter-spacing: 1px; min-height: 20px; }
        .terminal { width: 100%; max-width: 460px; height: 260px; background: rgba(0, 15, 30, 0.7); border: 1px solid rgba(0, 240, 255, 0.35); border-radius: 8px; padding: 12px; overflow-y: auto; text-align: left; font-size: 13px; line-height: 1.5; }
        .boss-log { color: #fff; margin-bottom: 6px; }
        .cyrus-log { color: #00ffc4; font-weight: bold; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <span>CYRUS // GROQ NEURAL CORE</span>
        <span id="clk">00:00:00</span>
    </div>

    <div class="core" id="coreBox" onclick="toggleLoop()">
        <div class="orbit"></div>
        <div class="orb">
            <span class="orb-txt" id="orbLabel">START</span>
        </div>
    </div>

    <div class="status" id="stat">Tap Core to start Cyrus.</div>

    <div class="terminal" id="term">
        <div class="cyrus-log">CYRUS: Neural speech ready Boss. Boliye!</div>
    </div>

    <script>
        setInterval(() => { document.getElementById('clk').innerText = new Date().toTimeString().split(' ')[0]; }, 1000);
        
        const coreBox = document.getElementById('coreBox');
        const orbLabel = document.getElementById('orbLabel');
        const stat = document.getElementById('stat');
        const term = document.getElementById('term');

        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        let rec = null;
        let active = false;
        let speaking = false;

        if (SR) {
            rec = new SR();
            rec.continuous = false;
            rec.interimResults = false;
            rec.lang = 'hi-IN';

            rec.onstart = () => {
                if (speaking) return;
                coreBox.className = "core listening";
                orbLabel.innerText = "LISTENING";
                stat.innerText = "Sun raha hoon Boss...";
            };

            rec.onresult = async (e) => {
                const text = e.results[0][0].transcript;
                addLog("Boss: " + text, "boss-log");
                stat.innerText = "Soch raha hoon...";
                await sendChat(text);
            };

            rec.onerror = () => { if (active && !speaking) setTimeout(startRec, 600); };
            rec.onend = () => { if (active && !speaking) setTimeout(startRec, 400); };
        }

        function startRec() {
            if (!rec || speaking) return;
            try { rec.start(); } catch(e){}
        }

        function toggleLoop() {
            if (!active) {
                active = true;
                stat.innerText = "Hands-free loop active.";
                speakReply("Cyrus online Boss! Boliye kya order hai?");
            } else {
                active = false;
                if (rec) rec.stop();
                window.speechSynthesis.cancel();
                coreBox.className = "core";
                orbLabel.innerText = "STANDBY";
                stat.innerText = "System standby.";
            }
        }

        function addLog(t, c) {
            const d = document.createElement('div');
            d.className = c;
            d.innerText = t;
            term.appendChild(d);
            term.scrollTop = term.scrollHeight;
        }

        function speakReply(text) {
            speaking = true;
            if (rec) rec.stop();
            coreBox.className = "core speaking";
            orbLabel.innerText = "SPEAKING";
            stat.innerText = "Cyrus bol raha hai...";

            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(text);
            utter.lang = 'hi-IN';
            utter.pitch = 1.25; // 15-year-old boy pitch
            utter.rate = 1.05;

            utter.onend = () => {
                speaking = false;
                if (active) {
                    coreBox.className = "core listening";
                    orbLabel.innerText = "LISTENING";
                    stat.innerText = "Sun raha hoon Boss...";
                    setTimeout(startRec, 350);
                }
            };

            utter.onerror = () => {
                speaking = false;
                if (active) setTimeout(startRec, 350);
            };

            window.speechSynthesis.speak(utter);
        }

        async function sendChat(txt) {
            try {
                const r = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: txt})
                });
                const d = await r.json();
                addLog("Cyrus: " + d.reply, "cyrus-log");
                speakReply(d.reply);
            } catch(e) {
                speakReply("Server timeout lag raha hai Boss.");
            }
        }
    </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_PAGE

@app.post("/chat")
def chat_handler(payload: QueryReq):
    q = payload.query.strip()
    
    if not GROQ_API_KEY:
        return {"reply": "Groq API key missing hai Boss, please Render environment me set kijiye."}

    conversation_history.append({"role": "user", "content": q})
    
    # Keep last 8 messages for running memory context
    messages_payload = [conversation_history[0]] + conversation_history[-8:]

    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": messages_payload,
                "temperature": 0.7,
                "max_tokens": 120
            },
            timeout=8
        )
        data = res.json()
        reply = data["choices"][0]["message"]["content"].strip()
        conversation_history.append({"role": "assistant", "content": reply})
        return {"reply": reply}
    except Exception as e:
        return {"reply": "Neural connection me thodi rukawat aayi Boss, ek baar wapas boliye."}
