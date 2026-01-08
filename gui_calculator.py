import tkinter as tk
from operations import (
    calculate_expression, memory_store, memory_add, memory_subtract,
    memory_recall, memory_clear, memory_list, reciprocal, square, sqrt,
    toggle_sign, clear_entry, clear_all, backspace, percentage,
    append_digit, append_decimal
)

# === Main Window Setup ===
root = tk.Tk()
root.title("Standard Calculator")
root.geometry("320x420")
root.minsize(320, 420)


# === Tooltip Helper Class ===
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw, text=self.text, justify="left",
            background="#ffffe0", relief="solid", borderwidth=1,
            font=("Segoe UI", 9)
        )
        label.pack(ipadx=4, ipady=2)

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


# === Variables ===
expression_var = tk.StringVar()
result_var = tk.StringVar()
history_data = []
memory_visible = tk.BooleanVar(value=False)
history_visible = tk.BooleanVar(value=False)

just_evaluated = tk.BooleanVar(value=False)


# ============================================================
#   MEMORY VALUE HELPER
# ============================================================
def get_memory_value():
    expr = expression_var.get().strip()
    res = result_var.get().strip()

    # If expression ends with "=", use result
    if expr.endswith("="):
        return res

    # If user is typing, use expression
    if expr:
        return expr

    # If no expression but result exists, use result
    if res:
        return res

    return "0"


# === Display ===
expression_label = tk.Label(
    root,
    textvariable=expression_var,
    font=("Segoe UI", 14),
    anchor="e",
    bg="white"
)
expression_label.pack(fill="x", padx=10, pady=(10, 0))

result_label = tk.Label(
    root,
    textvariable=result_var,
    font=("Segoe UI", 28),
    anchor="e",
    bg="white"
)
result_label.pack(fill="x", padx=10, pady=(0, 10))

# ============================================================
#   FLOATING HISTORY PANEL
# ============================================================

history_overlay = tk.Frame(root, bd=1, relief="solid", bg="#f0f0f0")


def show_history_overlay():
    x = history_btn.winfo_rootx() - root.winfo_rootx()
    y = (history_btn.winfo_rooty() - root.winfo_rooty() +
         history_btn.winfo_height())

    history_overlay.place(x=x-264, y=y+27, width=300, height=243)
    history_overlay.lift()

    for w in history_overlay.winfo_children():
        w.destroy()

    if not history_data:
        tk.Label(
            history_overlay,
            text="There is no history yet",
            anchor="center",
            bg="#f0f0f0",
            fg="gray"
        ).pack(expand=True, fill="both")
        return  # No delete button
    else:
        for item in history_data:
            tk.Label(
                history_overlay,
                text=item,
                anchor="w",
                bg="#f0f0f0"
            ).pack(fill="x", padx=5, pady=2)

        delete_btn = tk.Button(
            history_overlay, text="🗑️", command=clear_history)
        delete_btn.place(x=258, y=214)
        ToolTip(delete_btn, "Clear all history")


def hide_history_overlay():
    history_overlay.place_forget()


def toggle_history_panel():
    if history_visible.get():
        history_visible.set(False)
        hide_history_overlay()
    else:
        history_visible.set(True)
        show_history_overlay()


# === History Button Above Display ===
history_top_frame = tk.Frame(root)
history_top_frame.pack(fill="x", padx=10, pady=(5, 0))

history_btn = tk.Button(history_top_frame, text="🕒", font=("Segoe UI", 12),
                        command=toggle_history_panel)
history_btn.pack(side="right")


def clear_history():
    history_data.clear()
    hide_history_overlay()
    history_visible.set(False)


# ============================================================
#   FLOATING MEMORY PANEL
# ============================================================

memory_overlay = tk.Frame(root, bd=1, relief="solid", bg="#f0f0f0")


def show_memory_overlay():
    x = mview_btn.winfo_rootx() - root.winfo_rootx()
    y = mview_btn.winfo_rooty() - root.winfo_rooty() + mview_btn.winfo_height()

    memory_overlay.place(x=x-251, y=y+1, width=300, height=243)
    memory_overlay.lift()

    for w in memory_overlay.winfo_children():
        w.destroy()

    mem = memory_list()

    if not mem:
        tk.Label(
            memory_overlay,
            text="There is nothing saved in memory",
            anchor="center",
            bg="#f0f0f0",
            fg="gray"
        ).pack(expand=True, fill="both")
        return  # No delete button
    else:
        for item in mem:
            tk.Label(
                memory_overlay,
                text=item,
                anchor="w",
                bg="#f0f0f0"
            ).pack(fill="x", padx=5, pady=2)

        delete_btn = tk.Button(memory_overlay, text="🗑️", command=clear_memory)
        delete_btn.place(x=258, y=214)
        ToolTip(delete_btn, "Clear all memory")


def hide_memory_overlay():
    memory_overlay.place_forget()


def toggle_memory_panel():
    if memory_visible.get():
        memory_visible.set(False)
        hide_memory_overlay()
    else:
        memory_visible.set(True)
        show_memory_overlay()


def clear_memory():
    memory_clear()
    hide_memory_overlay()
    memory_visible.set(False)
    update_memory_buttons()


# ============================================================
#   MEMORY BUTTON STATE CONTROL
# ============================================================

def update_memory_buttons():
    if memory_list():  # use operations.py memory
        mc_btn.config(state="normal")
        mr_btn.config(state="normal")
        mview_btn.config(state="normal")
    else:
        mc_btn.config(state="disabled")
        mr_btn.config(state="disabled")
        mview_btn.config(state="disabled")


# ============================================================
#   MEMORY BUTTON ROW
# ============================================================

mem_frame = tk.Frame(root)
mem_frame.pack(fill="x", padx=10)

