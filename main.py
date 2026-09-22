import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Cyrus Holographic Jarvis HUD")

class VoicePayload(BaseModel):
    query: str

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CYRUS - JARVIS HUD</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Courier New', Courier, monospace; }
        body {
            background: radial-gradient(circle at center, #021226 0%, #00040a 100%);
            color: #00f0ff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            padding: 20px 10px;
            overflow: hidden;
        }

        /* Top HUD Bar */
        .hud-header {
            width: 100%;
            max-width: 440px;
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            letter-spacing: 2px;
            border-bottom: 1px solid rgba(0, 240, 255, 0.3);
            padding-bottom: 8px;
            text-transform: uppercase;
        }

        /* Multicolored Iron Man Core Orb */
        .reactor-container {
            position: relative;
            width: 210px;
            height: 210px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 25px auto;
            cursor: pointer;
        }

        .ring-outer {
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 2px dashed #00f0ff;
            animation: spin 16s linear infinite;
        }

        .ring-middle {
            position: absolute;
            width: 82%;
            height: 82%;
            border-radius: 50%;
            border: 2px solid #00ffaa;
            border-top: 3px solid #ffcc00;
            animation: spinReverse 7s linear infinite;
        }

        .core-orb {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: radial-gradient(circle, #38ef7d 0%, #11998e 40%, #0f3443 85%);
            box-shadow: 0 0 45px #00ffaa, 0 0 15px #00f0ff;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.4s ease;
        }

        /* State Classes */
        .reactor-container.listening .core-orb {
            background: radial-gradient(circle, #00f0ff 0%, #0072ff 60%, #001233 90%);
            box-shadow: 0 0 60px #00f0ff, 0 0 25px #00ffff;
            transform: scale(1.08);
        }

        .reactor-container.speaking .core-orb {
            background: radial-gradient(circle, #ff007f 0%, #7928ca 60%, #1a0033 90%);
            box-shadow: 0 0 65px #ff007f, 0 0 25px #ff00a0;
            transform: scale(1.15);
        }

        .core-text {
            font-size: 13px;
            font-weight: bold;
            color: #ffffff;
            letter-spacing: 2px;
            text-align: center;
            text-shadow: 0 0 8px #000;
            pointer-events: none;
        }

        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        @keyframes spinReverse {
            from { transform: rotate(360deg); }
            to { transform: rotate(0deg); }
        }

        /* Status & Logs */
        .status-line {
            font-size: 13px;
            color: #4df3ff;
            letter-spacing: 1px;
            min-height: 22px;
            margin-bottom: 12px;
            text-shadow: 0 0 5px #00f0ff;
        }

        .hud-terminal {
            width: 100%;
            max-width: 440px;
            height: 250px;
            background: rgba(0, 15, 30, 0.65);
            border: 1px solid rgba(0, 240, 255, 0.35);
            border-radius: 8px;
            padding: 12px;
            overflow-y: auto;
            text-align: left;
            box-shadow: inset 0 0 15px rgba(0, 240, 255, 0.15);
        }

        .log-entry {
            margin-bottom: 8px;
            font-size: 13px;
            line-height: 1.4;
        }
        .log-boss { color: #ffffff; }
        .log-cyrus { color: #00ffc4; font-weight: bold; }

        .btn-panel {
            margin-top: 10px;
            display: flex;
            gap: 10px;
        }

        .toggle-btn {
            background: transparent;
            border: 1px solid #00f0ff;
            color: #00f0ff;
            padding: 8px 16px;
            font-size: 12px;
            border-radius: 4px;
            cursor: pointer;
            letter-spacing: 1px;
        }
        .toggle-btn:active { background: #00f0ff; color: #000; }
    </style>
</head>
<body>

    <div class="hud-header">
        <span>CYRUS // JARVIS OS v4.2</span>
        <span id="clock">00:00:00</span>
    </div>

    <div class="reactor-container" id="reactor" onclick="toggleAssistant()">
        <div class="ring-outer"></div>
        <div class="ring-middle"></div>
        <div class="core-orb" id="coreOrb">
            <span class="core-text" id="coreText">START</span>
        </div>
    </div>

    <div class="status-line" id="statusText">Tap Core to activate hands-free mode</div>

    <div class="hud-terminal" id="terminal">
        <div class="log-entry log-cyrus">CYRUS: Mark VII online. Hands-free loop ready.</div>
    </div>

    <div class="btn-panel">
        <button class="toggle-btn" onclick="toggleAssistant()">PAUSE / RESUME</button>
    </div>

    <script>
        setInterval(() => {
            const d = new Date();
            document.getElementById('clock').innerText = d.toTimeString().split(' ')[0];
        }, 1000);

        const reactor = document.getElementById('reactor');
        const coreText = document.getElementById('coreText');
        const statusText = document.getElementById('statusText');
        const terminal = document.getElementById('terminal');

        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognizer = null;
        let isRunning = false;
        let isSpeaking = false;

        if (SpeechRec) {
            recognizer = new SpeechRec();
            recognizer.continuous = false;
            recognizer.interimResults = false;
            recognizer.lang = 'hi-IN';

            recognizer.onstart = () => {
                if (isSpeaking) return;
                reactor.className = 'reactor-container listening';
                coreText.innerText = "LISTENING";
                statusText.innerText = "Listening to Boss...";
            };

            recognizer.onresult = async (event) => {
                const transcript = event.results[0][0].transcript;
                appendLog("BOSS: " + transcript, "log-boss");
                statusText.innerText = "Processing...";
                await sendToBrain(transcript);
            };

            recognizer.onerror = (e) => {
                // Background me restart loop automatically
                if (isRunning && !isSpeaking) {
                    setTimeout(() => startListening(), 800);
                }
            };

            recognizer.onend = () => {
                // If assistant is active and not speaking, auto-restart listening (Continuous Jarvis loop)
                if (isRunning && !isSpeaking) {
                    setTimeout(() => startListening(), 500);
                }
            };
        }

        function startListening() {
            if (!recognizer || isSpeaking) return;
            try { recognizer.start(); } catch (err) {}
        }

        function toggleAssistant() {
            if (!isRunning) {
                isRunning = true;
                statusText.innerText = "Jarvis Active. Hands-free loop engaged.";
                speakReply("Jarvis online Boss. All systems nominal. Boliye!");
            } else {
                isRunning = false;
                if (recognizer) recognizer.stop();
                window.speechSynthesis.cancel();
                reactor.className = 'reactor-container';
                coreText.innerText = "STANDBY";
                statusText.innerText = "Standby mode. Tap core to engage.";
            }
        }

        function appendLog(text, cls) {
            const p = document.createElement('div');
            p.className = 'log-entry ' + cls;
            p.innerText = text;
            terminal.appendChild(p);
            terminal.scrollTop = terminal.scrollHeight;
        }

        function speakReply(text) {
            isSpeaking = true;
            if (recognizer) recognizer.stop();

            reactor.className = 'reactor-container speaking';
            coreText.innerText = "SPEAKING";
            statusText.innerText = "Cyrus Speaking...";

            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(text);
            utter.lang = 'hi-IN';
            utter.rate = 1.05;

            utter.onend = () => {
                isSpeaking = false;
                if (isRunning) {
                    reactor.className = 'reactor-container listening';
                    coreText.innerText = "LISTENING";
                    statusText.innerText = "Listening...";
                    setTimeout(() => startListening(), 400);
                }
            };

            utter.onerror = () => {
                isSpeaking = false;
                if (isRunning) setTimeout(() => startListening(), 400);
            };

            window.speechSynthesis.speak(utter);
        }

        async function sendToBrain(text) {
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: text})
                });
                const data = await res.json();
                appendLog("CYRUS: " + data.reply, "log-cyrus");
                speakReply(data.reply);
            } catch (err) {
                speakReply("Server timeout Boss, please check connection.");
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

    # 1. Date Check (English + Devanagari Hindi support)
    date_keywords = ["tarikh", "tareekh", "date", "din", "aaj", "तारीख", "तारीक", "आज", "दिन"]
    if any(k in cmd for k in date_keywords):
        now = datetime.now()
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        dt = f"{now.day} {months[now.month - 1]} {now.year}"
        return {"reply": f"Boss, aaj tareekh hai {dt}."}

    # 2. Time Check
    time_keywords = ["time", "samay", "waqt", "baje", "समय", "वक्त", "टाइम", "बजे"]
    if any(k in cmd for k in time_keywords):
        now = datetime.now()
        tm = now.strftime("%I bajke %M minute")
        return {"reply": f"Boss, abhi waqt ho raha hai {tm}."}

    # 3. Identity / Name
    identity_keywords = ["naam", "name", "who are you", "kaun ho", "नाम", "कौन हो"]
    if any(k in cmd for k in identity_keywords):
        return {"reply": "Mera naam Cyrus hai Boss. Main aapka personal Iron Man Jarvis AI system hoon."}

    # 4. Status / Small talk
    greet_keywords = ["kaise ho", "kya haal", "hello", "hi", "हैलो", "कैसे हो", "हाल"]
    if any(k in cmd for k in greet_keywords):
        return {"reply": "All systems operational Boss. Main bilkul ready hoon, boliye agla order kya hai?"}

    return {"reply": f"Boss, command verify ho gaya hai: {data.query}"}
