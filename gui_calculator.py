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

# === Panels ===
panel_frame = tk.Frame(root)
panel_frame.pack(fill="x", padx=10)

memory_panel = tk.Frame(panel_frame, bd=1, relief="solid", bg="#f8f8f8")
history_panel = tk.Frame(panel_frame, bd=1, relief="solid", bg="#f8f8f8")


def update_panels():
    for widget in memory_panel.winfo_children():
        widget.destroy()
    for widget in history_panel.winfo_children():
        widget.destroy()

    if memory_visible.get():
        for val in memory_data:
            tk.Label(memory_panel, text=val, anchor="e").pack(fill="x", padx=5)
        tk.Button(
            memory_panel, text="🗑️", command=clear_memory
            ).pack(anchor="e", padx=5, pady=5)
        memory_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))

    if history_visible.get():
        for val in history_data:
            tk.Label(
                history_panel, text=val, anchor="e").pack(fill="x", padx=5)
        tk.Button(history_panel, text="🗑️", command=clear_history
                  ).pack(anchor="e", padx=5, pady=5)
        history_panel.pack(side="right", fill="both", expand=True)


def clear_memory():
    memory_data.clear()
    memory_visible.set(False)
    update_memory_buttons()
    update_panels()


def clear_history():
    history_data.clear()
    history_visible.set(False)
    update_panels()


# === Top Buttons ===
top_frame = tk.Frame(root)
top_frame.pack(fill="x", padx=10)


def toggle_memory_panel():
    memory_visible.set(not memory_visible.get())
    update_panels()


def toggle_history_panel():
    history_visible.set(not history_visible.get())
    update_panels()


def update_memory_buttons():
    mc_btn.pack_forget()
    mr_btn.pack_forget()
    m_btn.pack_forget()
    if memory_data:
        mc_btn.pack(side="left", expand=True, fill="x")
        mr_btn.pack(side="left", expand=True, fill="x")
        m_btn.pack(side="left", expand=True, fill="x")


mc_btn = tk.Button(
    top_frame, text="MC", command=clear_memory)
mr_btn = tk.Button(
    top_frame, text="MR",
    command=lambda: result_var.set(memory_data[-1] if memory_data else ""))
mplus_btn = tk.Button(
    top_frame, text="M+", command=lambda: memory_data.append(result_var.get()))
mminus_btn = tk.Button(
    top_frame, text="M−",
    command=lambda: memory_data.append(f"-{result_var.get()}"))
ms_btn = tk.Button(
    top_frame, text="MS", command=lambda: memory_data.append(result_var.get()))
m_btn = tk.Button(top_frame, text="M", command=toggle_memory_panel)
clock_btn = tk.Button(top_frame, text="🕒", command=toggle_history_panel)

update_memory_buttons()
mplus_btn.pack(side="left", expand=True, fill="x")
mminus_btn.pack(side="left", expand=True, fill="x")
ms_btn.pack(side="left", expand=True, fill="x")
clock_btn.pack(side="right", padx=(5, 0))

# === Button Grid ===
btn_frame = tk.Frame(root)
btn_frame.pack(expand=True, fill="both", padx=10, pady=10)


def make_button(text, row, col, cmd=None, colspan=1):
    if cmd is None:
        def cmd(t=text):
            expression_var.set(expression_var.get() + t)
    btn = tk.Button(btn_frame, text=text, font=("Segoe UI", 12),
                    command=cmd)
    btn.grid(row=row, column=col, columnspan=colspan,
             sticky="nsew", padx=2, pady=2)


for r in range(6):
    btn_frame.rowconfigure(r, weight=1)
for c in range(4):
    btn_frame.columnconfigure(c, weight=1)

# Row 0: % CE C ⌫
make_button("%",  0, 0)
make_button("CE", 0, 1)
make_button("C",  0, 2)
make_button("⌫",  0, 3)

# Row 1: 1/x x² ²√x ÷
make_button("1/x", 1, 0)
make_button("x²",  1, 1)
make_button("²√x", 1, 2)
make_button("÷",   1, 3)

# Row 2: 7 8 9 ×
make_button("7", 2, 0)
make_button("8", 2, 1)
make_button("9", 2, 2)
make_button("×", 2, 3)

# Row 3: 4 5 6 −
make_button("4", 3, 0)
make_button("5", 3, 1)
make_button("6", 3, 2)
make_button("−", 3, 3)

# Row 4: 1 2 3 +
make_button("1", 4, 0)
make_button("2", 4, 1)
make_button("3", 4, 2)
make_button("+", 4, 3)


# Row 5: ± 0 . =
def calculate():
    try:
        expr = expression_var.get()
        expr = expr.replace("×", "*").replace("÷", "/").replace("−", "-")
        result = eval(expr)
        result_var.set(str(result))
        history_data.append(f"{expression_var.get()} = {result}")
        expression_var.set("")
        update_panels()
    except Exception:
        result_var.set("Error")


make_button("±", 5, 0)
make_button("0", 5, 1)
make_button(".", 5, 2)
make_button("=", 5, 3, cmd=calculate)

root.mainloop()