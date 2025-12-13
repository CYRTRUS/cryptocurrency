import tkinter as tk
from .debug import log

class BasePanel:
    """Base class for all panels with a Tkinter frame and stop logic."""
    def __init__(self, parent):
        self.parent = parent
        self.running = True
        self.frame = tk.Frame(parent)
    
    def safe_update(self, func, *args, **kwargs):
        """Safely update GUI from threads."""
        if self.running and getattr(self, "frame", None) and self.frame.winfo_exists():
            self.parent.after(0, lambda: func(*args, **kwargs))
    
    def stop(self):
        """Stop panel activity safely."""
        log("BASE_PANEL", f"Stopping {self.__class__.__name__}")
        self.running = False
