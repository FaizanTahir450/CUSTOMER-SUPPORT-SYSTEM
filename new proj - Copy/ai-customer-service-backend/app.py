import sys
import os

# Disable telemetry completely
try:
    import chromadb
    if hasattr(chromadb, "telemetry"):
        chromadb.telemetry.capture = lambda *args, **kwargs: None
except Exception as e:
    print(f"Telemetry patch failed: {e}")

from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import re
import base64
import asyncio
from typing import Optional
from dotenv import load_dotenv

# Import your existing components
from pdf_processor import PDFProcessor
from vector_store_manager import VectorStoreManager
from memory_manager import MemoryManager
from chatbot import LAMAChatbot
from langchain.agents import AgentExecutor, create_openai_functions_agent

app = FastAPI(title="LAMA Customer Support AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Initialize AI Components -----------------
print("🤖 Initializing AI System...")

load_dotenv()
PDF_PATH = "Lama.pdf"

# Check if PDF exists
if not os.path.exists(PDF_PATH):
    print(f"❌ PDF '{PDF_PATH}' not found!")
    chatbot = None
else:
    try:
        # Setup vector store
        vector_manager = VectorStoreManager()
        
        if not vector_manager.vector_store_exists():
            print("🔄 Creating vector store...")
            processor = PDFProcessor()
            chunks = processor.process_pdf(PDF_PATH)
            if chunks:
                vector_store = vector_manager.create_vector_store(chunks)
                print(f"✅ Vector store created with {len(chunks)} chunks")
            else:
                print("❌ Failed to process PDF")
                chatbot = None
        else:
            vector_store = vector_manager.load_vector_store()
            print("✅ Vector store loaded")
        
        # Initialize chatbot
        memory_manager = MemoryManager()
        chatbot = LAMAChatbot(vector_store, memory_manager)
        
        # Initialize agent
        agent = create_openai_functions_agent(
            chatbot.llm,
            [chatbot.retriever_tool],
            prompt=chatbot.prompt
        )
        
        executor = AgentExecutor(
            agent=agent,
            tools=[chatbot.retriever_tool],
            memory=memory_manager.get_memory(),
            verbose=False  # Set to False for cleaner logs
        )
        chatbot.set_agent_executor(executor)
        print("✅ AI system ready!")
        
    except Exception as e:
        print(f"❌ AI initialization failed: {e}")
        import traceback
        traceback.print_exc()
        chatbot = None

# ----------------- Utility Functions -----------------

def clean_markdown_for_tts(text: str) -> str:
    """Remove markdown formatting from text for clean TTS output"""
    if not text:
        return ""
    
    # Remove bold/italic markers
    text = re.sub(r'\*\*|\*|__|_', '', text)
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove inline code
    text = re.sub(r'`[^`]*`', '', text)
    # Remove headers
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    # Remove lists
    text = re.sub(r'^[*-]\s+', '', text, flags=re.MULTILINE)
    # Remove links
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Clean up multiple spaces
    text = ' '.join(text.split())
    
    return text.strip()

# ----------------- API Endpoints -----------------

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "LAMA Customer Support AI API",
        "status": "running",
        "chatbot_ready": chatbot is not None,
        "endpoints": [
            "/chat - POST - Text chat",
            "/text-to-speech - POST - Convert text to speech",
            "/speech-to-text - POST - Convert audio to text",
            "/chat-with-tts - POST - Chat with TTS response",
            "/health - GET - Health check"
        ]
    }

