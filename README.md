
# 🎙️ Live Real-Time Captioning on macOS

This project captures and transcribes audio playing on your Mac in real time using [BlackHole](https://existential.audio/blackhole/), [FFmpeg](https://ffmpeg.org/), and [OpenAI Whisper](https://github.com/openai/whisper).

## ✅ Features
- Captures internal audio with BlackHole
- Records short chunks using FFmpeg
- Transcribes with Whisper (offline)
- Saves captions per app-session in `captions/`
- Logs everything to a rotating `caption.log`
- Auto-deletes temporary audio chunks
- Tracks active app (Zoom, Safari, YouTube etc.)

## 📦 Folder Structure
```
live_caption/
├── captions/          # Caption output files
├── audio_chunks/      # Auto-deleted WAV chunks
├── config.json        # User config for model, paths, duration
├── live_caption.py    # Main real-time script
├── caption.log        # Rotating log (auto-created)
```

## ⚙️ Setup Instructions

### 1. Install BlackHole
Download and install [BlackHole 2ch](https://existential.audio/blackhole/), then create a Multi-Output Device with BlackHole + your output device.

### 2. Install Python dependencies
```bash
brew install ffmpeg
pip install git+https://github.com/openai/whisper
pip install AppKit psutil
```

### 3. Configure and Run
```bash
python live_caption.py
```

Configure via `config.json` to change:
- recording duration
- model size
- language
- output paths

## ✅ Output
Each app gets a file like `Zoom_20250701_120000.txt`, updated with new speech every 30s by default.

---

## 🛠 Next Steps
- Add GUI / menu bar widget
- Create `.app` launcher
- Show live captions in a floating window

Contributions welcome!
