# Install dependencies

  brew install ffmpeg
  
  python3 -m pip install --upgrade pip
  
  brew install portaudio
  
  pip3 install pyaudio openai-whisper numpy torch
  

# Save below script as live_transcribe.py

  import pyaudio
  
  import numpy as np
  
  import whisper
  
  import torch
  
  import queue
  
  
  MODEL_TYPE = "base"  # Use "tiny" for speed, "medium" for accuracy
  
  SAMPLE_RATE = 16000
  
  CHUNK_DURATION = 5   # Processes audio every 5 seconds
  
  CHUNK_SIZE = SAMPLE_RATE * CHUNK_DURATION
  
  
  print(f"Loading Whisper model '{MODEL_TYPE}'...")
  
  model = whisper.load_model(MODEL_TYPE)
  
  audio_queue = queue.Queue()
  
  def audio_callback(in_data, frame_count, time_info, status):
      
      # Convert buffer to float32 array for Whisper
      
      audio_queue.put(np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0)
      
      return (None, pyaudio.paContinue)
      
  

  p = pyaudio.PyAudio()
  
  stream = p.open(format=pyaudio.paInt16,
                  channels=1,
                  rate=SAMPLE_RATE,           
                  input=True,        
                  frames_per_buffer=CHUNK_SIZE,
                  stream_callback=audio_callback)
                  
  
  print("\n--- Live Transcription Started ---")
  
  print("Listening... (Press Ctrl+C to stop)\n")
  
  
  try:
  
      stream.start_stream()
      
      while stream.is_active():
      
          if not audio_queue.empty():
          
              audio_data = audio_queue.get()
              
              
              # Transcribe the current chunk
              
              result = model.transcribe(audio_data, fp16=torch.cuda.is_available())
              
              text = result['text'].strip()
              
              
              if text:
              
                  print(f">> {text}")
                  
  
  except KeyboardInterrupt:
  
      print("\nStopping...")
      
  finally:
  
      stream.stop_stream()
      
      stream.close()
      
      p.terminate()
      


# Run the script

python3 live_transcribe.py
