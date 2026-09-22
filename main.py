import os
import requests
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="CYRUS - Neural AI Partner")

AI_API_KEY = os.environ.get("AI_API_KEY", "")

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
            background: radial-gradient(circle at center, #010b19 0%, #000206 100%);
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
            border-bottom: 1px solid rgba(0, 240, 255, 0.25);
            padding-bottom: 8px;
        }

        /* Arc Core Container */
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
            animation: rotateClockwise 20s linear infinite;
        }

        .inner-ring {
            position: absolute;
            width: 80%;
            height: 80%;
            border-radius: 50%;
            border: 2px solid #00f0ff;
            border-top: 3px solid #ffaa00;
            animation: rotateCounter 8s linear infinite;
        }

        .pulsing-sphere {
            width: 115px;
            height: 115px;
            border-radius: 50%;
            background: radial-gradient(circle, #00f0ff 0%, #0044aa 70%, #001122 100%);
            box-shadow: 0 0 40px #00f0ff;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: 0.3s;
        }

        .core-container.listening .pulsing-sphere {
            background: radial-gradient(circle, #00ff88 0%, #008855 70%, #002211 100%);
            box-shadow: 0 0 60px #00ff88;
            transform: scale(1.08);
        }

        .core-container.speaking .pulsing-sphere {
            background: radial-gradient(circle, #ff0055 0%, #aa0033 70%, #220011 100%);
            box-shadow: 0 0 70px #ff0055;
            transform: scale(1.15);
        }

        .sphere-text {
            font-size: 13px;
            font-weight: bold;
            color: #ffffff;
            letter-spacing: 2px;
            text-shadow: 0 0 8px #000;
        }

        @keyframes rotateClockwise {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        @keyframes rotateCounter {
            from { transform: rotate(360deg); }
            to { transform: rotate(0deg); }
        }

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
        .msg-cyrus { color: #00f0ff; font-weight: 600; margin-bottom: 10px; }
    </style>
</head>
<body>

    <div class="hud-header">
        <span>CYRUS NEURAL OS</span>
        <span id="liveClock">00:00:00</span>
    </div>

    <div class="core-container" id="core" onclick="toggleLoop()">
        <div class="outer-ring"></div>
        <div class="inner-ring"></div>
        <div class="pulsing-sphere" id="sphere">
            <span class="sphere-text" id="sphereLabel">ENGAGE</span>
        </div>
    </div>

    <div class="status-bar" id="status">Tap the core to activate Cyrus.</div>

    <div class="terminal-log" id="terminal">
        <div class="msg-cyrus">CYRUS: All neural systems standing by, Boss.</div>
    </div>

    <script>
        setInterval(() => {
            const d = new Date();
            document.getElementById('liveClock').innerText = d.toTimeString().split(' ')[0];
        }, 1000);

        const core = document.getElementById('core');
        const sphereLabel = document.getElementById('sphereLabel');
        const statusText = document.getElementById('status');
        const terminal = document.getElementById('terminal');

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognizer = null;
        let isLoopActive = false;
        let isSpeaking = false;
        let maleVoice = null;

        // Load Male Voice
        function pickMaleVoice() {
            const voices = window.speechSynthesis.getVoices();
            // Male Hindi ya Deep English male voice choose karna
            maleVoice = voices.find(v => (v.name.includes("Male") || v.name.includes("David") || v.name.includes("Ravi") || v.name.includes("George")) && !v.name.includes("Female")) 
                        || voices.find(v => v.lang.includes("hi")) 
                        || voices[0];
        }

        window.speechSynthesis.onvoiceschanged = pickMaleVoice;
        pickMaleVoice();

        if (SpeechRecognition) {
            recognizer = new SpeechRecognition();
            recognizer.continuous = false;
            recognizer.interimResults = false;
            recognizer.lang = 'hi-IN';

            recognizer.onstart = () => {
                if (isSpeaking) return;
                core.className = "core-container listening";
                sphereLabel.innerText = "LISTENING";
                statusText.innerText = "Cyrus listening...";
            };

            recognizer.onresult = async (e) => {
                const text = e.results[0][0].transcript;
                appendLog("Boss: " + text, "msg-boss");
                statusText.innerText = "Processing logic...";
                await askBrain(text);
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
            try { recognizer.start(); } catch(err) {}
        }

        function toggleLoop() {
            if (!isLoopActive) {
                isLoopActive = true;
                statusText.innerText = "Hands-free loop engaged.";
                speakReply("Cyrus online Boss. All systems nominal. Main tayyar hoon.");
            } else {
                isLoopActive = false;
                if (recognizer) recognizer.stop();
                window.speechSynthesis.cancel();
                core.className = "core-container";
                sphereLabel.innerText = "STANDBY";
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
            sphereLabel.innerText = "SPEAKING";
            statusText.innerText = "Cyrus responding...";

            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(text);
            if (maleVoice) utter.voice = maleVoice;
            utter.lang = 'hi-IN';
            utter.pitch = 0.82; // Deep Male Pitch
            utter.rate = 1.0;

            utter.onend = () => {
                isSpeaking = false;
                if (isLoopActive) {
                    core.className = "core-container listening";
                    sphereLabel.innerText = "LISTENING";
                    statusText.innerText = "Cyrus listening...";
                    setTimeout(startListen, 400);
                }
            };

            utter.onerror = () => {
                isSpeaking = false;
                if (isLoopActive) setTimeout(startListen, 400);
            };

            window.speechSynthesis.speak(utter);
        }

        async function askBrain(query) {
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
                speakReply("Server synchronization error Boss.");
            }
        }
    </script>
</body>
</html>"""

# Cyrus Neural Persona & Memory
CYRUS_SYSTEM_PROMPT = """
You are CYRUS, a hyper-intelligent, loyal, tactical AI companion modeled with supreme intellect, sharp wit, and deep human psychological understanding.
You are talking to your creator/master, whom you address as "Boss" or "Sir".
Personality traits:
1. Name: Always CYRUS. Never refer to yourself as Jarvis or Gemini.
2. Tone: Calm, composed, mature, respectful, sharp, masculine, confident.
3. Language: Natural Hinglish / Hindi with English technical terms.
4. Response Length: Short, concise, punchy (1 to 2 sentences) — perfect for spoken conversations without boring monologue.
5. Behavior: Understand the intent, emotions, and practical requirements of Boss immediately.
"""

# Conversation History Context
conversation_memory = []

@app.get("/", response_class=HTMLResponse)
def get_ui():
    return HTML_CONTENT

@app.post("/chat")
def process_neural_query(data: VoicePayload):
    user_query = data.query.strip()
    now = datetime.now()
    dt_str = now.strftime("%d %B %Y, %I:%M %p")

    # If AI key exists, use generative brain
    if AI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_API_KEY}"
            prompt = f"{CYRUS_SYSTEM_PROMPT}\nCurrent Time: {dt_str}\nBoss: {user_query}\nCYRUS:"
            res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
            res_data = res.json()
            reply = res_data['candidates'][0]['content']['parts'][0]['text'].strip()
            return {"reply": reply}
        except Exception:
            pass

    # Tactical Fallback Brain (Instant response)
    cmd = user_query.lower()

    if any(k in cmd for k in ["tarikh", "tareekh", "date", "din", "aaj", "तारीख", "तारीक", "आज"]):
        return {"reply": f"Boss, aaj tareekh hai {now.day} {now.strftime('%B')} {now.year}."}

    if any(k in cmd for k in ["time", "samay", "waqt", "baje", "समय", "वक्त", "टाइम"]):
        return {"reply": f"Abhi waqt ho raha hai {now.strftime('%I bajke %M minute')} Boss."}

    if any(k in cmd for k in ["naam", "name", "kaun ho", "who are you", "नाम", "कौन हो"]):
        return {"reply": "Mera naam Cyrus hai Boss. Aapka dedicated AI tactical assistant."}

    if any(k in cmd for k in ["kaise ho", "kya haal", "हाल", "कैसे"]):
        return {"reply": "All systems operating at 100% efficiency Boss. Aap bataiye agla move kya hai?"}

    return {"reply": f"Aapka order note kar liya Boss. {user_query} par kaam shuru kar raha hoon."}
