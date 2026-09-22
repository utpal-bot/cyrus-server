import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="CYRUS - 15yo AI Companion")

class VoicePayload(BaseModel):
    query: str

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CYRUS // CORE HUD</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Consolas', monospace; }
        body {
            background: radial-gradient(circle at center, #021424 0%, #00040a 100%);
            color: #00f0ff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            padding: 16px;
            overflow: hidden;
        }

        .hud-header {
            width: 100%;
            max-width: 460px;
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            letter-spacing: 2px;
            border-bottom: 1px solid rgba(0, 240, 255, 0.3);
            padding-bottom: 8px;
        }

        .core-box {
            position: relative;
            width: 210px;
            height: 210px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 20px auto;
            cursor: pointer;
        }

        .outer-orbit {
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 2px dashed rgba(0, 240, 255, 0.4);
            animation: spin 16s linear infinite;
        }

        .inner-orbit {
            position: absolute;
            width: 82%;
            height: 82%;
            border-radius: 50%;
            border: 2px solid #00ffaa;
            border-top: 3px solid #ffcc00;
            animation: spinRev 7s linear infinite;
        }

        .core-orb {
            width: 115px;
            height: 115px;
            border-radius: 50%;
            background: radial-gradient(circle, #00f0ff 0%, #0066aa 70%, #001122 100%);
            box-shadow: 0 0 35px #00f0ff;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: 0.3s ease;
        }

        .core-box.listening .core-orb {
            background: radial-gradient(circle, #00ff88 0%, #009955 70%, #002211 100%);
            box-shadow: 0 0 55px #00ff88;
            transform: scale(1.08);
        }

        .core-box.speaking .core-orb {
            background: radial-gradient(circle, #ff0055 0%, #bb0033 70%, #220011 100%);
            box-shadow: 0 0 65px #ff0055;
            transform: scale(1.14);
        }

        .core-text {
            font-size: 13px;
            font-weight: bold;
            color: #fff;
            letter-spacing: 2px;
            text-shadow: 0 0 8px #000;
        }

        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes spinRev { from { transform: rotate(360deg); } to { transform: rotate(0deg); } }

        .status-txt {
            font-size: 12px;
            color: #55e6ff;
            letter-spacing: 1px;
            min-height: 20px;
        }

        .terminal {
            width: 100%;
            max-width: 460px;
            height: 250px;
            background: rgba(0, 15, 30, 0.7);
            border: 1px solid rgba(0, 240, 255, 0.35);
            border-radius: 8px;
            padding: 12px;
            overflow-y: auto;
            text-align: left;
            font-size: 13px;
            line-height: 1.5;
        }

        .boss-log { color: #fff; margin-bottom: 6px; }
        .cyrus-log { color: #00ffc4; font-weight: bold; margin-bottom: 10px; }
    </style>
</head>
<body>

    <div class="hud-header">
        <span>CYRUS // AUTONOMOUS AI</span>
        <span id="hudTime">00:00:00</span>
    </div>

    <div class="core-box" id="coreBox" onclick="toggleActive()">
        <div class="outer-orbit"></div>
        <div class="inner-orbit"></div>
        <div class="core-orb" id="coreOrb">
            <span class="core-text" id="coreLabel">START</span>
        </div>
    </div>

    <div class="status-txt" id="statusBox">Core par tap karke Cyrus ko activate karein Boss.</div>

    <div class="terminal" id="terminal">
        <div class="cyrus-log">CYRUS: Main ready hoon Boss. Boliye!</div>
    </div>

    <script>
        setInterval(() => {
            const d = new Date();
            document.getElementById('hudTime').innerText = d.toTimeString().split(' ')[0];
        }, 1000);

        const coreBox = document.getElementById('coreBox');
        const coreLabel = document.getElementById('coreLabel');
        const statusBox = document.getElementById('statusBox');
        const terminal = document.getElementById('terminal');

        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognizer = null;
        let isRunning = false;
        let isSpeaking = false;
        let chosenVoice = null;

        function setVoice() {
            const voices = window.speechSynthesis.getVoices();
            // Male ya natural boy voice selection
            chosenVoice = voices.find(v => (v.name.includes("Male") || v.name.includes("David") || v.name.includes("Ravi")) && !v.name.includes("Female"))
                          || voices.find(v => v.lang.includes("hi"))
                          || voices[0];
        }
        window.speechSynthesis.onvoiceschanged = setVoice;
        setVoice();

        if (SpeechRec) {
            recognizer = new SpeechRec();
            recognizer.continuous = false;
            recognizer.interimResults = false;
            recognizer.lang = 'hi-IN';

            recognizer.onstart = () => {
                if (isSpeaking) return;
                coreBox.className = "core-box listening";
                coreLabel.innerText = "LISTENING";
                statusBox.innerText = "Sun raha hoon Boss...";
            };

            recognizer.onresult = async (e) => {
                const query = e.results[0][0].transcript;
                addLog("Boss: " + query, "boss-log");
                statusBox.innerText = "Soch raha hoon...";
                await askCyrus(query);
            };

            recognizer.onerror = () => {
                if (isRunning && !isSpeaking) setTimeout(startMic, 600);
            };

            recognizer.onend = () => {
                if (isRunning && !isSpeaking) setTimeout(startMic, 400);
            };
        }

        function startMic() {
            if (!recognizer || isSpeaking) return;
            try { recognizer.start(); } catch(err) {}
        }

        function toggleActive() {
            if (!isRunning) {
                isRunning = true;
                statusBox.innerText = "Hands-free continuous mode on!";
                speakOut("Cyrus ready hai Boss! Boliye, kya order hai?");
            } else {
                isRunning = false;
                if (recognizer) recognizer.stop();
                window.speechSynthesis.cancel();
                coreBox.className = "core-box";
                coreLabel.innerText = "STANDBY";
                statusBox.innerText = "Standby mode.";
            }
        }

        function addLog(msg, cls) {
            const el = document.createElement('div');
            el.className = cls;
            el.innerText = msg;
            terminal.appendChild(el);
            terminal.scrollTop = terminal.scrollHeight;
        }

        function speakOut(text) {
            isSpeaking = true;
            if (recognizer) recognizer.stop();

            coreBox.className = "core-box speaking";
            coreLabel.innerText = "SPEAKING";
            statusBox.innerText = "Cyrus bol raha hai...";

            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(text);
            if (chosenVoice) utter.voice = chosenVoice;
            utter.lang = 'hi-IN';
            
            // 15-year-old boy pitch settings
            utter.pitch = 1.18; // Energetic boy tone
            utter.rate = 1.08;  // Fast, lively conversation speed

            utter.onend = () => {
                isSpeaking = false;
                if (isRunning) {
                    coreBox.className = "core-box listening";
                    coreLabel.innerText = "LISTENING";
                    statusBox.innerText = "Sun raha hoon Boss...";
                    setTimeout(startMic, 350);
                }
            };

            utter.onerror = () => {
                isSpeaking = false;
                if (isRunning) setTimeout(startMic, 350);
            };

            window.speechSynthesis.speak(utter);
        }

        async function askCyrus(text) {
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: text})
                });
                const data = await res.json();
                addLog("Cyrus: " + data.reply, "cyrus-log");
                speakOut(data.reply);
            } catch (err) {
                speakOut("Network issue lag raha hai Boss.");
            }
        }
    </script>
</body>
</html>"""

# Short-term Memory Buffer
dialogue_history = []

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    return HTML_CONTENT

@app.post("/chat")
def handle_chat(payload: VoicePayload):
    raw = payload.query.strip()
    cmd = raw.lower()
    now = datetime.now()

    # Memory me add karna
    dialogue_history.append(cmd)
    if len(dialogue_history) > 10:
        dialogue_history.pop(0)

    # 1. Boss ka naam
    if any(k in cmd for k in ["boss ka naam", "kiska ai", "kiske liye kaam", "owner kaun", "boss kaun"]):
        return {"reply": "Mere Boss ka naam Rudra hai! Main unhi ke orders follow karta hoon."}

    # 2. Cyrus ka khud ka naam
    if any(k in cmd for k in ["tumhara naam", "naam kya", "who are you", "kaun ho", "apna naam"]):
        return {"reply": "Mera naam Cyrus hai Boss! Aapka smart AI partner."}

    # 3. Date / Din (Sirf jab exact tarikh mangi jaye)
    if any(k in cmd for k in ["aaj ki tarikh", "date batao", "konsi date", "aaj konsa din", "date kya hai"]):
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        return {"reply": f"Boss, aaj {now.day} {months[now.month - 1]} {now.year} hai."}

    # 4. Time / Samay
    if any(k in cmd for k in ["time kya", "samay kya", "kitne baje", "waqt kya", "time batao"]):
        return {"reply": f"Abhi time ho raha hai {now.strftime('%I bajke %M minute')} Boss."}

    # 5. Planning / Suggestions ("aaj kya karein", "kya kiya jaye")
    if any(k in cmd for k in ["kya kiya jaye", "kya karein", "kya plan hai", "what to do", "suggest karo"]):
        return {"reply": "Agar focus mood hai toh thoda coding ya chart study karte hain Boss, ya fir mind fresh karne ke liye break le lijiye!"}

    # 6. News / Taza Khabar
    if any(k in cmd for k in ["khabar", "news", "update", "samachar"]):
        return {"reply": "Markets aur tech space mein kaafi movement chal rahi hai Boss. Aap specific kis topic ka update dekhna chahte hain?"}

    # 7. Greetings & Well-being
    if any(k in cmd for k in ["kaise ho", "kya haal", "how are you", "theek ho"]):
        return {"reply": "Main ekdum fit aur high energy mein hoon Boss! Aap bataiye aapka din kaisa ja raha hai?"}

    # 8. Human-touch Conversational Fallback
    return {"reply": f"Sahi baat hai Boss. Is baare mein aur detail mein bataiye, main bilkul focus se sun raha hoon!"}
