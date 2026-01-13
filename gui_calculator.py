import tkinter as tk
from tkinter import ttk
from operations import (
    calculate_expression, memory_store, memory_add, memory_subtract,
    memory_recall, memory_clear, memory_list, reciprocal, square, sqrt,
    toggle_sign, percentage, format_number
)
from style import apply_styles

# === Main Window Setup ===
root = tk.Tk()
root.title("Standard Calculator")
root.geometry("320x420")
root.minsize(320, 420)

# === Apply Styles ===
apply_styles()


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
selected_history_row = None
selected_memory_row = None
history_popup = None
memory_popup = None
# ============================================================
#   INTERNAL STATE (Windows Mode A)
# ============================================================
current_value = ""        # number being typed
stored_value = None       # left operand
pending_operator = None   # operator waiting to be applied
last_operator = None      # for repeated equals
last_operand = None       # for repeated equals


def hide_history_overlay():
    """Close the history popup completely."""
    global history_popup, selected_history_row
    if history_popup is not None:
        try:
            history_popup.destroy()
        except Exception:
            pass
        history_popup = None
    selected_history_row = None
    history_visible.set(False)


def toggle_history_panel():
    """Toggle the history panel cleanly."""
    if history_visible.get():
        hide_history_overlay()
    else:
        hide_history_overlay()  # ensure no old popups remain
        show_history_overlay()
        history_visible.set(True)


# ============================================================
#   MEMORY VALUE HELPER
# ============================================================
def get_memory_value():
    val = result_var.get().strip()
    if val in ("", ".", "-"):
        return "0"
    return val


# EXPRESSION DISPLAY
expression_entry = tk.Label(
    root,
    textvariable=expression_var,
    font=("Segoe UI", 14),
    anchor="e",
    bg="white",
    padx=10,
    pady=10
)
expression_entry.pack(fill="x", padx=10, pady=(10, 0))

