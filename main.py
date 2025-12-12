import tkinter as tk
from components.apps import ToggleableTickerApp

if __name__ == "__main__":
    root = tk.Tk()
    app = ToggleableTickerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
