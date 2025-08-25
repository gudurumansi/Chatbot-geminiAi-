import os, sys, json, datetime, pathlib, requests, re
from dotenv import load_dotenv
from calculator_tool import calculate

# ----------------------------
# Config
# ----------------------------
MODEL = "gemini-1.5-flash"
API_ROOT = "https://generativelanguage.googleapis.com/v1beta"

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("ERROR: API key not found. Please set GEMINI_API_KEY.")
    sys.exit(1)

# Logs
LOG_DIR = pathlib.Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "level2_log.jsonl"

# ----------------------------
# Gemini API
# ----------------------------
def gemini_generate(user_question: str) -> str:
    prompt = f"""You are a helpful assistant.
If the user asks about facts or explanations, answer normally.
Do NOT solve arithmetic problems yourself (the calculator tool handles that).
User asked: {user_question}
"""
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
# Detect math queries
# ----------------------------
def is_math_query(text: str) -> bool:
    """
    Detect if the user query looks like a math problem.
    """
    keywords = ["plus", "add", "minus", "subtract", "times", "multiply", "x", "divide", "divided by"]
    if any(kw in text.lower() for kw in keywords):
        return True
    # also check for numbers with math symbols
    return bool(re.search(r"\d+\s*[\+\-\*/]\s*\d+", text))


def extract_expression(text: str):
    """
    Extract a simple math expression from text.
    Converts words like 'times' -> '*', 'plus' -> '+', etc.
    """
    expr = text.lower()
    expr = expr.replace("times", "*").replace("x", "*")
    expr = expr.replace("plus", "+").replace("add", "+")
    expr = expr.replace("minus", "-").replace("subtract", "-")
    expr = expr.replace("multiply", "*")
    expr = expr.replace("divide", "/").replace("divided by", "/")

    # keep only digits and operators
    match = re.findall(r"[0-9\+\-\*/]+", expr)
    return "".join(match) if match else None

# ----------------------------
# Logging
# ----------------------------
def log_interaction(user_text: str, assistant_text: str):
    record = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "user": user_text,
        "assistant": assistant_text,
        "model": MODEL,
        "level": 2
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

# ----------------------------
# Main loop
# ----------------------------
def main():
    print("🤖 SmartStep Assistant (Level 2). Type 'exit' to quit.\n")
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

        if is_math_query(user_q):
            expr = extract_expression(user_q)
            if expr:
                answer = f"Answer: {calculate(expr)}"
            else:
                answer = "Sorry, I couldn’t parse the math expression."
        else:
            answer = gemini_generate(user_q)

        print(f"\nAssistant:\n{answer}\n")
        log_interaction(user_q, answer)

if __name__ == "__main__":
    main()
