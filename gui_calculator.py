import tkinter as tk

root = tk.Tk()
root.title("Standard Calculator")
root.geometry("320x420")
root.resizable(False, False)

# Two-line display
expression_var = tk.StringVar()
result_var = tk.StringVar()

expression_label = tk.Label(root, textvariable=expression_var,
                            font=("Segoe UI", 14), anchor="e", bg="white")
expression_label.pack(fill="x", padx=10, pady=(10, 0))

result_label = tk.Label(root, textvariable=result_var,
                        font=("Segoe UI", 24), anchor="e", bg="white")
result_label.pack(fill="x", padx=10, pady=(0, 10))

# Frame for buttons
btn_frame = tk.Frame(root)
btn_frame.pack(expand=True, fill="both", padx=10, pady=10)


def make_button(text, row, col, cmd=None, colspan=1):
    if cmd is None:
        def cmd(t=text):
            print(f"Pressed: {t}")
    btn = tk.Button(btn_frame, text=text, font=("Segoe UI", 12),
                    command=cmd)
    btn.grid(row=row, column=col, columnspan=colspan,
             sticky="nsew", padx=2, pady=2)


# Configure grid weights
for r in range(6):  # 6 rows of keys
    btn_frame.rowconfigure(r, weight=1)
for c in range(4):  # 4 columns
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
make_button("±", 5, 0)
make_button("0", 5, 1)
make_button(".", 5, 2)
make_button("=", 5, 3)

root.mainloop()