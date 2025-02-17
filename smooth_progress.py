from tqdm import tqdm
import time
import threading

class SmoothProgress:
    def __init__(self, total, desc="", unit="it"):
        self.pbar = tqdm(total=total, desc=desc, unit=unit, smoothing=0.1)
        self.current = 0
        self.total = total
        self.running = True
        self.thread = threading.Thread(target=self._smooth_update)
        self.thread.daemon = True
        self.lock = threading.Lock()

    def start(self):
        self.thread.start()

    def _smooth_update(self):
        while self.running:
            with self.lock:
                if self.pbar.n < self.current:
                    self.pbar.update(min(1, self.current - self.pbar.n))
            time.sleep(0.1)

    def update(self, n):
        with self.lock:
            self.current += n

    def set_description(self, desc):
        self.pbar.set_description(desc)

    def close(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
        self.pbar.n = self.total
        self.pbar.refresh()
        self.pbar.close() 