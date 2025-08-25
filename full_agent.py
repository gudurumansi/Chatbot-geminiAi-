import os, sys, json, datetime, pathlib, re, requests
from dotenv import load_dotenv
from calculator_tool import calculate
from translator_tool import translate_to_german

# ----------------------------
# Config
# ----------------------------
MODEL = "gemini-1.5-flash"
API_ROOT = "https://generativelanguage.googleapis.com/v1beta"

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("ERROR: API key not found")
    sys.exit(1)

# Logs
LOG_DIR = pathlib.Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "level3_log.jsonl"

# ----------------------------
# Gemini direct Q&A
# ----------------------------
def gemini_generate(user_question: str) -> str:
    prompt = f"You are a helpful assistant. Answer clearly.\nUser asked: {user_question}"
    url = f"{API_ROOT}/models/{MODEL}:generateContent?key={API_KEY}"
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts).strip()
    except Exception:
        return "⚠️ Could not parse response"

# ----------------------------
# Step detection
# ----------------------------
def split_into_steps(text: str):
    # crude split on "then" or "and then"
    return re.split(r"\bthen\b|\band\b", text, flags=re.IGNORECASE)

def is_math_query(text: str):
    keywords = ["plus", "add", "minus", "subtract", "times", "multiply", "x", "divide", "divided by"]
    return any(kw in text.lower() for kw in keywords) or bool(re.search(r"\d+\s*[\+\-\*/]\s*\d+", text))

def extract_expression(text: str):
    expr = text.lower()
    expr = expr.replace("times", "*").replace("x", "*")
    expr = expr.replace("plus", "+").replace("add", "+")
    expr = expr.replace("minus", "-").replace("subtract", "-")
    expr = expr.replace("multiply", "*")
    expr = expr.replace("divide", "/").replace("divided by", "/")
    match = re.findall(r"[0-9\+\-\*/]+", expr)
    return "".join(match) if match else None

def is_translation_query(text: str):
    return "translate" in text.lower() and "german" in text.lower()

# ----------------------------
# Logging
# ----------------------------
def log_interaction(user_text: str, assistant_text: str):
    record = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "user": user_text,
        "assistant": assistant_text,
        "model": MODEL,
        "level": 3
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

# ----------------------------
# Main agent loop
# ----------------------------
def main():
    print("🤖 SmartStep Agent (Level 3). Type 'exit' to quit.\n")
    while True:
        try:
            user_q = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_q:
            continue
        if user_q.lower() in {"exit", "quit"}:
            print("Bye!")
            break

        steps = split_into_steps(user_q)
        results = []
        for step in steps:
            step = step.strip()
            if not step:
                continue

            if is_translation_query(step):
                # Extract quoted text for translation
                match = re.findall(r"'(.*?)'", step)
                phrase = match[0] if match else step
                result = translate_to_german(phrase)
            elif is_math_query(step):
                expr = extract_expression(step)
                result = calculate(expr) if expr else "Could not parse math"
            else:
                result = gemini_generate(step)

            results.append(f"{step} → {result}")

        final_answer = "\n".join(results)
        print(f"\nAssistant:\n{final_answer}\n")
        log_interaction(user_q, final_answer)

if __name__ == "__main__":
    main()
