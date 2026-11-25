"""Wajeeha Transcribe - Windows GUI for Cactus Whistle (Needle) speech-to-text.

Audio in: browse a .wav file, or record from the microphone.
Output: transcript saved to a .txt file you choose.
Clips longer than 30 s are split automatically into ~28 s pieces.
"""
import os
import sys
import time
import wave
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --windowed builds have no console; some libraries print and would crash.
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

def app_dir():
    """Folder that holds the exe (or this script when run with python)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


APP_DIR = app_dir()
MODEL_PATH = os.path.join(APP_DIR, "models", "whistle.cact")
ENGINE_DIR = os.path.join(APP_DIR, "engine")


def setup_offline():
    """Point Needle at the model + engine shipped beside the exe.
    Returns a short message describing what was found."""
    have_model = os.path.isfile(MODEL_PATH)
    if have_model:
        os.environ["NEEDLE_WHISTLE_WEIGHTS"] = MODEL_PATH
    libs = []
    for root, _, files in os.walk(ENGINE_DIR):
        libs += [os.path.join(root, f) for f in files if f.lower().endswith(".dll")]
    libs.sort(key=lambda p: "needle" not in os.path.basename(p).lower())
    if libs:
        os.environ["NEEDLE3_LIB_PATH"] = libs[0]
    os.environ["NEEDLE_TELEMETRY"] = "0"
    os.environ["DO_NOT_TRACK"] = "1"
    if have_model and libs:
        os.environ["HF_HUB_OFFLINE"] = "1"
        return "Using model and engine from the app folder (offline)."
    missing = []
    if not have_model:
        missing.append("models\\whistle.cact")
    if not libs:
        missing.append("engine\\*.dll")
    return "Not found next to the exe: " + ", ".join(missing) + ". Will try to download (needs internet)."


import glob
import shutil


def _newest(pattern):
    files = glob.glob(pattern)
    return max(files, key=os.path.getmtime) if files else None


def _cache_files():
    """Where Needle puts its downloads: engine dll + whistle.cact."""
    base = os.path.join(os.path.expanduser("~"), ".cache", "cactus-needle")
    return (_newest(os.path.join(base, "v3", "*", "*.dll")),
            _newest(os.path.join(base, "whistle", "*", "whistle.cact")))


def models_present(dest):
    eng = os.path.join(dest, "engine")
    has_dll = any(f.lower().endswith(".dll") for _, _, fs in os.walk(eng) for f in fs)
    return os.path.isfile(os.path.join(dest, "models", "whistle.cact")) and has_dll


def copy_from_cache(dest):
    dll, cact = _cache_files()
    if not (dll and cact):
        return False
    os.makedirs(os.path.join(dest, "models"), exist_ok=True)
    os.makedirs(os.path.join(dest, "engine"), exist_ok=True)
    shutil.copy2(cact, os.path.join(dest, "models", "whistle.cact"))
    shutil.copy2(dll, os.path.join(dest, "engine", os.path.basename(dll)))
    return True


def prepare(dest, log=print):
    """Make sure models\\whistle.cact and engine\\*.dll exist next to dest.
    Downloads them once (needs internet) if they are not in Needle's cache yet."""
    if models_present(dest):
        return True
    if copy_from_cache(dest):
        log("Model and engine copied next to the exe.")
        return True
    log("First run: downloading model + engine (about 20 MB, needs internet)...")
    import numpy as np
    import needle
    tmp = os.path.join(tempfile.mkdtemp(), "silence.wav")
    write_wav(tmp, np.zeros(SR, dtype=np.float32))
    needle.transcribe(tmp)            # triggers the downloads into Needle's cache
    ok = copy_from_cache(dest)
    log("Model and engine saved next to the exe." if ok else "Could not find the downloaded files.")
    return ok


SR = 16000          # Whistle expects 16 kHz mono
CHUNK_S = 28        # stay under the 30 s limit
SEARCH_S = 3        # look for a quiet spot in the last 3 s of each chunk


