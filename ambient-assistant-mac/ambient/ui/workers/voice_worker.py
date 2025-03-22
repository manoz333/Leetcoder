"""Worker thread for voice input processing."""
import logging
import tempfile
from PyQt6.QtCore import QThread, pyqtSignal


class VoiceWorker(QThread):
    """Worker thread for voice input using OpenAI Whisper API."""
    finished = pyqtSignal(str)
    status = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Record and process audio using OpenAI Whisper API."""
        try:
            from openai import OpenAI
            import sounddevice as sd
            import soundfile as sf
            import numpy as np
            import os
            
            self.status.emit("Listening... Speak now")
            
            # Record audio
            fs = 44100  # Sample rate
            duration = 5  # seconds
            self.status.emit(f"Recording for {duration} seconds...")
            
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
            sd.wait()  # Wait until recording is finished
            
            # Save to temporary file
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            sf.write(temp_audio.name, recording, fs)
            
            # Get API key
            api_key = self.settings_manager.get_setting('openai_api_key')
            if not api_key:
                raise ValueError("OpenAI API key not found in settings")
                
            # Use OpenAI Whisper API
            client = OpenAI(api_key=api_key)
            self.status.emit("Processing speech with Whisper API...")
            
            with open(temp_audio.name, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    prompt="This is a coding assistant. The user may ask about programming languages, code, or technical concepts."
                )
            
            # Clean up temp file
            os.unlink(temp_audio.name)
            
            if transcription.text:
                self.finished.emit(transcription.text)
            else:
                self.status.emit("No speech detected")
                
        except ImportError as e:
            self.error.emit(f"Required packages not installed: {str(e)}")
            self.logger.error(f"Import error in voice processing: {str(e)}")
        except Exception as e:
            self.error.emit(str(e))
            self.logger.error(f"Error in voice processing: {str(e)}") 