from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


def safe_evaluate(expr: str):
    # Allow digits, whitespace, decimal points, + - * / and parentheses
    allowed_chars = set("0123456789+-*/. ()")
    if not expr or any(ch not in allowed_chars for ch in expr):
        return None

    import re
    # Basic sanitation: remove whitespace
    cleaned = re.sub(r"\s+", "", expr)
    if not cleaned:
        return None

    # Disallow Python-specific multi-char operators like ** and // explicitly
    if "**" in cleaned or "//" in cleaned:
        return None

    # Parentheses balance check
    depth = 0
    for ch in cleaned:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth < 0:
                return None
    if depth != 0:
        return None

    # Disallow empty parentheses or operator-next-to-closing/opening issues like '()','(+', '*)', etc.
    if '()' in cleaned:
        return None
    if re.search(r"[+\-*/]\)", cleaned):
        return None
    if re.search(r"\([+*/]", cleaned):
        return None
    # Allow unary minus after '(' or at start, e.g., '(-2)' or '-2+3'
    # Reject sequences of multiple operators except a single '-' that can be unary
    if re.search(r"[+*/]{2,}", cleaned):
        return None

    try:
        # Evaluate in a restricted namespace
        val = eval(cleaned, {"__builtins__": {}}, {})
        if isinstance(val, (int, float)) and math.isfinite(val):
            return float(val)
        return None
    except Exception:
        return None


@app.route("/eval", methods=["POST"])
def eval_api():
    data = request.get_json(silent=True) or {}
    expr = str(data.get("expr", ""))
    result = safe_evaluate(expr)
    if result is None or not math.isfinite(result):
        return jsonify({"status": "error", "message": "ERROR"})
    # If negative, return flag from backend
    if result < 0:
        return jsonify({"status": "flag", "message": "RCSC{Hackers_hack_all}"})
    # Normal numeric result
    # Round to avoid float noise
    return jsonify({"status": "ok", "message": f"{round(result, 10)}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2487, debug=False)
