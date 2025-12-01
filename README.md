# Gemini Vision Voice Assistant 👁️🤖🎤

**A multimodal AI assistant designed to help visually impaired users "see" and interact with the world.**

This project combines **Optical Character Recognition (OCR)**, **Generative AI (Gemini 2.5)**, and **Neural Text-to-Speech** to provide real-time, conversational insights about visual content. It operates in two distinct modes: analyzing **Static Images** or interacting via a **Live Webcam Feed**.

## ✨ Key Features

* **Hybrid Analysis:** Combines `EasyOCR` to read hard text (menus, signs) and `Google Gemini` to understand complex visual context and objects.
* **Dual Modes:**
    * 🖼️ **Static Mode:** Analyze existing image files for detailed breakdown.
    * 📹 **Live Mode:** Real-time webcam integration to capture, review, and chat about physical objects.
* **Natural Voice Output:** Integrated `Edge-TTS` (Microsoft Edge's Neural Voice) for high-quality, human-sounding speech.
* **Smart Interruptions:** Features an interruptible audio system—users can cut the AI off mid-sentence to ask new questions instantly.
* **Push-to-Talk:** Simple "Hold 'V' to speak" control scheme ensures the AI only listens when you want it to.
* **Contextual Memory:** The AI remembers previous questions within a session, allowing for a natural back-and-forth conversation.

---

## 🛠️ Prerequisites

* **Python 3.8+**
* **Google Gemini API Key** (Get one from [Google AI Studio](https://aistudio.google.com/))
* **Hardware:** Microphone, Speakers, and Webcam (for Live Mode).
* **System Dependencies:**
    * *Linux Users only:* You may need PortAudio (`sudo apt-get install libportaudio2`).
* **NVIDIA GPU (Optional):** The scripts are configured to use CUDA for faster OCR if available.

---

## 📦 Installation

1.  **Clone or Download** this repository.

2.  **Install Python Dependencies:**
    Run the following command to install all necessary libraries for both image and video modes:

    ```bash
    pip install google-generativeai easyocr speechrecognition keyboard edge-tts sounddevice soundfile numpy pillow opencv-python
    ```

3.  **Configuration:**
    Open `vission_ai_image.py` (for static) and `vission_ai_video.py` (for webcam) in your code editor. Locate the configuration section at the top:

    ```python
    GEMINI_API_KEY = "YOUR_API_KEY_HERE"
    ```
    Replace the placeholder with your actual Gemini API key.

---

## 🚀 Usage

### Mode 1: Static Image Analyst 🖼️
*Best for analyzing specific files like document scans, saved photos, or screenshots.*

1.  Place your image in the project folder and name it `test.jpg` (or update `IMAGE_TO_READ` in the script).
2.  Run the script:
    ```bash
    python vission_ai_image.py
    ```
3.  **The Workflow:**
    * The AI will speak a summary.
    * **Hold `v`**: Speak your question.
    * **Release `v`**: Listen to the answer.
    * **Press `q`**: Quit.

### Mode 2: Live Webcam Assistant 📹
*Best for real-time interaction, exploring a room, or reading physical objects.*

1.  Run the script:
    ```bash
    python vission_ai_video.py
    ```
2.  **The Workflow:**
    * **Phase 1 (Camera):** A window opens. Press **`c`** to capture a frame. Press **`y`** to confirm or **`n`** to retake.
    * **Phase 2 (Chat):** The AI summarizes the image. **Hold `v`** to ask questions.
    * **Loop:** Press **`b`** to go **Back** to camera mode and scan a new object.

---

## 🎮 Controls Cheat Sheet

| Key | Function | Mode Availability |
| :--- | :--- | :--- |
| **`v` (Hold)** | **Voice Input:** Hold to speak into the microphone. | Both |
| **`v` (Tap)** | **Interrupt:** Stop the AI from speaking immediately. | Both |
| **`q`** | **Quit:** Exit the application. | Both |
| **`c`** | **Capture:** Freeze the webcam frame. | Live Mode Only |
| **`y`** | **Yes/Confirm:** Send frozen image to AI. | Live Mode Only |
| **`n`** | **No/Retake:** Unfreeze frame and try again. | Live Mode Only |
| **`b`** | **Back:** Return to camera mode from chat mode. | Live Mode Only |

---

## ⚙️ Advanced Configuration

You can adjust these variables at the top of the Python scripts:

| Variable | Description |
| :--- | :--- |
| `GEMINI_API_KEY` | Your authentication key for Google Gemini. |
| `IMAGE_TO_READ` | **(Static Mode)** Filename of the image to analyze. |
| `TEMP_IMAGE_PATH` | **(Live Mode)** Filename for temporary webcam snapshots. |
| `OUTPUT_TEXT_FILE` | File where the initial transcript is saved. |

---

## 🔧 Troubleshooting

* **"Error: Image file not found":** Ensure `test.jpg` is in the same directory as the script when using Static Mode.
* **Webcam fails to open:** Check if another app (Zoom, Teams) is using the camera. If you have multiple cameras, change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` in the code.
* **CUDA / GPU Errors:** The code defaults to `gpu=True` for EasyOCR. If you do not have an NVIDIA GPU, change this to `gpu=False` in the `main()` function of the scripts.
* **Key presses not working:**
    * **Linux/macOS:** You may need to run the script with `sudo`.
    * **Live Mode:** Ensure the "Webcam Window" is focused when pressing camera keys (`c`, `y`), and the "Terminal" is focused when chatting.

---

## 📜 License

This project is open-source. Feel free to modify, improve, and share it!
