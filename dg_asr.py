from dotenv import load_dotenv
import os
import threading
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)

# Load environment variables
load_dotenv()



class TranscriptionService:
    def __init__(self):
        self.is_finals = []
        self.speech_final = None
        self.lock = threading.Lock()

        API_KEY = os.getenv("DEEPGRAM_API_KEY")
        config = DeepgramClientOptions(options={"keepalive": "true"})
        self.deepgram = DeepgramClient(API_KEY, config)
        self.dg_connection = self.deepgram.listen.live.v("1")

        self.options = LiveOptions(
            model="nova-2-drivethru",
            language="en",
            channels=1,
            #encoding="linear16",
            #sample_rate=16000,
            encoding="mulaw",
            sample_rate=8000,
            endpointing=10,
            #punctuate=True
        )
        
        self._initialize_events()
        self.dg_connection.start(self.options)

    def _initialize_events(self):
        self.dg_connection.on(LiveTranscriptionEvents.Open, self.on_open)
        self.dg_connection.on(LiveTranscriptionEvents.Transcript, self.on_message)
        self.dg_connection.on(LiveTranscriptionEvents.SpeechStarted, self.on_speech_started)
        self.dg_connection.on(LiveTranscriptionEvents.Close, self.on_close)
        self.dg_connection.on(LiveTranscriptionEvents.Error, self.on_error)
        self.dg_connection.on(LiveTranscriptionEvents.Unhandled, self.on_unhandled)

    def on_open(self, self_, open, **kwargs):
        pass
            
    def on_message(self, self_, result, **kwargs):
        sentence = result.channel.alternatives[0].transcript
        if not sentence:
            return

        if result.is_final:
            with self.lock:
                self.is_finals.append(sentence)
                if result.speech_final:
                    self.speech_final = " ".join(self.is_finals)
                    print(self.speech_final)
                    self.is_finals = []
                    

    def on_speech_started(self, self_, speech_started, **kwargs):
        pass
        
    

    def on_close(self, self_, close, **kwargs):
        pass

    def on_error(self, self_, error, **kwargs):
        self.dg_connection.finish()
        pass

    def on_unhandled(self, self_, unhandled, **kwargs):
        pass
    
    def microphone_stream(self):
        microphone = Microphone(self.dg_connection.send)
        microphone.start()
        input("")  # Wait for user input to finish
        microphone.finish()
        self.dg_connection.finish()
    
    def streaming_data(self, buffer):
        self.dg_connection.send(buffer)
        return self.speech_final
    
    def close_connection(self):
        self.dg_connection.finish()



