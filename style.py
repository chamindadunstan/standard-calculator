from tkinter import ttk


def apply_styles():
    style = ttk.Style()
    style.theme_use("clam")  # clam respects custom colors

    style.configure(
        "Equals.TButton",
        font=("Segoe UI", 14),
        padding=10,
        background="#0078d7",
        foreground="white",
        relief="flat"
    )

    style.map(
        "Equals.TButton",
        background=[
            ("active", "#006cc1"),
            ("pressed", "#005a9e")
        ]
    )

    style.configure(
        "Memory.TButton",
        font=("Segoe UI", 9),
        padding=(3, 1),                # compact vertical height
        width=3,                       # fits "MC", "M+", "M-"
        relief="flat",
        borderwidth=1,
        background="white",
        foreground="black"
    )

    style.map(
        "Memory.TButton",
        background=[
            ("active", "#e0e0e0"),
            ("pressed", "#d0d0d0")
        ],
        foreground=[
            ("active", "black"),
            ("pressed", "black")
        ]
    )
