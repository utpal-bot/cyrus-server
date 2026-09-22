import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Cyrus Jarvis Web UI")

class VoicePayload(BaseModel):
    query: str

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CYRUS - Personal AI Assistant</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #050b14; color: #00f0ff; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; text-align: center; }
        .hud-circle { width: 180px; height: 180px; border-radius: 50%; border: 4px solid #00f0ff; box-shadow: 0 0 30px #00f0ff, inset 0 0 20px #00f0ff; display: flex; align-items: center; justify-content: center; margin-bottom: 25px; cursor: pointer; transition: 0.3s; }
        .hud-circle.active { border-color: #ff0055; box-shadow: 0 0 40px #ff0055, inset 0 0 25px #ff0055; transform: scale(1.08); }
        .hud-circle span { font-size: 18px; font-weight: bold; letter-spacing: 2px; }
        .status-box { font-size: 15px; color: #7feaff; margin-bottom: 20px; min-height: 25px; padding: 0 15px; }
        .chat-box { width: 90%; max-width: 450px; background: rgba(0, 240, 255, 0.05); border: 1px solid rgba(0, 240, 255, 0.2); border-radius: 12px; padding: 15px; text-align: left; }
        .msg { margin: 8px 0; font-size: 14px; line-height: 1.4; }
        .user-msg { color: #fff; }
        .cyrus-msg { color: #00f0ff; font-weight: 600; }
    </style>
</head>
<body>

    <div class="hud-circle" id="micBtn" onclick="toggleListening()">
        <span id="btnText">TAP TO SPEAK</span>
    </div>

    <div class="status-box" id="status">Ready Boss. Tap the circle and speak!</div>

    <div class="chat-box" id="chat">
        <div class="msg cyrus-msg">Cyrus: System Online Boss. Ready for commands.</div>
    </div>

    <script>
        const micBtn = document.getElementById('micBtn');
        const btnText = document.getElementById('btnText');
        const statusBox = document.getElementById('status');
        const chatBox = document.getElementById('chat');

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition;
        let isListening = false;

        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'hi-IN';

            recognition.onstart = () => {
                isListening = true;
                micBtn.classList.add('active');
                btnText.innerText = "LISTENING...";
                statusBox.innerText = "Listening to you Boss...";
            };

            recognition.onresult = async (event) => {
                const speechResult = event.results[0][0].transcript;
                appendMsg("Boss: " + speechResult, "user-msg");
                statusBox.innerText = "Processing...";
                await sendToCyrus(speechResult);
            };

            recognition.onerror = (event) => {
                statusBox.innerText = "Recognition error: " + event.error;
                resetBtn();
            };

            recognition.onend = () => {
                resetBtn();
            };
        } else {
            statusBox.innerText = "Speech API not supported in this browser. Please use Chrome.";
        }

        function resetBtn() {
            isListening = false;
            micBtn.classList.remove('active');
            btnText.innerText = "TAP TO SPEAK";
        }

        function toggleListening() {
            if (!recognition) return;
            if (isListening) {
                recognition.stop();
            } else {
                recognition.start();
            }
        }

        function appendMsg(text, className) {
            const div = document.createElement('div');
            div.className = "msg " + className;
            div.innerText = text;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function speakText(text) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'hi-IN';
            utterance.rate = 1.0;
            window.speechSynthesis.speak(utterance);
        }

        async function sendToCyrus(text) {
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: text })
                });
                const data = await res.json();
                appendMsg("Cyrus: " + data.reply, "cyrus-msg");
                speakText(data.reply);
                statusBox.innerText = "Standing by Boss.";
            } catch (err) {
                statusBox.innerText = "Server error!";
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_ui():
    return HTML_CONTENT

@app.post("/chat")
def process_command(data: VoicePayload):
    cmd = data.query.lower().strip()

    # 1. Date Check
    if any(w in cmd for w in ["tarikh", "tareekh", "date", "din", "aaj"]):
        now = datetime.now()
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        dt = f"{now.day} {months[now.month - 1]} {now.year}"
        return {"reply": f"Boss, aaj tareekh hai {dt}."}

    # 2. Time Check
    if any(w in cmd for w in ["time", "samay", "waqt", "baje"]):
        now = datetime.now()
        tm = now.strftime("%I bajke %M minute %p")
        return {"reply": f"Boss, abhi samay ho raha hai {tm}."}

    # 3. Identity & Small Talk
    if any(w in cmd for w in ["kaun ho", "who are you", "naam kya"]):
        return {"reply": "Main Cyrus hoon, aapka personal Jarvis AI assistant."}

    if any(w in cmd for w in ["kaise ho", "kya haal"]):
        return {"reply": "Main hamesha ready hoon Boss. Aap bataiye aaj ka kya mission hai?"}

    return {"reply": f"Ji Boss, maine note kar liya: {cmd}"}
