import subprocess
import os
import time
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import whisper

# === Load config ===
with open("config.json") as f:
    config = json.load(f)

RECORD_DURATION = config["record_duration"]
AUDIO_DEVICE = config["audio_device"]
WHISPER_MODEL = config["whisper_model"]
LANGUAGE = config.get("language", "en")
CAPTIONS_DIR = config["output_dirs"]["captions"]
AUDIO_DIR = config["output_dirs"]["audio_chunks"]
LOG_FILE = config["log_file"]
LOG_MAX_BYTES = config["log_max_bytes"]
LOG_BACKUP_COUNT = config["log_backup_count"]

os.makedirs(CAPTIONS_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# === Logger setup ===
logger = logging.getLogger("LiveCaptionLogger")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT)
formatter = logging.Formatter("[%(asctime)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# === Load Whisper ===
logger.info("Loading Whisper model: %s", WHISPER_MODEL)
model = whisper.load_model(WHISPER_MODEL)

# === App tracking ===
last_app = None
caption_path = None
session_start_time = None

def get_active_app_name():
    try:
        import AppKit
        app = AppKit.NSWorkspace.sharedWorkspace().frontmostApplication()
        return app.localizedName()
    except:
        return "UnknownApp"

def safe_filename(name):
    return name.replace(" ", "_").replace("/", "_")

def record_audio(file_path):
    subprocess.run([
        "ffmpeg", "-y", "-f", "avfoundation", "-i", f":{AUDIO_DEVICE}",
        "-t", str(RECORD_DURATION), file_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def transcribe(audio_file):
    return model.transcribe(audio_file, language=LANGUAGE)["text"].strip()

def get_caption_file(app_name, session_start):
    filename = f"{safe_filename(app_name)}_{session_start}.txt"
    return os.path.join(CAPTIONS_DIR, filename)

def main_loop():
    global last_app, caption_path, session_start_time

    logger.info("Live Captioning Started")
    try:
        while True:
            active_app = get_active_app_name()

            if active_app != last_app:
                session_start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                caption_path = get_caption_file(active_app, session_start_time)
                with open(caption_path, "a") as f:
                    f.write(f"\n\n🪟 Switched to App: {active_app} @ {datetime.now().strftime('%H:%M:%S')}\n")
                logger.info("Switched app → %s", active_app)
                last_app = active_app

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = os.path.join(AUDIO_DIR, f"{safe_filename(active_app)}_{timestamp}.wav")

            record_audio(audio_file)

            if os.path.exists(audio_file) and os.path.getsize(audio_file) > 1000:
                try:
                    text = transcribe(audio_file)
                    if text:
                        with open(caption_path, "a") as f:
                            f.write(f"\n[{datetime.now().strftime('%H:%M:%S')}]\n{text}\n")
                        logger.info("Appended caption to %s", caption_path)
                    else:
                        logger.warning("No speech detected in %s", audio_file)
                except Exception as e:
                    logger.error("Transcription error: %s", str(e))
            else:
                logger.warning("Audio file %s was empty or missing", audio_file)

            if os.path.exists(audio_file):
                os.remove(audio_file)
                logger.info("Deleted audio file: %s", audio_file)

    except KeyboardInterrupt:
        logger.info("Stopped by user")

if __name__ == "__main__":
    main_loop()