# RESULT DISPLAY (Entry widget for selectable text)
result_entry = tk.Entry(
    root,
    textvariable=result_var,
    font=("Segoe UI", 28),
    justify="right",
    bd=0,
    relief="flat",
    readonlybackground="white",
    state="readonly",
    cursor="arrow"
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


result_entry.bind("<Enter>", lambda e: result_entry.config
                  (readonlybackground="#e0e0e0"))
result_entry.bind("<Leave>", lambda e: result_entry.config
                  (readonlybackground="white"))


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
    global history_popup, selected_history_row, history_delete_btn
    selected_history_row = None

    # Destroy old popup if exists
    if history_popup is not None:
        try:
            history_popup.destroy()
        except Exception:
            pass
        history_popup = None

    # Create new popup
    history_popup = tk.Toplevel(root)
    history_popup.overrideredirect(True)
    history_popup.configure(bg="#f0f0f0", bd=1, relief="solid")

    resize_floating_panels()

    frame = tk.Frame(history_popup, bg="#f0f0f0")
    frame.pack(expand=True, fill="both")

    # Empty history
    if not history_data:
        tk.Label(
            frame,
            text="There is no history yet.",
            anchor="nw",
            justify="left",
            bg="#f0f0f0",
            fg="gray"
        ).pack(expand=True, fill="both")
        return

    #   BUILD HISTORY ROWS
    for item in history_data:
        # Split into expression and result
        if "=" in item:
            expr, result = item.split("=")
            expr = expr.strip() + " ="
            result = result.strip()
        else:
            expr = item
            result = ""
        # --- create row ---
        row = tk.Frame(frame, bg="white")
        row.pack(fill="x", pady=2)

        # Expression ENTRY
        expr_entry = tk.Entry(
            row,
            text=expr,
            font=("Segoe UI", 12),
            justify="right",
            bd=0,
            relief="flat",
            bg="white",
            readonlybackground="white",
            state="normal",
            cursor="arrow"
        )
        expr_entry.insert(0, expr)
        expr_entry.config(state="readonly")
        expr_entry.pack(fill="x", padx=5, pady=(2, 0))

        # Result label
        result_entry = tk.Entry(
            row,
            text=result,
            font=("Segoe UI", 16, "bold"),
            justify="right",
            bd=0,
            relief="flat",
            bg="white",
            readonlybackground="white",
            state="normal",
            cursor="arrow"
        )
        result_entry.insert(0, result)
        result_entry.config(state="readonly")
        result_entry.pack(fill="x", padx=5, pady=(2, 0))

        # CLICK HANDLER (H1: load expression + result)
        def on_click(event, entry, value):
            global selected_history_row
            global current_value, stored_value, pending_operator
            global last_operator, last_operand

            # Reset previous selection
            if selected_history_row and selected_history_row != entry:
                selected_history_row.config(
                    bg="white", readonlybackground="white")

            # Highlight selected entry
            entry.config(bg="#cce5ff", readonlybackground="#cce5ff")
            selected_history_row = entry

            # Copy to clipboard
            root.clipboard_clear()
            root.clipboard_append(value)

            # Select all text
            entry.config(state="normal")
            entry.selection_range(0, tk.END)
            entry.config(state="readonly")

            # --- H1 behavior: load expression + result into display ---
            if "=" in value:
                expr_raw, res_raw = value.split("=", 1)
                expr_raw = expr_raw.strip()
                res_raw = res_raw.strip()

                # Top: full expression with "="
                expression_var.set(expr_raw + " =")
                # Bottom: result
                result_var.set(res_raw)

                # Reset internal state for new calculations
                current_value = ""
                try:
                    stored_value = float(res_raw)
                except ValueError:
                    stored_value = None

                pending_operator = None
                last_operator = None
                last_operand = None
                just_evaluated.set(True)

        # Bind click to both rows
        expr_entry.bind("<Button-1>", lambda e, ent=expr_entry,
                        v=item: on_click(e, ent, v))
        result_entry.bind("<Button-1>", lambda e, ent=result_entry,
                          v=item: on_click(e, ent, v))

        # --- HOVER HANDLERS ---
        def on_enter(e, r=row):
            if (not selected_history_row or selected_history_row
               not in r.winfo_children()):
                r.config(bg="#e0e0e0")
                expr_entry.config(bg="#e0e0e0", readonlybackground="#e0e0e0")
                result_entry.config(bg="#e0e0e0", readonlybackground="#e0e0e0")

        def on_leave(e, r=row):
            if (not selected_history_row or selected_history_row
               not in r.winfo_children()):
                r.config(bg="white")
                expr_entry.config(bg="white", readonlybackground="white")
                result_entry.config(bg="white", readonlybackground="white")

        # Hover bindings
        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)
        expr_entry.bind("<Enter>", on_enter)
        expr_entry.bind("<Leave>", on_leave)
        result_entry.bind("<Enter>", on_enter)
        result_entry.bind("<Leave>", on_leave)

    # --- DELETE BUTTON ---
    delete_btn = tk.Button(frame, text="🗑️", command=clear_history)
    history_delete_btn = delete_btn
    delete_btn.place(x=0, y=0)

    resize_floating_panels()


# === History Button Above Display ===
history_top_frame = tk.Frame(root)
history_top_frame.pack(fill="x", padx=10, pady=(5, 0))