# ---------- audio helpers ----------
def load_wav_16k_mono(path):
    import numpy as np
    with wave.open(path, "rb") as w:
        ch, sw, sr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    if sw == 2:
        a = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    elif sw == 1:
        a = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    elif sw == 4:
        a = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648.0
    else:
        raise ValueError("Unsupported WAV bit depth (use 8, 16 or 32-bit PCM).")
    if ch > 1:
        a = a[: len(a) // ch * ch].reshape(-1, ch).mean(axis=1)
    if sr != SR:
        import soxr
        a = soxr.resample(a, sr, SR)
    return a


def write_wav(path, a):
    import numpy as np
    pcm = (np.clip(a, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def split_audio(a):
    """Split into <=28 s pieces, cutting at the quietest ~100 ms near each boundary."""
    import numpy as np
    size = CHUNK_S * SR
    if len(a) <= size:
        return [a]
    pieces, start = [], 0
    win = SR // 10
    while len(a) - start > size:
        lo, hi = start + size - SEARCH_S * SR, start + size
        seg = np.abs(a[lo:hi])
        n = len(seg) // win
        energy = seg[: n * win].reshape(n, win).mean(axis=1)
        cut = lo + int(energy.argmin()) * win + win // 2
        pieces.append(a[start:cut])
        start = cut
    pieces.append(a[start:])
    return pieces


# ---------- GUI ----------
def resource_path(name):
    """Find a bundled file (works both from source and inside the one-file exe)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


BG, CARD, FG, MUTED = "#f3f5fa", "#ffffff", "#1f2937", "#6b7280"
ACCENT, ACCENT_H, DANGER, BORDER = "#2563eb", "#1d4ed8", "#dc2626", "#d6dbe6"
FONT = "Segoe UI"


class App:
    def __init__(self, root):
        self.root = root
        root.title("Wajeeha Transcribe")
        root.configure(bg=BG)
        root.geometry("600x560")
        root.minsize(560, 520)
        self.recording = False
        self.frames = []
        self.stream = None
        self.busy = False
        self.set_icon()
        self.build_styles()
        self.build_ui()

        if models_present(APP_DIR):
            self.log("Ready. Model found next to the exe.", clear=True)
        else:
            self.set_busy(True)
            self.log("First run: setting up the model next to the exe...", clear=True)
            threading.Thread(target=self.prep_worker, daemon=True).start()

    # ----- look & feel -----
    def set_icon(self):
        try:  # separate taskbar icon instead of the generic Python one
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("wajeeha.transcribe")
        except Exception:
            pass
        ico, png = resource_path("WT.ico"), resource_path("WT.png")
        try:
            if os.path.getsize(ico) > 0:
                self.root.iconbitmap(ico)
                return
        except Exception:
            pass
        try:
            if os.path.getsize(png) > 0:
                self._logo = tk.PhotoImage(file=png)
                self.root.iconphoto(True, self._logo)
        except Exception:
            pass

    def build_styles(self):
        st = ttk.Style(self.root)
        st.theme_use("clam")
        st.configure("TFrame", background=BG)
        st.configure("TLabel", background=BG, foreground=FG, font=(FONT, 10))
        st.configure("Section.TLabel", font=(FONT, 10, "bold"), foreground=FG)
        st.configure("Muted.TLabel", foreground=MUTED, font=(FONT, 9))
        st.configure("Field.TEntry", fieldbackground=CARD, foreground=FG, bordercolor=BORDER,
                     lightcolor=BORDER, darkcolor=BORDER, padding=8, font=(FONT, 10))
        st.map("Field.TEntry", bordercolor=[("focus", ACCENT)], lightcolor=[("focus", ACCENT)],
               darkcolor=[("focus", ACCENT)])
        base = dict(font=(FONT, 10, "bold"), padding=(16, 8), borderwidth=0, focusthickness=0, relief="flat")
        st.configure("Primary.TButton", background=ACCENT, foreground="white", **base)
        st.map("Primary.TButton", background=[("disabled", "#9ca3af"), ("active", ACCENT_H)],
               foreground=[("disabled", "#f3f4f6")])
        st.configure("Secondary.TButton", background="#e6ecff", foreground=ACCENT, **base)
        st.map("Secondary.TButton", background=[("active", "#d3deff")])
        st.configure("Rec.TButton", background="#fee2e2", foreground=DANGER, **base)
        st.map("Rec.TButton", background=[("active", "#fecaca")])
        st.configure("RecOn.TButton", background=DANGER, foreground="white", **base)
        st.map("RecOn.TButton", background=[("active", "#b91c1c")])
        st.configure("Bar.Horizontal.TProgressbar", troughcolor="#e5e9f2", background=ACCENT,
                     bordercolor="#e5e9f2", lightcolor=ACCENT, darkcolor=ACCENT, thickness=5)

    def build_ui(self):
        main = ttk.Frame(self.root, padding=(24, 20, 24, 14))
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(6, weight=1)

        # Audio file
        ttk.Label(main, text="Audio file", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        row = ttk.Frame(main)
        row.grid(row=1, column=0, sticky="ew", pady=(6, 18))
        row.columnconfigure(0, weight=1)
        self.audio_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.audio_var, style="Field.TEntry")\
            .grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(row, text="Browse", style="Secondary.TButton", command=self.browse_audio)\
            .grid(row=0, column=1, padx=(0, 8))
        self.rec_btn = ttk.Button(row, text="\u25cf  Record", style="Rec.TButton", command=self.toggle_record)
        self.rec_btn.grid(row=0, column=2)

        # Save path
        ttk.Label(main, text="Save transcript to", style="Section.TLabel").grid(row=2, column=0, sticky="w")
        row2 = ttk.Frame(main)
        row2.grid(row=3, column=0, sticky="ew", pady=(6, 18))
        row2.columnconfigure(0, weight=1)
        self.save_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.save_var, style="Field.TEntry")\
            .grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(row2, text="Browse", style="Secondary.TButton", command=self.browse_save)\
            .grid(row=0, column=1)

        # Run
        self.run_btn = ttk.Button(main, text="Run transcription", style="Primary.TButton", command=self.run)
        self.run_btn.grid(row=4, column=0, sticky="ew", ipady=4)

        # Status
        top = ttk.Frame(main)
        top.grid(row=5, column=0, sticky="ew", pady=(20, 6))
        top.columnconfigure(1, weight=1)
        ttk.Label(top, text="Status", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        self.bar = ttk.Progressbar(top, mode="indeterminate", style="Bar.Horizontal.TProgressbar", length=140)
        self.bar.grid(row=0, column=1, sticky="e")

        box = tk.Frame(main, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        box.grid(row=6, column=0, sticky="nsew")
        self.status = tk.Text(box, height=6, wrap="word", relief="flat", bg=CARD, fg=FG,
                              font=(FONT, 10), padx=12, pady=10, state="disabled", bd=0)
        sb = ttk.Scrollbar(box, command=self.status.yview)
        self.status.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.status.pack(side="left", fill="both", expand=True)

        ttk.Label(main, text="Note: If it fails, try a smaller audio file (under 30 seconds).\n"
                  "Longer files are split automatically, but short clips are most reliable.",
                  style="Muted.TLabel", justify="left").grid(row=7, column=0, sticky="w", pady=(12, 0))

    # status helpers (safe to call from worker threads)
    def log(self, msg, clear=False):
        def _do():
            self.status.config(state="normal")
            if clear:
                self.status.delete("1.0", "end")
            self.status.insert("end", msg + "\n")
            self.status.see("end")
            self.status.config(state="disabled")
        self.root.after(0, _do)

    def set_busy(self, b):
        self.busy = b

        def _do():
            self.run_btn.config(state="disabled" if b else "normal")
            if b:
                self.bar.start(12)
            else:
                self.bar.stop()
        self.root.after(0, _do)

    # file pickers
    def browse_audio(self):
        p = filedialog.askopenfilename(title="Select audio", filetypes=[("WAV audio", "*.wav"), ("All files", "*.*")])
        if p:
            self.audio_var.set(p)
            if not self.save_var.get():
                self.save_var.set(os.path.splitext(p)[0] + ".txt")

    def browse_save(self):
        p = filedialog.asksaveasfilename(title="Save transcript", defaultextension=".txt",
                                         filetypes=[("Text file", "*.txt")])
        if p:
            self.save_var.set(p)

    # recording
    def toggle_record(self):
        if not self.recording:
            try:
                import sounddevice as sd
                self.frames = []
                self.stream = sd.InputStream(samplerate=SR, channels=1, dtype="float32",
                                             callback=lambda d, n, t, s: self.frames.append(d.copy()))
                self.stream.start()
            except Exception as e:
                messagebox.showerror("Microphone error", str(e))
                return
            self.recording = True
            self.rec_btn.config(text="\u25a0  Stop", style="RecOn.TButton")
            self.log("Recording... press Stop when done.", clear=True)
        else:
            self.stream.stop()
            self.stream.close()
            self.recording = False
            self.rec_btn.config(text="\u25cf  Record", style="Rec.TButton")
            if not self.frames:
                self.log("Nothing recorded.")
                return
            import numpy as np
            a = np.concatenate(self.frames).reshape(-1)
            d = os.path.join(os.path.expanduser("~"), "Documents", "WajeehaTranscribe")
            os.makedirs(d, exist_ok=True)
            p = os.path.join(d, time.strftime("recording_%Y%m%d_%H%M%S.wav"))
            write_wav(p, a)
            self.audio_var.set(p)
            if not self.save_var.get():
                self.save_var.set(p[:-4] + ".txt")
            self.log(f"Recorded {len(a)/SR:.1f} s. Saved to {p}\nPress Run to transcribe.")

    # setup + transcription
    def prep_worker(self):
        try:
            ok = prepare(APP_DIR, self.log)
            self.log("Ready." if ok else "Setup incomplete. Check your internet and restart the app.")
        except Exception as e:
            self.log(f"Setup failed: {e}")
        finally:
            self.set_busy(False)

    def run(self):
        if self.busy:
            return
        if self.recording:
            messagebox.showinfo("Recording", "Press Stop first.")
            return
        audio, out = self.audio_var.get().strip(), self.save_var.get().strip()
        if not audio or not os.path.isfile(audio):
            messagebox.showwarning("Audio file", "Choose or record an audio file first.")
            return
        if not out:
            messagebox.showwarning("Save path", "Choose where to save the transcript.")
            return
        self.set_busy(True)
        self.log("Starting...", clear=True)
        threading.Thread(target=self.worker, args=(audio, out), daemon=True).start()

    def worker(self, audio, out):
        try:
            self.log("Loading audio...")
            a = load_wav_16k_mono(audio)
            pieces = split_audio(a)
            self.log(f"Audio length {len(a)/SR:.1f} s, {len(pieces)} part(s).")
            self.log(setup_offline())
            self.log("Loading Whistle model...")
            import needle
            texts = []
            tmpdir = tempfile.mkdtemp()
            for i, piece in enumerate(pieces, 1):
                self.log(f"Transcribing part {i}/{len(pieces)}...")
                tmp = os.path.join(tmpdir, f"part{i}.wav")
                write_wav(tmp, piece)
                texts.append(needle.transcribe(tmp)["text"].strip())
                os.remove(tmp)
            text = " ".join(t for t in texts if t)
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(text + "\n")
            preview = text if len(text) < 300 else text[:300] + "..."
            self.log(f"Done. Saved to {out}\n\n{preview if text else '(No speech detected)'}")
        except Exception as e:
            self.log(f"FAILED: {e}\nTry a smaller / 16-bit WAV file.")
        finally:
            self.set_busy(False)


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    if len(sys.argv) >= 3 and sys.argv[1] == "--prepare":      # used by build.bat
        sys.exit(0 if prepare(sys.argv[2]) else 1)
    root = tk.Tk()
    App(root)
    root.mainloop()
