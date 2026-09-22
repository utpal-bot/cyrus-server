import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="CYRUS Autonomous OS")

class VoicePayload(BaseModel):
    query: str

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CYRUS // TACTICAL HUD</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Consolas', 'Courier New', monospace; }
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

        .hud-header {
            width: 100%;
            max-width: 480px;
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            letter-spacing: 2px;
            border-bottom: 1px solid rgba(0, 240, 255, 0.3);
            padding-bottom: 8px;
        }

        .core-container {
            position: relative;
            width: 220px;
            height: 220px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 20px auto;
            cursor: pointer;
        }

        .outer-ring {
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 2px dashed rgba(0, 240, 255, 0.4);
            animation: spinCW 18s linear infinite;
        }

        .inner-ring {
            position: absolute;
            width: 82%;
            height: 82%;
            border-radius: 50%;
            border: 2px solid #00f0ff;
            border-top: 3px solid #ffbb00;
            animation: spinCCW 7s linear infinite;
        }

        .core-orb {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: radial-gradient(circle, #00f0ff 0%, #0044aa 70%, #001122 100%);
            box-shadow: 0 0 40px #00f0ff;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: 0.3s;
        }

        .core-container.listening .core-orb {
            background: radial-gradient(circle, #00ff88 0%, #008855 70%, #002211 100%);
            box-shadow: 0 0 60px #00ff88;
            transform: scale(1.08);
        }

        .core-container.speaking .core-orb {
            background: radial-gradient(circle, #ff0055 0%, #aa0033 70%, #220011 100%);
            box-shadow: 0 0 70px #ff0055;
            transform: scale(1.15);
        }

        .core-text {
            font-size: 13px;
            font-weight: bold;
            color: #ffffff;
            letter-spacing: 2px;
            text-shadow: 0 0 8px #000;
        }

        @keyframes spinCW { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes spinCCW { from { transform: rotate(360deg); } to { transform: rotate(0deg); } }

        .status-bar {
            font-size: 12px;
            color: #55e6ff;
            letter-spacing: 1px;
            min-height: 20px;
            margin-bottom: 8px;
        }

        .terminal-log {
            width: 100%;
            max-width: 480px;
            height: 240px;
            background: rgba(0, 10, 25, 0.7);
            border: 1px solid rgba(0, 240, 255, 0.3);
            border-radius: 8px;
            padding: 12px;
            overflow-y: auto;
            text-align: left;
            font-size: 13px;
            line-height: 1.5;
        }

        .msg-boss { color: #ffffff; margin-bottom: 6px; }
        .msg-cyrus { color: #00ffc4; font-weight: bold; margin-bottom: 10px; }
    </style>
</head>
<body>

    <div class="hud-header">
        <span>CYRUS // AUTONOMOUS OS</span>
        <span id="liveClock">00:00:00</span>
    </div>

    <div class="core-container" id="core" onclick="toggleLoop()">
        <div class="outer-ring"></div>
        <div class="inner-ring"></div>
        <div class="core-orb" id="coreOrb">
            <span class="core-text" id="coreText">START</span>
        </div>
    </div>

    <div class="status-bar" id="status">Tap Core to engage Cyrus hands-free mode.</div>

    <div class="terminal-log" id="terminal">
        <div class="msg-cyrus">CYRUS: All tactical systems online, Boss.</div>
    </div>

    <script>
        setInterval(() => {
            const d = new Date();
            document.getElementById('liveClock').innerText = d.toTimeString().split(' ')[0];
        }, 1000);

        const core = document.getElementById('core');
        const coreText = document.getElementById('coreText');
        const statusText = document.getElementById('status');
        const terminal = document.getElementById('terminal');

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognizer = null;
        let isLoopActive = false;
        let isSpeaking = false;
        let maleVoice = null;

        function findMaleVoice() {
            const voices = window.speechSynthesis.getVoices();
            // Male voice choose karna
            maleVoice = voices.find(v => (v.name.includes("Male") || v.name.includes("David") || v.name.includes("Ravi") || v.name.includes("Mark")) && !v.name.includes("Female"))
                        || voices.find(v => v.lang.includes("hi"))
                        || voices[0];
        }

        window.speechSynthesis.onvoiceschanged = findMaleVoice;
        findMaleVoice();

        if (SpeechRecognition) {
            recognizer = new SpeechRecognition();
            recognizer.continuous = false;
            recognizer.interimResults = false;
            recognizer.lang = 'hi-IN';

            recognizer.onstart = () => {
                if (isSpeaking) return;
                core.className = "core-container listening";
                coreText.innerText = "LISTENING";
                statusText.innerText = "Listening to Boss...";
            };

            recognizer.onresult = async (e) => {
                const text = e.results[0][0].transcript;
                appendLog("Boss: " + text, "msg-boss");
                statusText.innerText = "Thinking...";
                await sendToBrain(text);
            };

            recognizer.onerror = () => {
                if (isLoopActive && !isSpeaking) {
                    setTimeout(startListen, 600);
                }
            };

            recognizer.onend = () => {
                if (isLoopActive && !isSpeaking) {
                    setTimeout(startListen, 400);
                }
            };
        }

        function startListen() {
            if (!recognizer || isSpeaking) return;
            try { recognizer.start(); } catch(e) {}
        }

        function toggleLoop() {
            if (!isLoopActive) {
                isLoopActive = true;
                statusText.innerText = "Hands-free loop engaged.";
                speakReply("Cyrus online Boss. Main tayyar hoon. Boliye!");
            } else {
                isLoopActive = false;
                if (recognizer) recognizer.stop();
                window.speechSynthesis.cancel();
                core.className = "core-container";
                coreText.innerText = "STANDBY";
                statusText.innerText = "System standby.";
            }
        }

        function appendLog(txt, cls) {
            const el = document.createElement('div');
            el.className = cls;
            el.innerText = txt;
            terminal.appendChild(el);
            terminal.scrollTop = terminal.scrollHeight;
        }

        function speakReply(text) {
            isSpeaking = true;
            if (recognizer) recognizer.stop();

            core.className = "core-container speaking";
            coreText.innerText = "SPEAKING";
            statusText.innerText = "Cyrus responding...";

            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(text);
            if (maleVoice) utter.voice = maleVoice;
            utter.lang = 'hi-IN';
            utter.pitch = 0.82; // Mature deep male pitch
            utter.rate = 1.05;

            utter.onend = () => {
                isSpeaking = false;
                if (isLoopActive) {
                    core.className = "core-container listening";
                    coreText.innerText = "LISTENING";
                    statusText.innerText = "Listening...";
                    setTimeout(startListen, 400);
                }
            };

            utter.onerror = () => {
                isSpeaking = false;
                if (isLoopActive) setTimeout(startListen, 400);
            };

            window.speechSynthesis.speak(utter);
        }

        async function sendToBrain(query) {
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query})
                });
                const data = await res.json();
                appendLog("Cyrus: " + data.reply, "msg-cyrus");
                speakReply(data.reply);
            } catch (err) {
                speakReply("Connection lost Boss.");
            }
        }
    </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def get_ui():
    return HTML_CONTENT

@app.post("/chat")
def process_command(data: VoicePayload):
    cmd = data.query.lower().strip()
    now = datetime.now()

    # 1. Date Check (English + Devanagari)
    if any(k in cmd for k in ["tarikh", "tareekh", "date", "din", "तारीख", "तारीक", "दिन", "आज"]):
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        dt = f"{now.day} {months[now.month - 1]} {now.year}"
        return {"reply": f"Boss, aaj tareekh hai {dt}."}

    # 2. Time Check
    if any(k in cmd for k in ["time", "samay", "waqt", "baje", "समय", "वक्त", "टाइम", "बजे"]):
        tm = now.strftime("%I bajke %M minute")
        return {"reply": f"Boss, abhi waqt ho raha hai {tm}."}

    # 3. Identity / Name
    if any(k in cmd for k in ["naam", "name", "kaun ho", "who are you", "नाम", "कौन"]):
        return {"reply": "Mera naam Cyrus hai Boss. Main aapka personal AI partner hoon."}

    # 4. Status / How are you
    if any(k in cmd for k in ["kaise ho", "kya haal", "theek ho", "हाल", "कैसे"]):
        return {"reply": "All systems nominal Boss. Main full power par active hoon. Boliye kya hukm hai?"}

    # 5. Deadlines / Tasks
    if any(k in cmd for k in ["deadline", "task", "kam", "काम", "टारगेट"]):
        return {"reply": "Boss, aapke high-priority deadlines database me secured hain. Next target par concentrate kijiye."}

    # 6. Gratitude / Casual
    if any(k in cmd for k in ["shukriya", "thanks", "dhanyawad", "good", "badhiya"]):
        return {"reply": "Pleasure is always mine, Boss."}

    # 7. Default Smart Tactical Response
    return {"reply": f"Understood Boss. {data.query} par main nazar banaye hue hoon."}
