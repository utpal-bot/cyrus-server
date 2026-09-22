import os
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Cyrus Jarvis Brain")

class VoicePayload(BaseModel):
    query: str

@app.get("/")
def home():
    return {"status": "Cyrus Active"}

@app.post("/chat")
def chat(data: VoicePayload):
    cmd = data.query.lower().strip()
    
    # 1. Date & Time
    if any(w in cmd for w in ["tarikh", "tareekh", "date", "din"]):
        now = datetime.now()
        dt_str = now.strftime("%d %B %Y")
        return {"reply": f"Sir, aaj date hai {dt_str}.", "action": None}

    if any(w in cmd for w in ["time", "samay", "waqt"]):
        now = datetime.now()
        tm_str = now.strftime("%I bajke %M minute")
        return {"reply": f"Sir, abhi time ho raha hai {tm_str}.", "action": None}

    # 2. Hardware Control
    if "torch on" in cmd or "flashlight on" in cmd or "light on" in cmd:
        return {"reply": "Flashlight turned on, sir.", "action": "TORCH_ON"}

    if "torch off" in cmd or "flashlight off" in cmd or "light off" in cmd:
        return {"reply": "Flashlight turned off, sir.", "action": "TORCH_OFF"}

    # 3. Jarvis Personality / Greetings
    if any(w in cmd for w in ["kaise ho", "how are you", "kya haal"]):
        return {"reply": "All systems nominal sir. How can I help you today?", "action": None}

    if any(w in cmd for w in ["kaun ho", "who are you", "naam kya"]):
        return {"reply": "I am Cyrus, your personal artificial intelligence assistant.", "action": None}

    if any(w in cmd for w in ["so jao", "sleep", "good night", "band ho jao"]):
        return {"reply": "Entering standby mode. Good night sir.", "action": "SLEEP"}

    # 4. Default Assistant Answer
    return {"reply": f"Received your command, sir: {cmd}", "action": None}

