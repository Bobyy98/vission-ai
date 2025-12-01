# Gemini Live Vision Assistant (Webcam Edition)

A real-time, multimodal AI assistant designed to help visually impaired users interact with the world through a webcam. This tool captures live images, extracts text via **OCR**, analyzes the visual context using **Google Gemini Vision**, and enables a two-way spoken conversation about what the camera sees.

## Features

* **Live Webcam Integration:** Uses `OpenCV` to provide a real-time camera feed.
* **Workflow Navigation:** Seamlessly switch between **Camera Mode** (taking pictures) and **Chat Mode** (talking to the AI).
* **Review System:** "Freeze" the camera frame to review image clarity before sending it to the AI.
* **Continuous Loop:** After finishing a conversation about one object, press a single key (`b`) to return to the camera and scan something new.
* **Hybrid Analysis:** Combines `EasyOCR` (for reading specific text) and `Gemini 2.5` (for general visual understanding).
* **Neural Voice Output:** Uses `Edge-TTS` for high-quality, interruptible speech.

## Prerequisites

* **Python 3.8+**
* **Google Gemini API Key** (Get one from [Google AI Studio](https://aistudio.google.com/))
* **Hardware:**
    * **Webcam** (Built-in laptop camera or external USB).
    * Microphone and Speakers.
* **(Optional) NVIDIA GPU:** The script is configured to use a GPU for OCR acceleration if available.

## 📦 Installation

1.  **Clone or Download** this repository.
2.  **Install the required Python libraries:**
    (Note: `opencv-python` is required for the webcam features)

    ```bash
    pip install google-generativeai easyocr speechrecognition keyboard edge-tts sounddevice soundfile numpy pillow opencv-python
    ```

    *Note: On Linux systems, you may also need to install PortAudio (`sudo apt-get install libportaudio2`).*

3.  **Set up your API Key:**
    Open `vission_ai_video.py` (or your script name) and find the configuration section:
    ```python
    GEMINI_API_KEY = "YOUR_API_KEY_HERE"
    ```
    Replace the placeholder with your actual Gemini API key.

## 🚀 Usage

1.  **Run the script:**
    ```bash
    python vission_ai_video.py
    ```
    *(Note: On Linux/macOS, run with `sudo` if key presses aren't detected).*

2.  **Initialization:**
    * The script will load OCR and Calibrate the Microphone. **Stay silent for 1 second** during calibration.
    * A window titled **"Webcam - 'c' to capture"** will open.

3.  **Phase 1: Camera Mode 📷**
    * **`c`**: Press to **CAPTURE** (Freeze the frame).
    * **`y`**: Press to **CONFIRM** the captured image and send to AI.
    * **`n`**: Press to **RETAKE** (Unfreeze and return to live feed).
    * **`q`**: Quit the application.

4.  **Phase 2: Chat Mode 🗣️**
    * The AI will speak a summary of the image.
    * **Hold `v`**: Speak your question to the AI. Release to listen.
    * **Tap `v`**: Interrupt the AI if it is speaking.
    * **Press `b`**: **GO BACK** to Camera Mode to scan a new object.
    * **Press `q`**: Quit.

## ⚙️ Configuration

You can adjust these variables at the top of the script:

| Variable | Description |
| :--- | :--- |
| `GEMINI_API_KEY` | Your authentication key for Google Gemini. |
| `TEMP_IMAGE_PATH` | The filename for the temporary webcam snapshot (default: `captured_temp.jpg`). |
| `OUTPUT_TEXT_FILE` | The file where the initial summary transcript is saved. |

## 🔧 Troubleshooting

* **Webcam fails to open:**
    * Check if another app (Zoom, Teams) is using the camera.
    * If you have multiple cameras, change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` in the code.
* **"Stream is stopped" Error:**
    * This is normal behavior in the logs. It means you successfully interrupted the AI's speech using the keyboard.
* **Key presses not working:**
    * Click on the **Webcam Window** when in Camera Mode.
    * Ensure the terminal/console has focus when in Chat Mode.

## 📜 License

This project is open-source. Feel free to modify and improve it!