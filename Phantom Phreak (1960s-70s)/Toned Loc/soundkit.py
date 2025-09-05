# soundkit.py (patched)
# - fixes tuple→bytearray bug
# - adds proper WAV header for winsound in-memory playback
# - keeps simpleaudio path for non-Windows
import sys, math, threading, time, struct

_BACKEND = None
try:
    import simpleaudio  # pip install simpleaudio
    _BACKEND = "simpleaudio"
except Exception:
    if sys.platform.startswith("win"):
        try:
            import winsound
            _BACKEND = "winsound"
        except Exception:
            _BACKEND = None
    else:
        _BACKEND = None

_SR = 44100  # sample rate

def _sine(freq, ms, volume=0.4):
    n = int(_SR * (ms / 1000.0))
    twopi = 2.0 * math.pi
    buf = bytearray()
    for i in range(n):
        s = math.sin(twopi * freq * (i / _SR))
        v = int(max(-1.0, min(1.0, s)) * volume * 32767)
        buf.extend(struct.pack('<h', v))  # << fixed: write 16-bit LE
    return bytes(buf)

def _mix(stuffs):
    # stuffs = [(freq_or_bytes, ms, vol), ...]
    max_ms = max(ms for _, ms, _ in stuffs)
    total_len = int(_SR * (max_ms / 1000.0))
    acc = [0] * total_len
    for freq, ms, vol in stuffs:
        data = _sine(freq, ms, vol) if isinstance(freq, (int, float)) else freq
        n = min(total_len, len(data) // 2)
        for i in range(n):
            s = struct.unpack_from('<h', data, 2*i)[0]
            acc[i] += s
    # clamp & pack
    out = bytearray()
    for v in acc:
        v = max(-32768, min(32767, v))
        out.extend(struct.pack('<h', v))
    return bytes(out)

def _wav_from_pcm(pcm_bytes, sample_rate=_SR):
    # Build a minimal RIFF/WAVE header around 16-bit mono PCM
    num_channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    subchunk2_size = len(pcm_bytes)
    chunk_size = 36 + subchunk2_size
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF', chunk_size, b'WAVE',
        b'fmt ', 16, 1, num_channels, sample_rate,
        byte_rate, block_align, bits_per_sample,
        b'data', subchunk2_size
    )
    return header + pcm_bytes

def _play_pcm(pcm_bytes):
    if _BACKEND is None:
        return
    if _BACKEND == "simpleaudio":
        # non-blocking; returns a PlayObject
        try:
            simpleaudio.play_buffer(pcm_bytes, 1, 2, _SR)
        except Exception:
            pass
    else:
        # winsound: many systems cannot do SND_ASYNC with SND_MEMORY
        # We’re already on a background thread, so sync is fine.
        try:
            winsound.PlaySound(_wav_from_pcm(pcm_bytes), winsound.SND_MEMORY)
        except RuntimeError as e:
            # Fallback: try fileless stop, then retry sync
            try:
                winsound.PlaySound(None, 0)
                winsound.PlaySound(_wav_from_pcm(pcm_bytes), winsound.SND_MEMORY)
            except Exception:
                pass

def _async(fn, *a, **kw):
    threading.Thread(target=fn, args=a, kwargs=kw, daemon=True).start()

# ========= Public patterns =========

def play_ring(ms_on=2000, ms_off=4000, cycles=1):
    """NA ringback 440+480 Hz, ~2s on / ~4s off"""
    def _run():
        tone = _mix([(440, ms_on, 0.35), (480, ms_on, 0.35)])
        for _ in range(cycles):
            _play_pcm(tone)
            time.sleep((ms_on + ms_off)/1000.0)
    _async(_run)

def play_busy(cycles=4):
    """Busy: 480+620 Hz, 0.5s on / 0.5s off"""
    def _run():
        on = _mix([(480, 500, 0.35), (620, 500, 0.35)])
        for _ in range(cycles):
            _play_pcm(on)
            time.sleep(1.0)  # ~0.5 on + ~0.5 off
    _async(_run)

def play_reorder(cycles=6):
    """Fast busy: 0.25s on / 0.25s off"""
    def _run():
        on = _mix([(480, 250, 0.35), (620, 250, 0.35)])
        for _ in range(cycles):
            _play_pcm(on)
            time.sleep(0.5)
    _async(_run)

def play_carrier(speed="2400", ms=1200):
    freq = {"1200": 1200, "2400": 1200, "9600": 1800}.get(str(speed), 1500)
    _async(lambda: _play_pcm(_sine(freq, ms, 0.35)))

def play_connect(speed="2400"):
    def _run():
        f0, f1 = (900, 1400) if str(speed) == "1200" else (1000, 1800)
        steps = 5
        segs = [(f0 + (f1-f0)*i/(steps-1), 120, 0.35) for i in range(steps)]
        _play_pcm(_mix(segs))
    _async(_run)

def play_no_carrier():
    def _run():
        f0, f1 = 1800, 600
        steps = 6
        segs = [(f0 + (f1-f0)*i/(steps-1), 100, 0.35) for i in range(steps)]
        _play_pcm(_mix(segs))
    _async(_run)

def play_fax(ms=1200):
    def _run():
        segs = []
        for i in range(8):
            segs.append((1100 if i%2==0 else 2100, 150, 0.35))
        _play_pcm(_mix(segs))
    _async(_run)

def play_voice():
    def _run():
        _play_pcm(_sine(1000, 40, 0.4))
        time.sleep(0.06)
        _play_pcm(_sine(300, 200, 0.25))
    _async(_run)
