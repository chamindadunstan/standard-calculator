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
#   MEMORY FUNCTIONS
# ============================
def memory_store(value):
    memory.append(value)


def memory_add(value):
    if memory:
        memory[-1] = str(float(memory[-1]) + float(value))
    else:
        memory.append(value)


def memory_subtract(value):
    if memory:
        memory[-1] = str(float(memory[-1]) - float(value))
    else:
        memory.append("-" + value)


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
#   BINARY OPERATIONS
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
    if "." in expr.split()[-1]:
        return expr
    return expr + "."