
#  ESP32 AI Chatbot Server

Built with FastAPI, this backend facilitates ESP32 audio communication—capturing device audio, leveraging LLM processing, and outputting synthesized speech responses.

---

##  How to Run
### 1. Clone and CD into the repository

####  Linux / macOS /Windows
```bash
git clone https://github.com/syed-dce/ESP32_AI_chatbot.git
cd ESP32_AI_chatbot
````


### 2. Create and activate virtual environment

####  Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
````

####  Windows (CMD)

```cmd
python -m venv venv
venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Run the FastAPI server

```bash
python3 main.py
# or (on Windows)
python main.py
```
The server would now be running on http://127.0.0.1:8000 and would take use http://127.0.0.1:8000/convert route to input the recorded audio from the I2S microphone (eg:INMP441) of the ESP32-microcontroller and returns the LLM response in an audio file (.wav or .mp3- can be changed as needed) which can be played through speaker options such as I2S DAC Module (eg:MAX98357A).
Basically an HTTP server implementation of sending requests (prompts) to the LLM and receiving responses.

---

##  Routes

### 1.`GET "/"`

* Health check endpoint.
* Returns:

  ```json
  {
    "status": "healthy"
  }
  ```

---

### 2.`POST "/convert"`

* Accepts audio file (WAV/MP3).
* Transcribes speech to text.
* Sends to LLM for response generation.
* Converts response text to audio.
* Returns audio as a streaming WAV/MP3 response.

---
###  Optional: Test the `/convert` Route Locally

You can simulate an ESP32 audio POST request using the following script:

```
request/python_simulation/post_simulation.py
```

This script is useful for logical and intuitive testing of the POST request and response retrieval functionality without actual hardware.


---
##  Tech Stack

* FastAPI
* ESP32 HTTP client integration ( inside requests folder )
* Redis (for conversation memory/short term)
* ChromaDB (for personal information recall/long term)
* Speech Recognition & Text-to-Speech
* LangChain and Gemini AI for initial implementation testing
* SQLite (storage of ChromaDB personal information recall)
---


