import os
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client

app = FastAPI(title="Cyrus Cloud Brain")

# Supabase Credentials
SUPABASE_URL = "https://osdhwbvmrxnpkueidmde.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9zZGh3YnZtcnhucGt1ZWlkbWRlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTAwNjk2MjgsImV4cCI6MjEwNTY0NTYyOH0.8AneNbVt9emHJVQs_sY6GqYFDUJNxxE0kJwxldXl8k0"  # <-- Is quotes ke andar apni anon public key paste karo

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class VoicePayload(BaseModel):
    query: str

@app.get("/")
def home():
    return {"status": "Cyrus Cloud Brain is Active & Standing By, Boss!"}

@app.post("/chat")
def process_command(data: VoicePayload):
    cmd = data.query.lower().strip()
    
    # 1. Standby / Sleep Commands
    if any(w in cmd for w in ["so jao", "shutdown", "good night", "standby"]):
        return {
            "reply": "Standby par ja raha hoon Boss. Good night, araam kijiye.", 
            "action": "SLEEP"
        }

    # 2. Date aur Time Check
    if any(w in cmd for w in ["tarikh", "date", "waqt", "time"]):
        now = datetime.now()
        formatted = now.strftime("%d %B %Y, waqt ho raha hai %I:%M %p")
        return {
            "reply": f"Boss, aaj tareekh hai {formatted}.", 
            "action": None
        }

    # 3. Mobile Hardware Control (Torch)
    if "torch on" in cmd or "flashlight on" in cmd:
        return {
            "reply": "Flashlight on kar di hai Boss.", 
            "action": "TORCH_ON"
        }
        
    if "torch off" in cmd or "flashlight off" in cmd:
        return {
            "reply": "Flashlight band kar di hai Boss.", 
            "action": "TORCH_OFF"
        }

    # 4. Note / Daily Memory Database me save karna
    try:
        supabase.table("daily_logs").insert({"entry": cmd}).execute()
        return {
            "reply": f"Ji Boss, maine note kar liya: '{cmd}'", 
            "action": None
        }
    except Exception as e:
        return {
            "reply": "Boss command sun li, par database save me dikkat aayi.", 
            "action": None
        }
