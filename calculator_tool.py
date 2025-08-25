# calculator_tool.py

def calculate(expression: str) -> str:
    """
    Very basic calculator.
    Supports +, -, *, / only.
    Example inputs: "12 * 7", "45 + 30"
    """
    try:
        # Security note: eval is dangerous in real apps, but okay for controlled demo
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception:
        return "Error: Unable to calculate"

# For quick testing
if __name__ == "__main__":
    while True:
        expr = input("Enter expression (or 'exit'): ")
        if expr.lower() == "exit":
            break
        print("Result:", calculate(expr))
