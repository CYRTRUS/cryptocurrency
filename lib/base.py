from .debug import log

class BasePanel:
    """Base class for panels with WebSocket and stop logic."""
    def __init__(self):
        self.running = True
        self.ws = None

    def stop(self):
        log(self.__class__.__name__.upper(), "Stopping")
        self.running = False
        try:
            if self.ws:
                self.ws.close()
        except:
            pass
