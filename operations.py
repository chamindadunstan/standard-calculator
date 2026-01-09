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
#   NUMBER FORMATTER
# ============================

def format_number(value):
    """Return int-like numbers without .0, keep decimals otherwise."""
    try:
        num = float(value)
        if num.is_integer():
            return str(int(num))
        return str(num)
    except Exception:
        return value


def format_result(value):
    """Format final results: remove .0, limit long floats."""
    try:
        num = float(value)

        # If integer → return without decimals
        if num.is_integer():
            return str(int(num))

        # Limit to 10 decimal places, remove trailing zeros
        formatted = f"{num:.10f}".rstrip("0").rstrip(".")

        return formatted
    except Exception:
        return value


# ============================
#   MEMORY FUNCTIONS
# ============================
def memory_store(value):
    global memory
    num = _safe_number(value)
    memory.insert(0, format_number(num))


def memory_add(value):
    global memory
    num = _safe_number(value)
    if memory:
        memory[0] = format_number(_safe_number(memory[0]) + num)
    else:
        memory.insert(0, format_number(num))


def memory_subtract(value):
    global memory
    num = _safe_number(value)
    if memory:
        memory[0] = format_number(_safe_number(memory[0]) - num)
    else:
        memory.insert(0, format_number(-num))


def memory_recall():
    return memory[-1] if memory else ""


def memory_clear():
    memory.clear()


def memory_list():
    global memory

    return memory.copy()


# ============================
#   UNARY OPERATIONS
# ============================
def reciprocal(x):
    try:
        return format_number(1 / float(x))
    except Exception:
        return "Error"


def square(x):
    try:
        return format_number(float(x) ** 2)
    except Exception:
        return "Error"


def sqrt(x):
    try:
        return format_number(math.sqrt(float(x)))
    except Exception:
        return "Error"


# ============================
#   SIGN TOGGLE
# ============================
def toggle_sign(x):
    try:
        return format_number(-float(x))
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