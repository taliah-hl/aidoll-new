# recorder.py
import sounddevice as sd
import soundfile as sf
import queue, threading, datetime, pathlib

class Recorder:
    """
    Simple async audio recorder  (start() / stop())
    ------------------------------------------------------------------
    * writes 16-bit little-endian WAV
    * default device = system default input
    * thread-safe: you can call stop() from another thread / GUI callback
    """
    def __init__(self, rate=48_000, channels=1, device=None, out_dir="recordings"):
        self.rate      = rate
        self.channels  = channels
        self.device    = device
        self.out_dir   = pathlib.Path(out_dir)
        self.out_dir.mkdir(exist_ok=True)
        self._q        = queue.Queue()
        self._running  = False

    # ---------------- public API ----------------
    def start(self):
        if self._running:
            print("Already recording!")
            return
        self._running = True

        ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # self._path = self.out_dir / f"rec_{ts}.wav"
        self._path = self.out_dir / f"record.wav"
        self._wav  = sf.SoundFile(self._path, mode='w', samplerate=self.rate,
                                  channels=self.channels, subtype='PCM_16')

        self._stream = sd.InputStream(samplerate=self.rate,
                                      channels=self.channels,
                                      device=self.device,
                                      callback=self._callback)
        self._stream.start()
        self._writer_th = threading.Thread(target=self._writer, daemon=True)
        self._writer_th.start()
        print(f"🔴  Recording → {self._path}")

    def stop(self):
        if not self._running:
            return
        self._running = False
        self._stream.stop();   self._stream.close()
        self._writer_th.join()            # wait for writer to flush queue
        self._wav.close()
        print(f"🟢  Saved  {self._path}")

    # --------------- internal helpers ---------------
    def _callback(self, indata, frames, time, status):
        if status:
            print("⚠️", status)
        self._q.put(indata.copy())

    def _writer(self):
        while self._running:
            self._wav.write(self._q.get())
        # flush anything left
        while not self._q.empty():
            self._wav.write(self._q.get())

# ----------- one-liner demo -----------
# if __name__ == "__main__":
#     rec = Recorder()          # 48 kHz, mono, default mic
#     rec.start()
#     input("Press Enter to stop…")
#     rec.stop()