history_btn = tk.Button(
    history_top_frame,
    text="🕒",
    font=("Segoe UI", 12),
    relief="flat",
    bg="#f3f3f3",
    activebackground="#e0e0e0",
    bd=0,
    command=toggle_history_panel
)
history_btn.pack(side="right", padx=5)


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
    global memory_popup, selected_memory_row, memory_delete_btn
    selected_memory_row = None

    try:
        memory_popup.destroy()
    except Exception:
        pass

    memory_popup = tk.Toplevel(root)
    memory_popup.overrideredirect(True)
    memory_popup.configure(bg="#f0f0f0", bd=1, relief="solid")

    resize_floating_panels()

    frame = tk.Frame(memory_popup, bg="#f3f3f3", padx=8, pady=6)
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
        return

    for item in mem:

        row = tk.Frame(frame, bg="white")
        row.pack(fill="x", pady=2)

        value_entry = tk.Entry(
            row,
            font=("Segoe UI", 14),
            justify="right",
            bd=0,
            relief="flat",
            bg="white",
            readonlybackground="white",
            state="normal",
            cursor="arrow"
        )
        value_entry.insert(0, str(item))
        value_entry.config(state="readonly")
        value_entry.pack(fill="x", padx=5, pady=(2, 0))

        # BUTTON ROW (always visible)
        button_row = tk.Frame(row, bg="white")
        button_row.pack(fill="x", padx=5, pady=(0, 4))

        right_container = tk.Frame(button_row, bg="white")
        right_container.pack(side="right")

        buttons = []
        for btn_text in ["MC", "M+", "M-"]:
            btn = ttk.Button(
                right_container,
                text=btn_text,
                style="Memory.TButton",
                command=lambda b=btn_text, v=item: handle_memory_action(b, v)
            )
            btn.pack(side="left", padx=2)
            buttons.append(btn)

        # CLICK HANDLER
        def on_click_row(event, row=row, value=item):
            global selected_memory_row

            if selected_memory_row and selected_memory_row != row:
                selected_memory_row.config(bg="white")
                for child in selected_memory_row.winfo_children():
                    child.config(bg="white")
            # Apply blue highlight
            row.config(bg="#cce5ff")
            for child in row.winfo_children():
                child.config(bg="#cce5ff")

            selected_memory_row = row
            # Copy memory value
            root.clipboard_clear()
            root.clipboard_append(value)

        row.bind("<Button-1>", on_click_row)
        button_row.bind("<Button-1>", on_click_row)
    # --- DELETE BUTTON ---
    delete_btn = tk.Button(frame, text="🗑️", command=clear_memory)
    memory_delete_btn = delete_btn
    delete_btn.place(x=0, y=0)

    resize_floating_panels()


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
#   RESIZE HANDLER
# ============================================================
def resize_floating_panels(event=None):
    global history_popup, memory_popup
    global history_delete_btn, memory_delete_btn

    calc_x = root.winfo_rootx()
    calc_width = root.winfo_width()
    calc_height = root.winfo_height()

    new_width = calc_width - 20
    new_height = calc_height - 200
    if new_height < 150:
        new_height = 150

    # HISTORY PANEL
    if history_popup and history_popup.winfo_exists():
        btn_y = history_btn.winfo_rooty() + history_btn.winfo_height()
        new_x = calc_x + 10
        new_y = btn_y + 31

        history_popup.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")

        # Move delete button only if it still exists
        if ('history_delete_btn' in globals() and
           history_delete_btn.winfo_exists()):
            history_delete_btn.place(
                x=new_width - 43,
                y=new_height - 30
            )

    # MEMORY PANEL
    if memory_popup and memory_popup.winfo_exists():
        btn_y = mview_btn.winfo_rooty() + mview_btn.winfo_height()
        new_x = calc_x + 10
        new_y = btn_y + 5

        memory_popup.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")

        # Move delete button only if it still exists
        if ('memory_delete_btn' in globals() and
           memory_delete_btn.winfo_exists()):
            memory_delete_btn.place(
                x=new_width - 51,
                y=new_height - 36
            )


# Bind resize event (ALSO ADD HERE)
root.bind("<Configure>", resize_floating_panels)


# ============================================================
#   CLICK OUTSIDE TO CLOSE PANELS
# ============================================================

