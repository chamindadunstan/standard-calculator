import tkinter as tk
from operations import (
    calculate_expression, memory_store, memory_add, memory_subtract,
    memory_recall, memory_clear, memory_list, reciprocal, square, sqrt,
    toggle_sign,  backspace, percentage, format_number, format_result
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
last_was_operator = tk.BooleanVar(value=False)
history_popup = None
memory_popup = None


# ============================================================
#   MEMORY VALUE HELPER
# ============================================================
def get_memory_value():
    """Return only the current entry (bottom display) for memory operations."""
    val = result_var.get().strip()

    # Normalize invalid or empty values
    if val in ("", ".", "-"):
        return "0"

    return val


# EXPRESSION DISPLAY
expression_label = tk.Label(
    root,
    textvariable=expression_var,
    font=("Segoe UI", 14),
    anchor="e",
    bg="white"
)
expression_label.pack(fill="x", padx=10, pady=(10, 0))

# RESULT DISPLAY (Entry widget for selectable text)
result_entry = tk.Entry(
    root,
    textvariable=result_var,
    font=("Segoe UI", 28),
    justify="right",
    bd=0,
    relief="flat",
    readonlybackground="white",
    state="readonly"
)
result_entry.pack(fill="x", padx=10, pady=(0, 10))

# SET CURSOR STYLE
result_entry.configure(cursor="arrow")  # normal pointer

# CLICK TO COPY
result_entry.bind("<Button-1>", lambda e: copy_to_clipboard(result_var.get()))


# HOVER EFFECT
def on_result_enter(e):
    result_entry.config(readonlybackground="#e0e0e0")


def on_result_leave(e):
    result_entry.config(readonlybackground="white")


result_entry.bind("<Enter>", on_result_enter)
result_entry.bind("<Leave>", on_result_leave)


# ============================================================
#   HELPER WIDGETS (Hover + Click-to-Copy)
# ============================================================

def make_hover_label(parent, text, on_click=None):
    lbl = tk.Label(
        parent,
        text=text,
        anchor="e",
        justify="right",
        bg="#f0f0f0",
        padx=5,
        pady=2
    )

    # Hover highlight
    def on_enter(e):
        lbl.config(bg="#e0e0e0")

    def on_leave(e):
        lbl.config(bg="#f0f0f0")

    lbl.bind("<Enter>", on_enter)
    lbl.bind("<Leave>", on_leave)

    # Click handler (copy to clipboard)
    if on_click:
        lbl.bind("<Button-1>", lambda e: on_click(text))

    return lbl


# ============================================================
#   CLIPBOARD HELPER
# ============================================================

def copy_to_clipboard(value):
    root.clipboard_clear()
    root.clipboard_append(value)


# ============================================================
#   FLOATING HISTORY PANEL
# ============================================================

history_overlay = tk.Frame(root, bd=1, relief="solid", bg="#f0f0f0")
history_inner = tk.Frame(history_overlay, bg="#f0f0f0")
history_inner.pack(expand=True, fill="both")


def show_history_overlay():
    global history_popup

    # Destroy old popup if it exists
    try:
        history_popup.destroy()
    except Exception:
        pass

    history_popup = tk.Toplevel(root)
    history_popup.overrideredirect(True)
    history_popup.configure(bg="#f0f0f0", bd=1, relief="solid")

    x = history_btn.winfo_rootx()
    y = history_btn.winfo_rooty() + history_btn.winfo_height()
    history_popup.geometry(f"300x243+{x-264}+{y+27}")

    history_popup.bind("<FocusOut>", lambda e: hide_history_overlay())

    frame = tk.Frame(history_popup, bg="#f0f0f0")
    frame.pack(expand=True, fill="both")

    if not history_data:
        tk.Label(
            frame,
            text="There is no history yet.",
            anchor="nw",
            justify="left",
            bg="#f0f0f0",
            fg="gray"
        ).pack(expand=True, fill="both")
    else:
        for item in history_data:
            lbl = make_hover_label(frame, item, on_click=copy_to_clipboard)
            lbl.pack(fill="x")

        delete_btn = tk.Button(frame, text="🗑️", command=clear_history)
        delete_btn.place(x=258, y=214)


def hide_history_overlay():
    global history_popup
    if history_popup:
        history_popup.destroy()
        history_popup = None
        history_visible.set(False)


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
memory_inner = tk.Frame(memory_overlay, bg="#f0f0f0")
memory_inner.pack(expand=True, fill="both")


def handle_memory_action(action, value):
    if action == "MC":
        memory_clear()
    elif action == "M+":
        memory_add(value)
    elif action == "M-":
        memory_subtract(value)
    # Refresh panel to show updated memory
    show_memory_overlay()


def show_memory_overlay():
    global memory_popup
    try:
        memory_popup.destroy()
    except Exception:
        pass
    memory_popup = tk.Toplevel(root)
    memory_popup.overrideredirect(True)
    memory_popup.configure(bg="#f0f0f0", bd=1, relief="solid")

    x = mview_btn.winfo_rootx()
    y = mview_btn.winfo_rooty() + mview_btn.winfo_height()
    memory_popup.geometry(f"300x243+{x-251}+{y+1}")

    memory_popup.bind("<FocusOut>", lambda e: hide_memory_overlay())

    frame = tk.Frame(memory_popup, bg="#f0f0f0")
    frame.pack(expand=True, fill="both")

    mem = memory_list()

    if not mem:
        tk.Label(
            frame,
            text="There is nothing saved in memory.",
            anchor="nw",
            justify="left",
            bg="#f0f0f0",
            fg="gray"
        ).pack(expand=True, fill="both")

    else:
        for item in mem:

            # Outer container
            row = tk.Frame(frame, bg="white")
            row.pack(fill="x", pady=2)

            # TOP ROW: Memory value (Entry)
            value_entry = tk.Entry(
                row,
                font=("Segoe UI", 16),
                justify="right",
                bd=0,
                relief="flat",
                readonlybackground="white",
                state="readonly"
            )
            value_entry.insert(0, item)
            value_entry.configure(cursor="arrow")
            value_entry.pack(fill="x", padx=5, pady=(2, 0))

            # BOTTOM ROW: Buttons (hidden initially)
            button_row = tk.Frame(row, bg="white")
            button_row.pack(fill="x", padx=5, pady=(0, 4))
            button_row.pack_forget()

            # Create buttons
            buttons = []
            for btn_text in ["MC", "M+", "M-"]:
                btn = tk.Button(
                    button_row,
                    text=btn_text,
                    font=("Segoe UI", 10),
                    width=4,
                    relief="flat",
                    command=lambda
                    b=btn_text,
                    v=item: handle_memory_action(b, v)
                )
                btn.pack(side="left", padx=3)
                buttons.append(btn)

            # Hover functions
            def on_enter(e):
                row.config(bg="#e0e0e0")
                value_entry.config(readonlybackground="#e0e0e0")
                button_row.pack(fill="x", padx=5, pady=(0, 4))

            def on_leave(e):
                # Check if mouse is still inside the row
                x, y = row.winfo_pointerxy()
                widget_under_mouse = row.winfo_containing(x, y)
                if (widget_under_mouse and
                        widget_under_mouse.winfo_toplevel() ==
                        row.winfo_toplevel()):
                    return  # still inside, do nothing

                row.config(bg="white")
                value_entry.config(readonlybackground="white")
                button_row.pack_forget()

            # Bind hover to ALL widgets
            widgets = [row, value_entry, button_row] + buttons
            for w in widgets:
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)

        delete_btn = tk.Button(frame, text="🗑️", command=clear_memory)
        delete_btn.place(x=258, y=214)


