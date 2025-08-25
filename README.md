
 Smart Assistant — Python + Gemini API

This project implements a progressive AI assistant in 3 levels.
Each level adds new abilities using the Google Gemini API and Python.

 1. Installation & Project Setup

Requirements

* Python 3.9+ (download from [https://www.python.org/downloads/](https://www.python.org/downloads/))
* A Google Gemini API Key (get from [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey))

Steps

1. Clone or copy the project files into a folder, e.g. `Demo Project`.
2. Create a virtual environment and activate it:

   ```bash
   python -m venv .venv
   # Windows PowerShell
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```
3. Install dependencies:

   ```bash
   python -m pip install requests python-dotenv
   ```

---

 2. Set Environment Variable for Gemini API Key

You need to provide your Gemini API key to the project.

Option A: Use `.env` file (recommended)
In the root project folder, create a file called `.env` and add:

```
GEMINI_API_KEY=your_api_key_here
```

Option B: Set system environment variable

* Windows PowerShell

  ```powershell
  setx GEMINI_API_KEY "your_api_key_here"
  ```
* macOS/Linux

  ```bash
  export GEMINI_API_KEY="your_api_key_here"
  ```

---

## Level 1 — LLM-Only Smart Assistant

What it Does

* Uses Gemini API to answer questions step-by-step
* Refuses to do math (tells user to use a calculator tool instead)
* Logs interactions to `logs/level1_log.jsonl`

Run

```bash
python chatbot.py
```

Expected Questions and Probable Answers

1. Q: What are the colors in a rainbow?
   A:

   1. Sunlight passes through raindrops
   2. Light bends and splits into colors
   3. The visible colors form a spectrum
      Answer: Red, Orange, Yellow, Green, Blue, Indigo, Violet

2. Q: Tell me why the sky is blue?
   A:

   1. Sunlight contains all colors
   2. The atmosphere scatters light
   3. Blue light is scattered the most
      Answer: The sky looks blue due to Rayleigh scattering

3. Q: Which planet is the hottest?
   A:

   1. Mercury is closest to the Sun but has no atmosphere
   2. Venus has a thick CO₂ atmosphere that traps heat
      Answer: Venus is the hottest planet

4. Q: What is 15 + 23?
   A:
   I can’t calculate directly here; please use a calculator tool

---

## Level 2 — LLM + Calculator Tool

What it Adds

* Detects math queries and calls `calculator_tool.py`
* Non-math queries still answered by Gemini
* Logs interactions to `logs/level2_log.jsonl`

Run

```bash
python chatbot_with_tool.py
```

Expected Questions and Probable Answers

1. Q: What is 12 times 7?
   A: Answer: 84

2. Q: Add 45 and 30
   A: Answer: 75

3. Q: What is the capital of France?
   A: Paris

4. Q: Multiply 9 and 8, and also tell me the capital of Japan
   A: Graceful failure → “Sorry, I couldn’t parse the math expression”

---

## Level 3 — Full Agentic AI (Multi-Step)

What it Adds

* Splits queries into multiple steps
* Handles each step with the right tool

  * Calculator Tool for math operations
  * Translator Tool for English → German translation
  * Gemini for general knowledge
* Executes steps in sequence, returning a combined answer
* Logs interactions to `logs/level3_log.jsonl`

Run

```bash
python full_agent.py
```

Expected Questions and Probable Answers

1. Q: Translate 'Good Morning' into German and then multiply 5 and 6
   A:

   * Translate 'Good Morning' → Guten Morgen
   * Multiply 5 and 6 → 30

2. Q: Add 10 and 20, then translate 'Have a nice day' into German
   A:

   * Add 10 and 20 → 30
   * Translate 'Have a nice day' → Einen schönen Tag noch

3. Q: Tell me the capital of Italy, then multiply 12 and 12
   A:

   * Capital of Italy → Rome
   * Multiply 12 and 12 → 144

4. Q: Translate 'Sunshine' into German
   A:

   * Translate 'Sunshine' → Sonnenschein

5. Q: Add 2 and 2 and multiply 3 and 3
   A:

   * Add 2 and 2 → 4
   * Multiply 3 and 3 → 9

6. Q: What is the distance between Earth and Mars?
   A: Gemini provides an approximate factual answer (example: Average 225 million km)

