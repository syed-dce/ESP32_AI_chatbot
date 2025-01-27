#==============================IMPORTS AND JUST GETTING SCRIPTS FROM PYTHON PACKAGES(services/local/database)=====================
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from io import BytesIO
import threading, json, httpx, os, time, uvicorn, asyncio
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from redis import Redis
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import urllib.parse

load_dotenv()

#imports from services modules
from services.STT import transcribe_audio
from services.TTS import synthesize_audio
from services.LLM import generate_response
from services.chroma_store import store_chromadb
from services.chroma_store import query_chromadb

#getting redis (caching recent conversation-short term memory implementation) related details from .env file
REDIS_HOST=os.getenv("REDIS_HOST")
REDIS_PORT=os.getenv("REDIS_PORT")

#=================================SETTING UP THE FASTAPI APP (INTIALIZE POSTGRESQL ORM, LIFESPAN, REDIS CACHE, SCHEDULERS)====================================
# Use lifespan for startup/shutdown logic.... set up redis client
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis(host=REDIS_HOST, port=REDIS_PORT,db=3)
    yield  # app runs here
    # Cleanup
    app.state.redis.close()
    print("Redis client closed.")

app = FastAPI(lifespan=lifespan)

# Add CORS middleware, since everything running on local development just allowing all origins and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allow all headers
)

def format_past_conversations(past_conversations):
    lines = []
    for msg in past_conversations[-10:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            lines.append(f"User: {content}")
        elif role == "assistant":
            lines.append(f"Assistant: {content}")
        else:
            lines.append(content)
    return "\n".join(lines)

#=================================================ROUTES===================================================================
#just a simple route to check if the server is active (taking in requests)
@app.get("/")
def return_status():
    return {"status":"healthy"}

#the only needed route tbh.......takes in the audio request (in .wav form as of now) sent by esp32s (using HTTP.client module), and then does transcription, LLM response generation and return a converted audio reponse (which can then be played using ESP32 audio output forms)
@app.post("/convert")
async def convert(request: Request,background_tasks:BackgroundTasks, audio: UploadFile = File(...)):
    # 1. Validate content type
    valid_types = ["audio/", "application/octet-stream"]
    if not any(audio.content_type.startswith(t) for t in valid_types):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")

    # 2. Read audio bytes from UploadFile
    audio_bytes = await audio.read()

    # 3. Transcribe audio (speech-to-text)
    try:
        user_text = transcribe_audio(audio_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech transcription failed: {str(e)}")
    
    print("USER PROMTPT: ", user_text)


    

    # 4. Generate response text from LLM
    redis = request.app.state.redis
    user_id = 1
    background_tasks.add_task(store_chromadb, user_text, str(user_id))
    redis_key = f"convo:{user_id}"

    # Retrieve and parse past conversations from redis

    past_data = redis.get(redis_key)
    past_conversations = json.loads(past_data) if past_data else []
    user_info = query_chromadb(user_text, str(user_id))
    user_info_str = ";".join(user_info)

    context_text = format_past_conversations(past_conversations)
    llm_text = generate_response(user_text, user_id, context_text, user_info_str)

    #Storing the previous convos in the redis cache
    past_conversations.append({"role": "user", "content": user_text})
    past_conversations.append({"role": "assistant", "content": llm_text})
    redis.set(redis_key, json.dumps(past_conversations[-20:]))

    # 5. Synthesize audio (text-to-speech)
    try:
        response_audio_bytes = synthesize_audio(llm_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio synthesis failed: {str(e)}")

    # 6. Return audio file as StreamingResponse (mp3)

    return StreamingResponse(BytesIO(response_audio_bytes), media_type="audio/mpeg")


#============================START THE UVICORN SERVER BY RUNNING main.py=========================================================

if __name__=="__main__":
    #this line runs the uvicorn asgi server on localhost
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)