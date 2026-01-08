import threading
import keyboard
import speech_recognition as sr
import pyttsx3
import re
import time
import warnings
import tempfile
import os
import asyncio
import edge_tts
import sys

# Suppress warnings
warnings.filterwarnings("ignore")

class LiveWhisperSTT:
    def __init__(self):
        print("🔊 Initializing Google Speech Recognition System...")
        
        # Initialize Speech Recognition
        try:
            self.recognizer = sr.Recognizer()
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 170)
            self.stop_listening = False
            self.partial_text = ""
            self.is_speaking = False  # Track if TTS is active
            self.tts_stop_event = threading.Event()  # Event to stop TTS
            
            # Test microphone
            print("🔍 Testing microphone...")
            mic_list = sr.Microphone.list_microphone_names()
            if not mic_list:
                print("❌ No microphones found!")
                raise Exception("No microphones detected")
            
            print(f"✅ Found {len(mic_list)} microphone(s)")
            print("✅ Speech Recognition ready")
            
        except Exception as e:
            print(f"❌ Failed to initialize speech system: {e}")
            print("\n💡 TROUBLESHOOTING:")
            print("1. Make sure a microphone is connected")
            print("2. Check Windows microphone permissions")
            print("3. Install required packages: pip install speechrecognition pyttsx3 keyboard")
            raise
        
        # Initialize TTS
        print("🗣️ Initializing Text-to-Speech...")
        try:
            # Try to find a natural-sounding voice
            voices = self.engine.getProperty('voices')
            if voices:
                # Prefer female voices
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        print(f"✅ TTS using voice: {voice.name}")
                        break
                    elif 'david' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        print(f"✅ TTS using voice: {voice.name}")
                        break
            print("✅ TTS engine ready")
        except Exception as e:
            print(f"⚠️ TTS initialization failed: {e}")
        
        # Edge TTS for better voices (optional)
        self.edge_tts_available = False
        try:
            import edge_tts
            self.edge_tts_available = True
            print("✅ Edge TTS available for better voices")
        except ImportError:
            print("⚠️ Edge TTS not installed. Using pyttsx3.")
    
    # ----------------- STT Methods -----------------
    def _wait_for_key(self):
        """Stops listening when any key is pressed."""
        try:
            keyboard.read_key()
            self.stop_listening = True
            print("\n🛑 Key pressed, stopping listening...")
        except:
            self.stop_listening = True
    
    def listen_with_google(self):
        """Listens to the user's speech until a key is pressed."""
        self.stop_listening = False
        with sr.Microphone() as source:
            print("🎤 Speak now (press any key to stop)...")
            self.recognizer.adjust_for_ambient_noise(source)

            key_thread = threading.Thread(target=self._wait_for_key)
            key_thread.start()

            audio_data = []
            while not self.stop_listening:
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    audio_data.append(audio)
                except sr.WaitTimeoutError:
                    pass

        if not audio_data:
            print("⚠️ No speech detected.")
            return None

        combined = audio_data[0]
        for extra in audio_data[1:]:
            combined = sr.AudioData(
                combined.frame_data + extra.frame_data,
                combined.sample_rate,
                combined.sample_width
            )

        try:
            text = self.recognizer.recognize_google(combined)
            print(f"🧠 You said: {text}")
            self.partial_text = text
            return text
        except sr.UnknownValueError:
            print("⚠️ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Google API error: {e}")
            print("💡 Check your internet connection")
            return None
        except Exception as e:
            print(f"⚠️ Error recognizing speech: {e}")
            return None
    
    def start_recording(self):
        """Main function to start listening"""
        return self.listen_with_google()
    
    def stop_recording(self):
        """Stop any ongoing recording"""
        self.stop_listening = True
    
    # ----------------- TTS Methods with Interruption -----------------
    def _clean_for_tts(self, text):
        """Clean text for TTS"""
        if not text:
            return ""
        
        # Remove markdown
        text = re.sub(r'\*\*|\*|__|_|`|#', '', text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Clean up brackets and parentheses
        text = re.sub(r'\[.*?\]|\(.*?\)', '', text)
        
        # Remove emojis and special characters
        text = re.sub(r'[^\w\s.,!?\-:\'"]', '', text)
        
        return text.strip()
    
    def _chunk_text(self, text, max_length=400):
        """Splits long text into smaller chunks for safer TTS playback."""
        chunks, current = [], ""
        for sentence in re.split(r'(?<=[.!?]) +', text.strip()):
            if len(current) + len(sentence) > max_length:
                chunks.append(current.strip())
                current = sentence
            else:
                current += " " + sentence
        if current:
            chunks.append(current.strip())
        return chunks
    
    def _monitor_interruption(self):
        """Monitor for interruption key (Enter) during TTS"""
        print("   💡 Press 'Enter' to interrupt speech and ask new question")
        try:
            input()  # Wait for Enter key
            self.tts_stop_event.set()  # Signal to stop TTS
            print("\n🛑 Speech interrupted!")
        except:
            pass
    
    def speak_with_pyttsx3_interruptible(self, text):
        """Speaks text with interruption capability using pyttsx3"""
        if not self.tts_engine:
            print("⚠️ TTS engine not available")
            return
        
        self.is_speaking = True
        self.tts_stop_event.clear()  # Reset stop event
        
        try:
            self.engine.stop()
            
            # Clean text
            text = self._clean_for_tts(text)
            if not text:
                self.is_speaking = False
                return
            
            # Start interruption monitoring thread
            interrupt_thread = threading.Thread(target=self._monitor_interruption, daemon=True)
            interrupt_thread.start()
            
            # Split into sentences
            sentences = re.split(r'(?<=[.!?]) +', text.strip())
            
            for sentence in sentences:
                if sentence and not self.tts_stop_event.is_set():
                    self.engine.say(sentence)
                    self.engine.runAndWait()
                    
                    # Check if interrupted between sentences
                    if self.tts_stop_event.is_set():
                        print("✅ Speech stopped by user")
                        break
                    
                    time.sleep(0.1)  # Small pause between sentences
                else:
                    break
            
            if not self.tts_stop_event.is_set():
                print("✅ Speech completed")
            
        except Exception as e:
            print(f"⚠️ Speech error: {e}")
        finally:
            self.is_speaking = False
    
    async def _speak_with_edge_tts_interruptible(self, text):
        """Speak using Edge TTS with interruption capability"""
        if not text.strip():
            return
        
        self.is_speaking = True
        self.tts_stop_event.clear()  # Reset stop event
        
        temp_file = None
        try:
            # Start interruption monitoring thread
            interrupt_thread = threading.Thread(target=self._monitor_interruption, daemon=True)
            interrupt_thread.start()
            
            # Create temp file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                temp_file = tmp.name
            
            # Generate speech with female voice
            communicate = edge_tts.Communicate(text, voice="en-US-AriaNeural")
            await communicate.save(temp_file)
            
            # Play using pygame if available
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()
                
                print("🔊 Playing audio...")
                # Check for interruption while playing
                while pygame.mixer.music.get_busy() and not self.tts_stop_event.is_set():
                    await asyncio.sleep(0.1)
                
                if self.tts_stop_event.is_set():
                    pygame.mixer.music.stop()
                    print("✅ Speech stopped by user")
                else:
                    print("✅ Speech completed")
                    
            except ImportError:
                # Fallback to pyttsx3 interruptible version
                self.speak_with_pyttsx3_interruptible(text)
            
        except Exception as e:
            print(f"⚠️ Edge TTS Error: {e}")
        finally:
            self.is_speaking = False
            # Cleanup
            try:
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
    
    def speak_chatbot_text(self, text, use_edge_tts=None):
        """Main TTS function with interruption capability"""
        if not text.strip():
            return
        
        # Check if already speaking
        if self.is_speaking:
            print("🛑 Stopping current speech...")
            self.tts_stop_event.set()
            time.sleep(0.5)  # Wait for current speech to stop
        
        # Clean text
        text = self._clean_for_tts(text)
        if not text:
            return
        
        print(f"🔊 Speaking: {text[:80]}...")
        
        # Determine which TTS to use
        use_edge = use_edge_tts if use_edge_tts is not None else self.edge_tts_available
        
        if use_edge:
            # Run Edge TTS async with interruption
            asyncio.run(self._speak_with_edge_tts_interruptible(text))
        else:
            # Use pyttsx3 with interruption
            self.speak_with_pyttsx3_interruptible(text)
    
    def stop_speech(self):
        """Force stop any ongoing speech"""
        if self.is_speaking:
            print("🛑 Stopping speech...")
            self.tts_stop_event.set()
            self.engine.stop()  # Stop pyttsx3 engine
            
            # Also stop pygame if playing
            try:
                import pygame
                pygame.mixer.music.stop()
            except:
                pass
            
            self.is_speaking = False
            return True
        return False


# ----------------- Test Function -----------------
if __name__ == "__main__":
    print("="*60)
    print("🎤 SPEECH SYSTEM WITH INTERRUPTION")
    print("="*60)
    
    # Initialize
    try:
        stt = LiveWhisperSTT()
        print("✅ System ready!")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        exit(1)
    
    # Test interruption
    print("\n🔊 Testing interruption feature...")
    print("The system will speak a long text.")
    print("Press 'Enter' anytime to interrupt and type a new question.")
    print("-"*50)
    
    long_text = """
    This is a test of the speech interruption feature. 
    The assistant will speak this long text to demonstrate how you can interrupt it.
    When you press the Enter key, the speech will stop immediately.
    You can then type or speak a new question without waiting for this to finish.
    This is very useful when you want to ask follow-up questions or clarify something.
    The system should respond quickly to your interruptions.
    """
    
    # Run TTS in a separate thread so we can test interruption
    def run_tts():
        stt.speak_chatbot_text(long_text)
    
    tts_thread = threading.Thread(target=run_tts)
    tts_thread.start()
    
    # Wait a bit then show we can interrupt
    time.sleep(3)
    print("\n💡 Try pressing 'Enter' now to interrupt the speech!")
    
    # Wait for thread to finish or be interrupted
    tts_thread.join(timeout=10)
    
    print("\n✅ Test completed!")