def on_click_outside(event):
    mouse_widget = root.winfo_containing(event.x_root, event.y_root)

    # Ignore clicks on toggle buttons
    if mouse_widget in (history_btn, mview_btn):
        return

    # If history popup exists and click is inside it → do nothing
    if history_visible.get() and history_popup is not None:
        if is_descendant(mouse_widget, history_popup):
            return

    # If memory popup exists and click is inside it → do nothing
    if memory_visible.get() and memory_popup is not None:
        if is_descendant(mouse_widget, memory_popup):
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
        global current_value, stored_value, pending_operator
        global last_operator, last_operand

        # text = btn_text  # however you pass the button text

        current = expression_var.get()
        result = result_var.get()

        # === NUMBER BUTTONS ===
        if text.isdigit():
            if just_evaluated.get():
                # Start new calculation
                current_value = text
                expression_var.set("")
                result_var.set(text)
                just_evaluated.set(False)
                return

            # Normal typing
            current_value += text
            result_var.set(current_value)
            return

        # === DECIMAL POINT ===
        if text == ".":
            if just_evaluated.get():
                current_value = "0."
                expression_var.set("")
                result_var.set("0.")
                just_evaluated.set(False)
                return

            if "." not in current_value:
                if current_value == "":
                    current_value = "0."
                else:
                    current_value += "."
                result_var.set(current_value)
            return

        # === BASIC OPERATORS ===
        if text in ["+", "−", "×", "÷"]:
            # If no stored value yet
            if stored_value is None:
                stored_value = float(current_value or "0")
                pending_operator = text
                expression_var.set(f"{format_number(stored_value)} {text}")
                current_value = ""
                just_evaluated.set(False)
                return

            # If operator exists, evaluate immediately
            if current_value != "":
                right = float(current_value)
                stored_value = calculate_expression(
                    f"{stored_value}{pending_operator}{right}")
                expression_var.set(f"{format_number(stored_value)} {text}")
                result_var.set(format_number(stored_value))

            pending_operator = text
            current_value = ""
            just_evaluated.set(False)
            return

        # === PERCENTAGE ===
        if text == "%":
            result_var.set(str(percentage(result or current)))
            return

        # === CLEAR ENTRY ===
        if text == "CE":
            current_value = ""
            result_var.set("0")
            return

        # === CLEAR ALL ===
        if text == "C":
            current_value = ""
            stored_value = None
            pending_operator = None
            last_operator = None
            last_operand = None
            expression_var.set("")
            result_var.set("0")
            just_evaluated.set(False)
            return

        # === BACKSPACE ===
        if text == "⌫":
            if not just_evaluated.get():
                current_value = current_value[:-1]
                result_var.set(current_value or "0")
            return

        # === RECIPROCAL ===
        if text == "1/x":
            if current_value == "":
                current_value = result_var.get()
            val = reciprocal(current_value)
            current_value = str(val)
            result_var.set(current_value)
            just_evaluated.set(True)
            return

        # === SQUARE ===
        if text == "x²":
            if current_value == "":
                current_value = result_var.get()
            val = square(current_value)
            current_value = str(val)
            result_var.set(current_value)
            just_evaluated.set(True)
            return

        # === SQUARE ROOT ===
        if text == "²√x":
            if current_value == "":
                current_value = result_var.get()
            val = sqrt(current_value)
            current_value = str(val)
            result_var.set(current_value)
            just_evaluated.set(True)
            return

        # === SIGN TOGGLE ===
        if text == "+/-":
            if current_value == "":
                current_value = result_var.get()
            current_value = str(toggle_sign(current_value))
            result_var.set(current_value)
            return

        # === EQUALS ===
        if text == "=":

            # Case 1: normal evaluation
            if pending_operator and current_value != "":
                left = stored_value
                right = float(current_value)
                op = pending_operator

                result = calculate_expression(f"{left}{op}{right}")

                # Save for repeated equals
                last_operator = op
                last_operand = right

                expression_var.set(
                    f"{format_number(left)} {op} {format_number(right)} =")
                result_var.set(format_number(result))

                # Save to history
                history_data.insert(
                        0,
                        f"{format_number(left)} {op} {format_number(right)} = "
                        f"{format_number(result)}"
                    )

                # Reset state
                stored_value = result
                current_value = ""
                pending_operator = None
                just_evaluated.set(True)
                return

            # Case 2: repeated equals
            if last_operator and stored_value is not None:
                left = stored_value
                right = last_operand
                op = last_operator

                result = calculate_expression(f"{left}{op}{right}")

                expression_var.set(
                    f"{format_number(left)} {op} {format_number(right)} =")
                result_var.set(format_number(result))

                # Save to history
                history_data.insert(
                    0,
                    f"{format_number(left)} {op} {format_number(right)} = "
                    f"{format_number(result)}"
                )

                stored_value = result
                just_evaluated.set(True)
                return

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