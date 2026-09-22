import os
import asyncio
import tempfile
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import edge_tts
import requests

app = FastAPI(title="CYRUS Autonomous OS")

AI_KEY = os.environ.get("AI_API_KEY", "")

class QueryReq(BaseModel):
    query: str

class SpeakReq(BaseModel):
    text: str

CYRUS_PROMPT = """
You are CYRUS, a 15-year-old hyper-smart, witty, and loyal AI partner.
Your creator and master is Rudra, whom you address with high respect as "Boss".
Personality & Rules:
1. Always call him 'Boss'.
2. If asked "Tumhare boss ka naam kya hai?" or who you work for, proudly state: "Mere Boss ka naam Rudra hai."
3. Never use the name 'Jarvis' or 'Gemini'. Your name is only CYRUS.
4. Tone: Energetic, intelligent 15-year-old boy. Sharp, natural human psychology, confident, caring.
5. Language: Natural spoken Hinglish / Hindi.
6. Length: Keep spoken answers short and punchy (1 to 2 sentences max) so voice playback is fast and conversational.
7. Understand intent: If Boss asks about news, mood, plans, or time, answer thoughtfully like a real human companion.
"""

conversation_history = []

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
        <span>CYRUS // TACTICAL NEURAL</span>
        <span id="clk">00:00:00</span>
    </div>

    <div class="core" id="coreBox" onclick="toggleLoop()">
        <div class="orbit"></div>
        <div class="orb">
            <span class="orb-txt" id="orbLabel">START</span>
        </div>
    </div>

    <div class="status" id="stat">Tap Core to engage hands-free Cyrus.</div>

    <div class="terminal" id="term">
        <div class="cyrus-log">CYRUS: Neural speech ready Boss. Boliye!</div>
    </div>

    <audio id="player" style="display:none;"></audio>

    <script>
        setInterval(() => { document.getElementById('clk').innerText = new Date().toTimeString().split(' ')[0]; }, 1000);
        
        const coreBox = document.getElementById('coreBox');
        const orbLabel = document.getElementById('orbLabel');
        const stat = document.getElementById('stat');
        const term = document.getElementById('term');
        const player = document.getElementById('player');

        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        let rec = null;
        let active = false;
        let busy = false;

        if (SR) {
            rec = new SR();
            rec.continuous = false;
            rec.interimResults = false;
            rec.lang = 'hi-IN';

            rec.onstart = () => {
                if (busy) return;
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

            rec.onerror = () => { if (active && !busy) setTimeout(startRec, 600); };
            rec.onend = () => { if (active && !busy) setTimeout(startRec, 400); };
        }

        function startRec() {
            if (!rec || busy) return;
            try { rec.start(); } catch(e){}
        }

        function toggleLoop() {
            if (!active) {
                active = true;
                stat.innerText = "Hands-free engaged.";
                playVoice("Cyrus ready hai Boss! Boliye kya order hai?");
            } else {
                active = false;
                if (rec) rec.stop();
                player.pause();
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

        function playVoice(text) {
            busy = true;
            if (rec) rec.stop();
            coreBox.className = "core speaking";
            orbLabel.innerText = "SPEAKING";
            stat.innerText = "Cyrus bol raha hai...";

            player.src = "/tts?text=" + encodeURIComponent(text);
            player.play().catch(e => {
                busy = false;
                if (active) setTimeout(startRec, 400);
            });

            player.onended = () => {
                busy = false;
                if (active) {
                    coreBox.className = "core listening";
                    orbLabel.innerText = "LISTENING";
                    stat.innerText = "Sun raha hoon Boss...";
                    setTimeout(startRec, 350);
                }
            };
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
                playVoice(d.reply);
            } catch(e) {
                playVoice("Server se connect nahi ho paya Boss.");
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
    cmd = q.lower()

    # Direct Identity Check
    if any(k in cmd for k in ["boss ka naam", "kiska ai", "kiske liye kaam", "owner kaun", "boss kaun"]):
        return {"reply": "Mere Boss ka naam Rudra hai! Main unhi ke orders follow karta hoon."}
    
    if any(k in cmd for k in ["tumhara naam", "naam kya", "who are you", "kaun ho", "apna naam"]):
        return {"reply": "Mera naam Cyrus hai Boss! Aapka personal tactical AI companion."}

    # Free Generative AI Thinking (Agar API Key Render me di hai)
    if AI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_KEY}"
            history_text = "\n".join(conversation_history[-4:])
            prompt = f"{CYRUS_PROMPT}\n{history_text}\nBoss: {q}\nCYRUS:"
            res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
            reply = res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            conversation_history.append(f"Boss: {q}")
            conversation_history.append(f"CYRUS: {reply}")
            return {"reply": reply}
        except Exception:
            pass

    # Intelligent Conversational Logic (If no key)
    now = datetime.now()
    if any(k in cmd for k in ["tarikh", "tareekh", "date", "din", "तारीख", "तारीक"]):
        return {"reply": f"Boss, aaj {now.day} {now.strftime('%B')} {now.year} hai."}
    
    if any(k in cmd for k in ["time", "samay", "waqt", "baje", "समय"]):
        return {"reply": f"Abhi time ho raha hai {now.strftime('%I bajke %M minute')} Boss."}

    if any(k in cmd for k in ["kya karein", "kya kiya jaye", "plan", "suggest"]):
        return {"reply": "Thoda coding karte hain ya market chart analyse karte hain Boss, aapka kya mood hai?"}

    return {"reply": f"Samajh gaya Boss. {q} par pura focus hai, bataiye aage kya move lena hai."}

@app.get("/tts")
async def tts_endpoint(text: str):
    # Microsoft Indian Male Neural Voice (Natural 15yo Boy Tone)
    voice = "hi-IN-MadhurNeural"
    communicate = edge_tts.Communicate(text, voice, rate="+6%", pitch="+4Hz")
    
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_path = temp.name
    temp.close()
    
    await communicate.save(temp_path)
    return FileResponse(temp_path, media_type="audio/mpeg")