def hide_memory_overlay():
    global memory_popup
    if memory_popup:
        memory_popup.destroy()
        memory_popup = None
        memory_visible.set(False)


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


def is_descendant(widget, ancestor):
    """Return True if widget is the ancestor or inside ancestor."""
    w = widget
    while w is not None:
        if w == ancestor:
            return True
        w = w.master
    return False


# ============================================================
#   CLICK OUTSIDE TO CLOSE PANELS
# ============================================================

def on_click_outside(event):
    widget = event.widget

    # Ignore clicks on toggle buttons
    if widget in (history_btn, mview_btn):
        return

    # If history popup exists and click is inside it → do nothing
    if history_visible.get() and history_popup is not None:
        if is_descendant(widget, history_popup):
            return

    # If memory popup exists and click is inside it → do nothing
    if memory_visible.get() and memory_popup is not None:
        if is_descendant(widget, memory_popup):
            return

    # Otherwise click is outside → close panels
    if history_visible.get():
        hide_history_overlay()
        history_visible.set(False)

    if memory_visible.get():
        hide_memory_overlay()
        memory_visible.set(False)


# Bind global click
root.bind_all(
    "<ButtonRelease-1>", lambda e: root.after(1, on_click_outside, e), add="+")


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
    command=lambda: (
        memory_clear(),
        update_memory_buttons(),
        just_evaluated.set(True),
        last_was_operator.set(False)
    )
)