mc_btn = tk.Button(
    mem_frame, text="MC",
    command=lambda: (memory_clear(), update_memory_buttons())
)
mr_btn = tk.Button(
    mem_frame, text="MR",
    command=lambda: result_var.set(memory_recall())
)
mplus_btn = tk.Button(
    mem_frame, text="M+",
    command=lambda: (
        memory_add(get_memory_value()),
        update_memory_buttons()
    )
)

mminus_btn = tk.Button(
    mem_frame, text="M−",
    command=lambda: (
        memory_subtract(get_memory_value()),
        update_memory_buttons()
    )
)

ms_btn = tk.Button(
    mem_frame, text="MS",
    command=lambda: (
        memory_store(get_memory_value()),
        update_memory_buttons()
    )
)
mview_btn = tk.Button(mem_frame, text="Mv", command=toggle_memory_panel)

# Pack all buttons in correct order
mc_btn.pack(side="left", expand=True, fill="x")
mr_btn.pack(side="left", expand=True, fill="x")
mplus_btn.pack(side="left", expand=True, fill="x")
mminus_btn.pack(side="left", expand=True, fill="x")
ms_btn.pack(side="left", expand=True, fill="x")
mview_btn.pack(side="left", expand=True, fill="x")

# Initialize button states
update_memory_buttons()

# ============================================================
#   Tool Tips for Memory Buttons
# ============================================================
ToolTip(mc_btn, "Memory Clear")
ToolTip(mr_btn, "Memory Recall")
ToolTip(mplus_btn, "Add to Memory")
ToolTip(mminus_btn, "Subtract from Memory")
ToolTip(ms_btn, "Store in Memory")
ToolTip(mview_btn, "View Memory")


# ============================================================
#   CALCULATION FUNCTIONS
# ============================================================
def calculate():
    expr = expression_var.get()
    result = calculate_expression(expr)

    if result != "Error":
        expression_var.set(f"{expr} =")   # Show full expression with "="
        result_var.set(str(result))       # Show result below
        history_data.append(f"{expr} = {result}")
        just_evaluated.set(True)
    else:
        expression_var.set(expr)
        result_var.set("Error")
        just_evaluated.set(False)

    if history_visible.get():
        show_history_overlay()


# ============================================================
#   BUTTON GRID
# ============================================================

btn_frame = tk.Frame(root)
btn_frame.pack(expand=True, fill="both", padx=10, pady=10)


def make_button(text, row, col, colspan=1):
    def cmd():

        # === Clear expression after evaluation ===
        if just_evaluated.get():
            expression_var.set("")
            just_evaluated.set(False)

        current = expression_var.get()
        result = result_var.get()

        # === NUMBER BUTTONS ===
        if text.isdigit():
            expression_var.set(append_digit(current, text))
            return

        # === DECIMAL POINT ===
        if text == ".":
            expression_var.set(append_decimal(current))
            return

        # === BASIC OPERATORS ===
        if text in ["+", "−", "×", "÷"]:
            expression_var.set(current + text)
            return

        # === PERCENTAGE ===
        if text == "%":
            result_var.set(str(percentage(result or current)))
            return

        # === CLEAR ENTRY ===
        if text == "CE":
            expression_var.set(clear_entry(current))
            return

        # === CLEAR ALL ===
        if text == "C":
            expr, res = clear_all()
            expression_var.set(expr)
            result_var.set(res)
            return

        # === BACKSPACE ===
        if text == "⌫":
            expression_var.set(backspace(current))
            return

        # === RECIPROCAL ===
        if text == "1/x":
            result_var.set(str(reciprocal(result or current)))
            return

        # === SQUARE ===
        if text == "x²":
            result_var.set(str(square(result or current)))
            return

        # === SQUARE ROOT ===
        if text == "²√x":
            result_var.set(str(sqrt(result or current)))
            return

        # === SIGN TOGGLE ===
        if text == "+/-":
            # If result is showing, toggle that
            if result:
                new_val = str(toggle_sign(result))
                result_var.set(new_val)
                expression_var.set(new_val)
                return

            # If typing inside expression, toggle last number
            if current:
                # Find last number in expression
                import re
                parts = re.split(r'([+\-×÷])', current)

                if parts:
                    if parts[-1] == "":
                        return  # nothing to toggle

                    # Toggle last numeric part
                    parts[-1] = str(toggle_sign(parts[-1]))
                    new_expr = "".join(parts)

                    expression_var.set(new_expr)
                    result_var.set(parts[-1])
                return

        # === EQUALS ===
        if text == "=":
            calculate()
            return

    btn = tk.Button(btn_frame, text=text, font=("Segoe UI", 12), command=cmd)
    btn.grid(row=row, column=col, columnspan=colspan,
             sticky="nsew", padx=2, pady=2)


for r in range(6):
    btn_frame.rowconfigure(r, weight=1)
for c in range(4):
    btn_frame.columnconfigure(c, weight=1)

make_button("%",  0, 0)
make_button("CE", 0, 1)
make_button("C",  0, 2)
make_button("⌫",  0, 3)

make_button("1/x", 1, 0)
make_button("x²",  1, 1)
make_button("²√x", 1, 2)
make_button("÷",   1, 3)

make_button("7", 2, 0)
make_button("8", 2, 1)
make_button("9", 2, 2)
make_button("×", 2, 3)

make_button("4", 3, 0)
make_button("5", 3, 1)
make_button("6", 3, 2)
make_button("−", 3, 3)

make_button("1", 4, 0)
make_button("2", 4, 1)
make_button("3", 4, 2)
make_button("+", 4, 3)

make_button("+/-", 5, 0)
make_button("0", 5, 1)
make_button(".", 5, 2)
make_button("=", 5, 3)


# === Start the GUI Event Loop ===
root.mainloop()