@app.post("/chat")
async def chat_endpoint(request: Request):
    """Simple text chat endpoint"""
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized. Check if PDF exists.")
    
    data = await request.json()
    message = data.get("message", "")
    
    if not message:
        raise HTTPException(status_code=400, detail="Empty message")
    
    print(f"📝 Customer: {message}")
    
    try:
        response = chatbot.ask(message)
        print(f"🤖 LAMA: {response[:100]}...")
        
        return {
            "success": True,
            "response": response,
            "clean_text": clean_markdown_for_tts(response)
        }
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/text-to-speech")
async def text_to_speech_endpoint(request: Request):
    """Convert text to speech audio"""
    data = await request.json()
    text = data.get("text", "")
    
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    try:
        # Clean the text
        clean_text = clean_markdown_for_tts(text)
        
        # Generate TTS using edge_tts
        import edge_tts
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            temp_path = tmp.name
        
        # Generate speech
        communicate = edge_tts.Communicate(clean_text, voice="en-US-AriaNeural")
        await communicate.save(temp_path)
        
        # Read and encode audio
        with open(temp_path, 'rb') as f:
            audio_bytes = f.read()
        
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Cleanup
        os.unlink(temp_path)
        
        return {
            "success": True,
            "original_text": text,
            "clean_text": clean_text,
            "audio": audio_base64,
            "audio_format": "mp3"
        }
        
    except ImportError:
        raise HTTPException(status_code=500, detail="edge_tts not installed. Run: pip install edge-tts")
    except Exception as e:
        print(f"❌ TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

# Add this function to your app.py
def convert_webm_to_wav(webm_bytes: bytes) -> bytes:
    """Convert WebM audio bytes to WAV format"""
    import subprocess
    import tempfile
    import os
    
    # Create temp files
    with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as webm_file:
        webm_path = webm_file.name
        webm_file.write(webm_bytes)
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
        wav_path = wav_file.name
    
    try:
        # Use ffmpeg to convert webm to wav
        cmd = [
            'ffmpeg', '-i', webm_path,
            '-acodec', 'pcm_s16le',
            '-ac', '1',
            '-ar', '16000',
            wav_path,
            '-y'  # Overwrite output file
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        # Read converted wav file
        with open(wav_path, 'rb') as f:
            wav_bytes = f.read()
        
        return wav_bytes
        
    except Exception as e:
        print(f"WebM to WAV conversion failed: {e}")
        # Fallback: return original bytes
        return webm_bytes
    finally:
        # Cleanup temp files
        for path in [webm_path, wav_path]:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except:
                pass

# Update the speech-to-text endpoint:
@app.post("/speech-to-text")
async def speech_to_text_endpoint(audio_file: UploadFile = File(...)):
    """Convert audio to text with format detection"""
    try:
        import speech_recognition as sr
        
        # Read audio file
        audio_bytes = await audio_file.read()
        filename = audio_file.filename.lower()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as tmp:
            temp_path = tmp.name
            tmp.write(audio_bytes)
        
        # Check file format and convert if necessary
        if filename.endswith('.webm') or filename.endswith('.weba'):
            # Convert WebM to WAV
            try:
                wav_bytes = convert_webm_to_wav(audio_bytes)
                # Save converted file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_tmp:
                    wav_path = wav_tmp.name
                    wav_tmp.write(wav_bytes)
                
                # Use the converted WAV file
                temp_path = wav_path
            except Exception as conv_error:
                print(f"Conversion failed, trying original: {conv_error}")
        
        try:
            # Initialize recognizer
            recognizer = sr.Recognizer()
            
            # Load audio file
            with sr.AudioFile(temp_path) as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Record the audio
                audio = recognizer.record(source)
            
            # Convert to text
            text = recognizer.recognize_google(audio)
            
            # Cleanup
            os.unlink(temp_path)
            
            return {
                "success": True,
                "text": text,
                "message": "Speech converted to text successfully"
            }
            
        except sr.UnknownValueError:
            os.unlink(temp_path)
            return {
                "success": False,
                "text": "",
                "message": "Could not understand audio. Please speak clearly."
            }
            
        except sr.RequestError as e:
            os.unlink(temp_path)
            return {
                "success": False,
                "text": "",
                "message": f"Google Speech Recognition error: {str(e)}. Check internet connection."
            }
            
        except Exception as e:
            os.unlink(temp_path)
            print(f"❌ Speech recognition error: {e}")
            return {
                "success": False,
                "text": "",
                "message": f"Speech recognition failed: {str(e)}"
            }
            
    except ImportError:
        raise HTTPException(
            status_code=500, 
            detail="speech_recognition not installed. Run: pip install SpeechRecognition"
        )
    except Exception as e:
        print(f"❌ General speech-to-text error: {e}")
        raise HTTPException(status_code=500, detail=f"Speech to text failed: {str(e)}")
    
@app.post("/chat-with-tts")
async def chat_with_tts_endpoint(request: Request):
    """Chat with automatic TTS response"""
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    data = await request.json()
    message = data.get("message", "")
    
    if not message:
        raise HTTPException(status_code=400, detail="Empty message")
    
    print(f"📝 Customer: {message}")
    
    try:
        # Get AI response
        response = chatbot.ask(message)
        clean_response = clean_markdown_for_tts(response)
        print(f"🤖 LAMA: {response[:100]}...")
        
        # Generate TTS audio
        audio_base64 = None
        try:
            import edge_tts
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                temp_path = tmp.name
            
            communicate = edge_tts.Communicate(clean_response, voice="en-US-AriaNeural")
            await communicate.save(temp_path)
            
            with open(temp_path, 'rb') as f:
                audio_bytes = f.read()
            
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            os.unlink(temp_path)
            
        except Exception as e:
            print(f"⚠️ TTS generation failed: {e}")
            # Continue without audio
        
        return {
            "success": True,
            "response": response,
            "clean_text": clean_response,
            "audio": audio_base64,
            "has_audio": audio_base64 is not None
        }
        
    except Exception as e:
        print(f"❌ Chat with TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Test speech recognition availability
    speech_available = True
    try:
        import speech_recognition
    except ImportError:
        speech_available = False
    
    # Test TTS availability
    tts_available = True
    try:
        import edge_tts
    except ImportError:
        tts_available = False
    
    return {
        "status": "healthy",
        "chatbot": chatbot is not None,
        "speech_recognition": speech_available,
        "text_to_speech": tts_available,
        "pdf_exists": os.path.exists(PDF_PATH) if PDF_PATH else False,
        "vector_store": True  # We'll assume it's working
    }

# ----------------- Run Server -----------------

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🤖 LAMA AI - Starting Server")
    print("="*60)
    print(f"Chatbot: {'✅ Ready' if chatbot else '❌ Not ready'}")
    print(f"PDF: {'✅ Found' if os.path.exists(PDF_PATH) else '❌ Missing: ' + PDF_PATH}")
    print(f"Server: http://localhost:8000")
    print("="*60)
    print("\n📋 Available endpoints:")
    print("  POST /chat             - Text chat")
    print("  POST /text-to-speech   - Convert text to speech")
    print("  POST /speech-to-text   - Convert audio to text")
    print("  POST /chat-with-tts    - Chat with TTS response")
    print("  GET  /health           - Health check")
    print("="*60)
    
    # Check for required packages
    print("\n🔍 Checking dependencies...")
    try:
        import speech_recognition
        print("✅ speech_recognition: OK")
    except ImportError:
        print("❌ speech_recognition: MISSING - Run: pip install SpeechRecognition")
    
    try:
        import edge_tts
        print("✅ edge_tts: OK")
    except ImportError:
        print("❌ edge_tts: MISSING - Run: pip install edge-tts")
    
    try:
        import chromadb
        print("✅ chromadb: OK")
    except ImportError:
        print("❌ chromadb: MISSING - Run: pip install chromadb")
    
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")