mr_btn = tk.Button(
    mem_frame, text="MR",
    command=lambda: (
        result_var.set(memory_recall()),
        just_evaluated.set(True),
        last_was_operator.set(False)
    )
)

mplus_btn = tk.Button(
    mem_frame, text="M+",
    command=lambda: (
        memory_add(get_memory_value()),
        update_memory_buttons(),
        just_evaluated.set(True),
        last_was_operator.set(False)
    )
)

mminus_btn = tk.Button(
    mem_frame, text="M−",
    command=lambda: (
        memory_subtract(get_memory_value()),
        update_memory_buttons(),
        just_evaluated.set(True),
        last_was_operator.set(False)
    )
)

ms_btn = tk.Button(
    mem_frame, text="MS",
    command=lambda: (
        memory_store(get_memory_value()),
        update_memory_buttons(),
        just_evaluated.set(True),
        last_was_operator.set(False)
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
        formatted = format_number(result)

        expression_var.set(f"{expr} =")
        result_var.set(formatted)

        # Save formatted result to history
        history_data.insert(0, f"{expr} = {formatted}")

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

        current = expression_var.get()
        result = result_var.get()

        # === NUMBER BUTTONS ===
        if text.isdigit():
            if just_evaluated.get():
                expression_var.set("")
                result_var.set(text)
                just_evaluated.set(False)
                last_was_operator.set(False)
                return

            if last_was_operator.get():
                result_var.set(text)
                last_was_operator.set(False)
                return

            if result in ("", "0"):
                result_var.set(text)
            else:
                result_var.set(result + text)
            return

        # === DECIMAL POINT ===
        if text == ".":
            # After "=", start new entry "0."
            if just_evaluated.get():
                result_var.set("0.")
                expression_var.set("")
                just_evaluated.set(False)
                last_was_operator.set(False)
                return

            # After operator, start "0."
            if last_was_operator.get():
                result_var.set("0.")
                last_was_operator.set(False)
                return

            # Normal case
            if result in ("", "0"):
                result_var.set("0.")
            elif "." not in result:
                result_var.set(result + ".")
            return

        # === BASIC OPERATORS ===
        if text in ["+", "−", "×", "÷"]:
            current_bottom = result_var.get().strip()
            current_top = expression_var.get().strip()

            # Change operator if already present
            if current_top.endswith(("+", "−", "×", "÷")):
                expression_var.set(current_top[:-1] + text)
            else:
                expression_var.set(current_bottom + text)

            last_was_operator.set(True)
            just_evaluated.set(False)
            return

        # === PERCENTAGE ===
        if text == "%":
            result_var.set(str(percentage(result or current)))
            return

        # === CLEAR ENTRY ===
        if text == "CE":
            result_var.set("0")
            return

        # === CLEAR ALL ===
        if text == "C":
            expression_var.set("")
            result_var.set("0")
            just_evaluated.set(False)
            last_was_operator.set(False)
            return

        # === BACKSPACE ===
        if text == "⌫":
            # If result is active, backspace result
            if not just_evaluated.get() and not last_was_operator.get():
                result_var.set(backspace(result_var.get()))
                return

            # Otherwise backspace expression
            expression_var.set(backspace(expression_var.get()))
            return

        # === RECIPROCAL ===
        if text == "1/x":
            result_var.set(str(reciprocal(result or current)))
            just_evaluated.set(True)
            last_was_operator.set(False)
            return

        # === SQUARE ===
        if text == "x²":
            result_var.set(str(square(result or current)))
            just_evaluated.set(True)
            last_was_operator.set(False)
            return

        # === SQUARE ROOT ===
        if text == "²√x":
            result_var.set(str(sqrt(result or current)))
            just_evaluated.set(True)
            last_was_operator.set(False)
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
            top = expression_var.get().strip()
            bottom = result_var.get().strip()

            expr = top + bottom
            result = calculate_expression(expr)

            if result != "Error":
                formatted = format_result(result)

                expression_var.set(expr + " =")
                result_var.set(formatted)

                # newest history at top
                history_data.insert(0, f"{expr} = {formatted}")

                just_evaluated.set(True)
            else:
                result_var.set("Error")
                just_evaluated.set(False)

            last_was_operator.set(False)

            if history_visible.get():
                show_history_overlay()
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