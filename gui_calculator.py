import tkinter as tk

root = tk.Tk()
root.title("Standard Calculator")
root.geometry("320x420")
root.minsize(320, 420)

# === Variables ===
expression_var = tk.StringVar()
result_var = tk.StringVar()
memory_data = []
history_data = []
memory_visible = tk.BooleanVar(value=False)
history_visible = tk.BooleanVar(value=False)

# === Display ===
expression_label = tk.Label(root, textvariable=expression_var,
                            font=("Segoe UI", 14), anchor="e", bg="white")
expression_label.pack(fill="x", padx=10, pady=(10, 0))

result_label = tk.Label(root, textvariable=result_var,
                        font=("Segoe UI", 24), anchor="e", bg="white")
result_label.pack(fill="x", padx=10, pady=(0, 10))

# ============================================================
#   FLOATING HISTORY PANEL
# ============================================================

history_overlay = tk.Frame(root, bd=1, relief="solid", bg="#f0f0f0")


def show_history_overlay():
    x = history_btn.winfo_rootx() - root.winfo_rootx()
    y = (history_btn.winfo_rooty() - root.winfo_rooty() +
         history_btn.winfo_height())

    history_overlay.place(x=x-264, y=y+25, width=300, height=250)
    history_overlay.lift()

    for w in history_overlay.winfo_children():
        w.destroy()

    for item in history_data:
        tk.Label(
            history_overlay, text=item, anchor="w", bg="#f0f0f0"
            ).pack(fill="x", padx=5, pady=2)

    tk.Button(
        history_overlay, text="🗑️", command=clear_history
        ).place(x=260, y=220)


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

    memory_overlay.place(x=x-252, y=y, width=300, height=250)
    memory_overlay.lift()

    for w in memory_overlay.winfo_children():
        w.destroy()

    for item in memory_data:
        tk.Label(
            memory_overlay, text=item, anchor="w", bg="#f0f0f0"
            ).pack(fill="x", padx=5, pady=2)

    tk.Button(
        memory_overlay, text="🗑️", command=clear_memory
        ).place(x=260, y=220)


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
    memory_data.clear()
    memory_visible.set(False)
    hide_memory_overlay()
    update_memory_buttons()


# ============================================================
#   MEMORY BUTTON ROW
# ============================================================

mem_frame = tk.Frame(root)
mem_frame.pack(fill="x", padx=10)

mc_btn = tk.Button(mem_frame, text="MC", command=clear_memory)
mr_btn = tk.Button(
    mem_frame, text="MR",
    command=lambda: result_var.set(memory_data[-1] if memory_data else "")
)
mplus_btn = tk.Button(
    mem_frame, text="M+",
    command=lambda: (
        memory_data.append(result_var.get()), update_memory_buttons())
)
mminus_btn = tk.Button(
    mem_frame, text="M−",
    command=lambda: (
        memory_data.append(f"-{result_var.get()}"), update_memory_buttons())
)
ms_btn = tk.Button(
    mem_frame, text="MS",
    command=lambda: (
        memory_data.append(result_var.get()), update_memory_buttons())
)
mview_btn = tk.Button(mem_frame, text="Mv", command=toggle_memory_panel)

# Pack all buttons in correct order
mc_btn.pack(side="left", expand=True, fill="x")
mr_btn.pack(side="left", expand=True, fill="x")
mplus_btn.pack(side="left", expand=True, fill="x")
mminus_btn.pack(side="left", expand=True, fill="x")
ms_btn.pack(side="left", expand=True, fill="x")
mview_btn.pack(side="left", expand=True, fill="x")


# Update button states based on memory
def update_memory_buttons():
    if memory_data:
        mc_btn.config(state="normal")
        mr_btn.config(state="normal")
        mview_btn.config(state="normal")
    else:
        mc_btn.config(state="disabled")
        mr_btn.config(state="disabled")
        mview_btn.config(state="disabled")


# ============================================================
#   BUTTON GRID
# ============================================================

btn_frame = tk.Frame(root)
btn_frame.pack(expand=True, fill="both", padx=10, pady=10)


def make_button(text, row, col, cmd=None, colspan=1):
    if cmd is None:
        def cmd(t=text):
            expression_var.set(expression_var.get() + t)
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


def calculate():
    try:
        expr = expression_var.get()
        expr = expr.replace("×", "*").replace("÷", "/").replace("−", "-")
        result = eval(expr)
        result_var.set(str(result))
        history_data.append(f"{expression_var.get()} = {result}")
        expression_var.set("")
        if history_visible.get():
            show_history_overlay()
    except Exception:
        result_var.set("Error")


make_button("±", 5, 0)
make_button("0", 5, 1)
make_button(".", 5, 2)
make_button("=", 5, 3, cmd=calculate)

root.mainloop()