# vission_ai_image.py

import os
import sys
import time
import threading
import asyncio 
import google.generativeai as genai
from PIL import Image
import easyocr
import speech_recognition as sr
import re 
import keyboard 
import edge_tts
import sounddevice as sd
import soundfile as sf
import numpy as np


# --- 1. CONFIGURATION ---
GEMINI_API_KEY = "YOUR_API_KEY" 
IMAGE_TO_READ = 'test2.jpg'
OUTPUT_TEXT_FILE = 'final_summary.txt'

# --- OCR FUNCTION ---
def extract_text_from_image(ocr_engine, image_path):
    print(f"[1/6] Running OCR on {image_path}...")
    if not os.path.exists(image_path):
        print(f"Error: Image file not found.", file=sys.stderr)
        return None
    try:
        result = ocr_engine.readtext(image_path)
        full_text = " ".join([text for (_, text, _) in result])
        return full_text.strip()
    except Exception as e:
        print(f"Error during OCR: {e}", file=sys.stderr)
        return None

# --- TEXT CLEANER ---
def clean_text_for_tts(text):
    clean = re.sub(r'[*#_]', '', text)
    return clean.strip()

# --- EDGE-TTS GENERATOR (Async Wrapper) ---
async def generate_audio_edge(text, output_file):
    voice = 'en-US-AriaNeural' 
    # Increased speed is fine with SoundFile, it won't distort pitch
    communicate = edge_tts.Communicate(text, voice, rate="+0%")
    await communicate.save(output_file)

# --- SPEECH OUTPUT WORKER ---
def speak_worker(text):
    temp_filename = ""
    try:
        safe_text = clean_text_for_tts(text)
        if not safe_text: return

        # 1. Unique filename
        temp_filename = f"tts_{int(time.time())}.mp3"

        # 2. Generate Audio File
        asyncio.run(generate_audio_edge(safe_text, temp_filename))

        # 3. Read and Play Audio (The Distortion Fix)
        # data = the audio wave, fs = sample rate (e.g., 24000)
        data, fs = sf.read(temp_filename)
        
        # Stop any existing audio
        sd.stop()
        
        # Play asynchronously
        sd.play(data, fs)
        
        # Block this thread until audio finishes (or is stopped externally)
        sd.wait()

        # 4. Cleanup
        # Give the OS a tiny moment to release the file handle
        time.sleep(0.1) 
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    except Exception as e:
        if "Stream is stopped" not in str(e):
             print(f"\n[TTS Error]: {e}")
        
        if temp_filename and os.path.exists(temp_filename):
            try: os.remove(temp_filename)
            except: pass

def speak_text_interruptible(text):
    # Stop whatever is currently playing immediately
    sd.stop()

    print(f" 🗣️ AI: {text}")
    
    t = threading.Thread(target=speak_worker, args=(text,), daemon=True)
    t.start()

def stop_talking():
    # Immediate silence
    sd.stop()

# --- PUSH-TO-TALK LISTENER ---
def listen_while_key_pressed(recognizer, mic):
    print("\n   [Hold 'v' to speak / Press 'q' to quit]")

    while True:
        # --- QUIT ---
        if keyboard.is_pressed('q'):
            print("\n   [👋 Quit key detected...]")
            stop_talking()
            return "exit" 

        # --- TALK ---
        if keyboard.is_pressed('v'):
            stop_talking() 
            print("   [🔴 Recording... Release 'v' to stop]")
            
            try:
                with mic as source:
                    frames = []
                    while keyboard.is_pressed('v'):
                        try:
                            data = source.stream.read(source.CHUNK)
                            frames.append(data)
                        except Exception:
                            break
            except OSError as e:
                print(f"   [Microphone Error: {e}]")
                time.sleep(1)
                return None

            print("   [✋ Processing...]")
            
            if len(frames) > 0:
                raw_data = b''.join(frames)
                audio_data = sr.AudioData(raw_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
                try:
                    text = recognizer.recognize_google(audio_data)
                    print(f" 👤 You said: '{text}'")
                    return text.lower()
                except sr.UnknownValueError:
                    print("   (Didn't catch that, try again)")
                    print("\n   [Hold 'v' to speak / Press 'q' to quit]")
                except sr.RequestError:
                    print("   [API Error]")
                    return None
            
        time.sleep(0.05) 

# --- MAIN WORKFLOW ---
def start_interactive_chat(gemini_model, image_path, ocr_text):
    print("[2/6] Loading image...")
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error: {e}")
        return

    print("[3/6] Calibrating Microphone (Please stay silent for 1 second)...")
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
        print("      Done.")
    except Exception as e:
        print(f"      Warning: Mic calibration failed ({e}). Proceeding anyway.")

    initial_prompt = f"""
    You are a helpful assistant for a visually impaired person.
    Here is an image I am looking at.
    My local OCR tool also found this text: '{ocr_text}'
    
    First, give a summary (max 30 words).
    Then, wait for questions.
    """

    chat_session = gemini_model.start_chat(
        history=[{"role": "user", "parts": [img, initial_prompt]}]
    )

    try:
        response = chat_session.send_message("Initial summary.")
        summary = response.text.strip()
        with open(OUTPUT_TEXT_FILE, 'w', encoding='utf-8') as f: f.write(summary)
        speak_text_interruptible(summary)
    except Exception as e:
        print(f"Gemini Error: {e}")
        return

    print("\n" + "="*40)
    print("💬 PUSH-TO-TALK MODE STARTED")
    print("👉 HOLD 'v' to ask a question.")
    print("👉 PRESS 'q' to quit cleanly.")
    print("="*40)

    while True:
        user_text = listen_while_key_pressed(recognizer, mic)

        if user_text:
            if "exit" in user_text or "quit" in user_text:
                stop_talking()
                print("👋 Session ended by user.")
                os._exit(0) 
            
            try:
                response = chat_session.send_message(user_text)
                answer = response.text.strip()
                speak_text_interruptible(answer)
            except Exception as e:
                print(f"Gemini Error: {e}")

def main():
    if GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        print("Set API Key.")
        return

    try:
        print(" -> Loading EasyOCR...")
        # Note: os._exit(0) handles the shutdown crash, so gpu=True is fine.
        ocr_engine = easyocr.Reader(['en'], gpu=True) 
        
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.5-flash-lite') 
        
        ocr_text = extract_text_from_image(ocr_engine, IMAGE_TO_READ)
        if ocr_text:
            start_interactive_chat(gemini_model, IMAGE_TO_READ, ocr_text)

    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    main()