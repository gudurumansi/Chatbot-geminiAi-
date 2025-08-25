# translator_tool.py
import os, requests
from dotenv import load_dotenv

MODEL = "gemini-1.5-flash"
API_ROOT = "https://generativelanguage.googleapis.com/v1beta"

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

def translate_to_german(text: str) -> str:
    if not API_KEY:
        return "Error: API key missing"

    prompt = f"Translate this English text into German only (no extra commentary): {text}"
    url = f"{API_ROOT}/models/{MODEL}:generateContent?key={API_KEY}"
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    try:
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts).strip()
    except Exception:
        return "⚠️ Translation failed"

# quick test
if __name__ == "__main__":
    print(translate_to_german("Good morning"))
