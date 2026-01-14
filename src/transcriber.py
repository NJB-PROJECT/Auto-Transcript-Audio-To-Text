import os
# from faster_whisper import WhisperModel
import threading

class Transcriber:
    def __init__(self, model_size="small", device="cpu", compute_type="int8"):
        """
        Inisialisasi model Faster Whisper.
        :param model_size: Ukuran model ('tiny', 'base', 'small', 'medium', 'large').
        :param device: 'cpu' atau 'cuda'.
        :param compute_type: 'int8', 'float16', dll.
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None
        # self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print(f"Transcriber initialized with model: {model_size}")

    def load_model(self):
        """Memuat model (lazy loading jika diperlukan)"""
        if self.model is None:
            try:
                from faster_whisper import WhisperModel
                print("Loading Whisper Model...")
                self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
                print("Model loaded successfully.")
            except ImportError:
                print("Error: faster_whisper not installed. Using mock mode.")
                self.model = "MOCK"

    def transcribe_segment(self, audio_data, sample_rate=16000):
        """
        Mentranskrip segmen audio raw (numpy array).
        Digunakan untuk real-time transcription.
        """
        if self.model is None:
            self.load_model()

        if self.model == "MOCK":
            return " [Mock Transcript] "

        segments, info = self.model.transcribe(audio_data, beam_size=5, language="id")

        text = ""
        for segment in segments:
            text += segment.text + " "
        return text.strip()

    def transcribe_file(self, file_path):
        """
        Mentranskrip file audio/video.
        """
        if self.model is None:
            self.load_model()

        if self.model == "MOCK":
             return [f"Mock transcript for {file_path}"]

        segments, info = self.model.transcribe(file_path, beam_size=5, language="id")

        results = []
        for segment in segments:
            results.append(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
        return results
