import math

# ============================
#   MEMORY STORAGE
# ============================
memory = []


# ============================
#   EXPRESSION EVALUATION
# ============================
def calculate_expression(expr: str):
    try:
        expr = expr.replace("×", "*").replace("÷", "/").replace("−", "-")
        return eval(expr)
    except Exception:
        return "Error"


# ============================
#   SAFE NUMBER CONVERSION
# ============================
def _safe_number(value):
    """Convert to float safely. Empty or invalid → 0."""
    try:
        return float(value)
    except Exception:
        return 0.0


# ============================
#   MEMORY FUNCTIONS
# ============================
def memory_store(value):
    num = _safe_number(value)
    memory.append(str(num))


def memory_add(value):
    num = _safe_number(value)

    if memory:
        memory[-1] = str(_safe_number(memory[-1]) + num)
    else:
        memory.append(str(num))


def memory_subtract(value):
    num = _safe_number(value)

    if memory:
        memory[-1] = str(_safe_number(memory[-1]) - num)
    else:
        memory.append(str(-num))


def memory_recall():
    return memory[-1] if memory else ""


def memory_clear():
    memory.clear()


def memory_list():
    return memory.copy()


# ============================
#   UNARY OPERATIONS
# ============================
def reciprocal(x):
    try:
        return 1 / float(x)
    except Exception:
        return "Error"


def square(x):
    try:
        return float(x) ** 2
    except Exception:
        return "Error"


def sqrt(x):
    try:
        return math.sqrt(float(x))
    except Exception:
        return "Error"


# ============================
#   SIGN TOGGLE
# ============================
def toggle_sign(x):
    try:
        return str(-float(x))
    except Exception:
        return x


# ============================
#   EDITING OPERATIONS
# ============================
def clear_entry(expr):
    return ""


def clear_all():
    return "", ""


def backspace(expr):
    return expr[:-1]


# ============================
#   PERCENTAGE
# ============================
def percentage(expr):
    try:
        return float(expr) / 100
    except Exception:
        return "Error"


# ============================
#   INPUT HELPERS
# ============================
def append_digit(expr, digit):
    return expr + digit


def append_decimal(expr):
    # Prevent multiple decimals in the current number

    if "." in expr.split()[-1]:
        return expr
    return expr + "."