# Gemini Vision Voice Assistant

A multimodal AI assistant designed to help visually impaired users "chat" with static images. This tool combines **Optical Character Recognition (OCR)**, **Generative AI**, and **Neural Text-to-Speech** to provide real-time, conversational insights about visual content.

## Features

* **Hybrid Analysis:** Uses `EasyOCR` to read hard text and `Google Gemini 2.5` to understand visual context.
* **Natural Voice Output:** Integrated `Edge-TTS` (Microsoft Edge's Neural Voice) for high-quality, human-sounding speech.
* **Interruptible Audio:** Features a smart playback system using `sounddevice`—users can cut the AI off mid-sentence to ask new questions instantly.
* **Push-to-Talk Interface:** Simple "Hold 'V' to speak" control scheme ensures the AI only listens when you want it to.
* **Contextual Memory:** The AI remembers previous questions, allowing for a natural back-and-forth conversation.

## 🛠️ Prerequisites

* **Python 3.8+**
* **Google Gemini API Key** (Get one from [Google AI Studio](https://aistudio.google.com/))
* **Hardware:** Microphone and Speakers.
* **(Optional) NVIDIA GPU:** The script is currently configured to use a GPU for OCR acceleration.

## 📦 Installation

1.  **Clone or Download** this repository.
2.  **Install the required Python libraries:**

    ```bash
    pip install google-generativeai easyocr speechrecognition keyboard edge-tts sounddevice soundfile numpy pillow
    ```

    *Note: On Linux systems, you may also need to install PortAudio (`sudo apt-get install libportaudio2`).*

3.  **Set up your API Key:**
    Open `vission_ai_image.py` (or your script name) and find the configuration section:
    ```python
    GEMINI_API_KEY = "YOUR_API_KEY_HERE"
    ```
    Replace the placeholder with your actual Gemini API key.

4.  **Prepare Input:**
    Place the image you want to analyze in the project folder and name it `test.jpg`, or update the `IMAGE_TO_READ` variable in the code.

## 🚀 Usage

1.  **Run the script:**
    ```bash
    python vission_ai_image.py
    ```
    *(Note: On Linux/macOS, you may need to run as `sudo` because the `keyboard` library requires root privileges to detect key presses).*

2.  **Calibration:**
    The script will print `[3/6] Calibrating Microphone...`. **Stay silent for 1 second** while it adjusts to your background noise.

3.  **The Conversation:**
    * The AI will automatically analyze the image and speak a **brief summary**.
    * **To Ask a Question:** Hold down the **`v`** key. Speak your question. Release **`v`** when finished.
    * **To Stop the AI Talking:** If the answer is too long, just press/hold **`v`** to interrupt and ask something else.
    * **To Quit:** Press **`q`**.

## ⚙️ Configuration

You can adjust these variables at the top of the script:

| Variable | Description |
| :--- | :--- |
| `GEMINI_API_KEY` | Your authentication key for Google Gemini. |
| `IMAGE_TO_READ` | The filename of the image to analyze (e.g., `'menu.jpg'`). |
| `OUTPUT_TEXT_FILE` | The file where the initial summary transcript is saved. |

## 🔧 Troubleshooting

* **"Error: Image file not found"**: Ensure `test.jpg` is in the same directory as the script.
* **CUDA / GPU Errors**: The code defaults to `ocr_engine = easyocr.Reader(['en'], gpu=True)`. If you do not have an NVIDIA GPU, change `gpu=True` to `gpu=False` in the `main()` function.
* **Microphone Errors**: Ensure your default system microphone is set correctly in your OS sound settings.

## 📜 License

This project is open-source. Feel free to modify and improve it!