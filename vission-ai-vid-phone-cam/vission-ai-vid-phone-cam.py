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
import cv2  
import edge_tts
import sounddevice as sd
import soundfile as sf
import numpy as np

# --- 1. CONFIGURATION ---
# Replace with your actual key
GEMINI_API_KEY = "YOUR_API_KEY" 
TEMP_IMAGE_PATH = 'captured_temp.jpg' 
OUTPUT_TEXT_FILE = 'final_summary.txt'

# URL from the "IP Webcam" app on your S23. 
# On a Hotspot, it is usually 192.168.43.1:8080.
# If connected to home Wi-Fi, it might be 192.168.1.X:8080.
# ALWAYS keep '/video' at the end.
PHONE_URL = "http://192.168.1.5:8080/video"

# --- OCR FUNCTION ---
def extract_text_from_image(ocr_engine, image_path):
    print(f"[Info] Running OCR on {image_path}...")
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

# --- EDGE-TTS GENERATOR ---
async def generate_audio_edge(text, output_file):
    voice = 'en-US-AriaNeural' 
    communicate = edge_tts.Communicate(text, voice, rate="+0%")
    await communicate.save(output_file)

# --- SPEECH OUTPUT WORKER ---
def speak_worker(text):
    temp_filename = ""
    try:
        safe_text = clean_text_for_tts(text)
        if not safe_text: return

        temp_filename = f"tts_{int(time.time())}.mp3"
        asyncio.run(generate_audio_edge(safe_text, temp_filename))

        data, fs = sf.read(temp_filename)
        sd.stop()
        sd.play(data, fs)
        sd.wait()

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
    sd.stop()
    print(f" 🗣️ AI: {text}")
    t = threading.Thread(target=speak_worker, args=(text,), daemon=True)
    t.start()

def stop_talking():
    sd.stop()

# --- WEBCAM CAPTURE MODULE (S23 EDITION) ---
def capture_image_from_webcam():
    print(f"\n[Connecting to S23 at {PHONE_URL} ...]")
    
    # Connect to the IP stream
    cap = cv2.VideoCapture(PHONE_URL) 
    
    # Set buffer size to 1 to reduce lag/latency
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if not cap.isOpened():
        print("Error: Could not connect to the phone camera.")
        print(f"Make sure the IP Webcam app is running and the URL is correct: {PHONE_URL}")
        return None

    print("\n" + "="*40)
    print("📷 S23 CAMERA MODE")
    print("👉 Press 'c' to CAPTURE")
    print("👉 Press 'q' to QUIT app")
    print("="*40)

    captured_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame. (Stream ended or connection lost?)")
            break

        # Resize frame: Phone cameras are high res (4K/1080p)
        # We resize it to 960x540 to fit comfortably on the laptop screen
        frame = cv2.resize(frame, (540, 960))

        # Show the live feed
        cv2.imshow('S23 Feed - "c" to capture', frame)

        key = cv2.waitKey(1) & 0xFF

        # --- CAPTURE ---
        if key == ord('c'):
            captured_frame = frame
            print("\n[Image Captured] Reviewing...")
            
            # Show the frozen captured image
            while True:
                cv2.imshow('S23 Feed - "c" to capture', captured_frame)
                
                # Create a small instruction overlay on console
                print("   >> Press 'y' to PROCESS, 'n' to RETAKE")
                
                k2 = cv2.waitKey(0) # Wait indefinitely for a key
                
                if k2 == ord('y'):
                    # Save image
                    cv2.imwrite(TEMP_IMAGE_PATH, captured_frame)
                    cap.release()
                    cv2.destroyAllWindows()
                    return TEMP_IMAGE_PATH
                
                elif k2 == ord('n'):
                    print("   >> Retaking...")
                    break # Break inner loop, go back to live feed
        
        # --- QUIT ---
        elif key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return "exit"

    cap.release()
    cv2.destroyAllWindows()
    return None

# --- PUSH-TO-TALK LISTENER ---
def listen_while_key_pressed(recognizer, mic):
    print("\n   [Hold 'v' to speak / Press 'b' for Camera / 'q' to quit]")

    while True:
        # --- BACK TO CAMERA ---
        if keyboard.is_pressed('b'):
             print("\n   [🔙 Going back to Camera...]")
             stop_talking()
             return "back"

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
                    print("\n   [Hold 'v' to speak / Press 'b' for Camera]")
                except sr.RequestError:
                    print("   [API Error]")
                    return None
            
        time.sleep(0.05) 

# --- CHAT SESSION ---
def start_interactive_chat(gemini_model, image_path, ocr_text, recognizer, mic):
    print("[Info] Analyzing image content...")
    
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error: {e}")
        return "back" # Go back to camera if image fails

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
        speak_text_interruptible(summary)
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "back"

    print("\n" + "="*40)
    print("💬 CHAT MODE")
    print("👉 HOLD 'v' to ask a question.")
    print("👉 PRESS 'b' to go back to Camera.")
    print("="*40)

    while True:
        user_text = listen_while_key_pressed(recognizer, mic)

        if user_text == "back":
            return "back"
        
        if user_text == "exit":
            return "exit"

        if user_text:
            if "exit" in user_text or "quit" in user_text:
                stop_talking()
                return "exit"
            
            try:
                response = chat_session.send_message(user_text)
                answer = response.text.strip()
                speak_text_interruptible(answer)
            except Exception as e:
                print(f"Gemini Error: {e}")

# --- MAIN LOOP ---
def main():
    if GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        print("Set API Key.")
        return

    try:
        # 1. SETUP - Do this once
        print(" -> Loading EasyOCR (One time setup)...")
        ocr_engine = easyocr.Reader(['en'], gpu=True) 
        
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.5-flash-lite') 

        print(" -> Calibrating Microphone...")
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
        
        # 2. MAIN APP LOOP
        while True:
            # --- STEP A: CAMERA ---
            image_path = capture_image_from_webcam()
            
            if image_path == "exit" or image_path is None:
                print("Goodbye.")
                break

            # --- STEP B: PROCESSING ---
            ocr_text = extract_text_from_image(ocr_engine, image_path)
            
            # --- STEP C: CHAT INTERACTION ---
            # We pass the mic/recognizer so we don't have to recalibrate every time
            result = start_interactive_chat(gemini_model, image_path, ocr_text, recognizer, mic)
            
            if result == "exit":
                print("Goodbye.")
                break
            elif result == "back":
                continue # Loops back to Step A (Camera)

    except Exception as e:
        print(f"Critical Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()