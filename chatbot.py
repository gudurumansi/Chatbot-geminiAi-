import os, sys, json, time, datetime, pathlib
import requests
from dotenv import load_dotenv

# ----------------------------
# Config
# ----------------------------
MODEL = "gemini-1.5-flash"  # widely available, fast
API_ROOT = "https://generativelanguage.googleapis.com/v1beta"
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("ERROR: Set GEMINI_API_KEY (or GOOGLE_API_KEY) in your environment or .env")
    sys.exit(1)

# Logs
LOG_DIR = pathlib.Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "level1_log.jsonl"

# ----------------------------
# Prompt template (Level 1 rules)
# ----------------------------
SYSTEM_INSTRUCTIONS = """You are SmartStep, a CLI assistant.

OUTPUT RULES:
- Always answer with a clean, numbered, step-by-step explanation (3–7 concise steps).
- After the steps, include a one-line "**Answer:** ..." summary.
- NEVER perform arithmetic or provide numeric results of calculations (e.g., 15+23).
- If asked to calculate (addition, subtraction, multiplication, division, percent, etc.),
  politely refuse and say exactly: "I can’t calculate directly here; please use a calculator tool."
  Do not include the computed result or show any intermediate arithmetic.

STYLE:
- Be concise and accurate.
- Plain text only (no markdown tables).
"""

def build_user_prompt(user_question: str) -> str:
    return (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"User question:\n{user_question}\n\n"
        f"Follow the OUTPUT RULES and STYLE precisely."
    )

# ----------------------------
# Gemini REST call
# ----------------------------
def gemini_generate(prompt_text: str) -> str:
    url = f"{API_ROOT}/models/{MODEL}:generateContent?key={API_KEY}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt_text}]
            }
        ],
        # You can tweak this if you like
        "generationConfig": {"temperature": 0.6}
    }
    resp = requests.post(url, json=payload, timeout=45)
    resp.raise_for_status()
    data = resp.json()
    # Safely extract the first candidate’s text
    try:
        parts = data["candidates"][0]["content"]["parts"]
        text_chunks = [p.get("text", "") for p in parts]
        return "".join(text_chunks).strip()
    except Exception:
        return f"Sorry, I couldn’t generate a response. Raw: {json.dumps(data)[:400]}"

def append_log(user_text: str, model_text: str):
    record = {
        "ts": datetime.datetime.now(datetime.UTC).isoformat(),
        "model": MODEL,
        "user": user_text,
        "assistant": model_text,
        "level": 1
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def main():
    print("SmartStep (Level 1 — Gemini). Type 'exit' to quit.")
    while True:
        try:
            user_q = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_q:
            continue
        if user_q.lower() in {"exit", "quit"}:
            print("Bye!")
            break

        prompt = build_user_prompt(user_q)
        answer = gemini_generate(prompt)
        print("\nAssistant:\n" + answer)
        append_log(user_q, answer)

if __name__ == "__main__":
    main()
