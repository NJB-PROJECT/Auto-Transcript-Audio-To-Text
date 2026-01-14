import threading
import time
import queue
import platform
import numpy as np
import scipy.signal

# Public flag to check system audio availability
IS_SYSTEM_AUDIO_AVAILABLE = False

try:
    import pyaudiowpatch as pyaudio
    IS_SYSTEM_AUDIO_AVAILABLE = True
except ImportError:
    try:
        import pyaudio
        IS_SYSTEM_AUDIO_AVAILABLE = False
    except ImportError:
        pyaudio = None
        IS_SYSTEM_AUDIO_AVAILABLE = False

class AudioRecorder:
    def __init__(self, target_sample_rate=16000, chunk_duration=3):
        """
        :param target_sample_rate: Sample rate needed by Whisper (default 16000).
        :param chunk_duration: Duration of each audio chunk to transcribe (in seconds).
        """
        self.target_sample_rate = target_sample_rate
        self.chunk_duration = chunk_duration
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.thread = None

        # Expose the global flag status through instance for easier access
        self.is_system_audio_available = IS_SYSTEM_AUDIO_AVAILABLE

    def _get_loopback_device(self, p):
        """
        [Windows Only] Helper to find the loopback device.
        """
        try:
            # Get default WASAPI output device
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

            if not default_speakers["isLoopbackDevice"]:
                for loopback in p.get_loopback_device_info_generator():
                    if default_speakers["name"] in loopback["name"]:
                        return loopback
            return default_speakers
        except Exception as e:
            print(f"Error finding loopback device: {e}")
            return None

    def _process_audio_chunk(self, raw_data, input_rate, channels):
        """
        Convert raw bytes -> float32 numpy array -> Downmix to Mono -> Resample to 16kHz
        """
        # 1. Convert bytes to int16 numpy array
        audio_int16 = np.frombuffer(raw_data, dtype=np.int16)

        # 2. Normalize to float32 (-1.0 to 1.0)
        audio_float = audio_int16.astype(np.float32) / 32768.0

        # 3. Reshape if multi-channel
        if channels > 1:
            audio_float = audio_float.reshape(-1, channels)
            # Downmix to mono (average of channels)
            audio_mono = audio_float.mean(axis=1)
        else:
            audio_mono = audio_float

        # 4. Resample if rate differs from target
        if input_rate != self.target_sample_rate:
            num_samples = int(len(audio_mono) * self.target_sample_rate / input_rate)
            audio_resampled = scipy.signal.resample(audio_mono, num_samples)
            return audio_resampled

        return audio_mono

    def _record_loop(self):
        """Internal recording loop running in a thread."""
        print("Recording started...")

        # Determine if we are on Windows and have the patch
        use_loopback = self.is_system_audio_available and platform.system() == "Windows"

        if pyaudio:
             with pyaudio.PyAudio() as p:
                if use_loopback:
                    # --- SYSTEM AUDIO (LOOPBACK) ---
                    device_info = self._get_loopback_device(p)
                    if not device_info:
                        print("No Loopback device found. Falling back to default input.")
                        use_loopback = False
                    else:
                        print(f"Recording from Loopback: {device_info['name']}")
                        input_rate = int(device_info["defaultSampleRate"])
                        channels = device_info["maxInputChannels"]
                        input_device_index = device_info["index"]

                if not use_loopback:
                     # --- STANDARD MICROPHONE ---
                     print("Recording from Default Microphone")
                     # Use default input device
                     input_rate = 44100
                     channels = 1
                     input_device_index = None # Default

                # Setup Stream
                frames_per_buffer = int(input_rate * self.chunk_duration)

                stream = p.open(format=pyaudio.paInt16,
                                channels=channels,
                                rate=input_rate,
                                input=True,
                                input_device_index=input_device_index,
                                frames_per_buffer=frames_per_buffer)

                while self.is_recording:
                    try:
                        data = stream.read(frames_per_buffer, exception_on_overflow=False)
                        processed_audio = self._process_audio_chunk(data, input_rate, channels)
                        self.audio_queue.put(processed_audio)
                    except Exception as e:
                        print(f"Recording error: {e}")
                        continue

                stream.stop_stream()
                stream.close()
        else:
            # --- TOTAL MOCK (No pyaudio) ---
            print("No audio backend available. Generating silence.")
            while self.is_recording:
                time.sleep(self.chunk_duration)
                fake_audio = np.random.uniform(-0.01, 0.01, int(self.target_sample_rate * self.chunk_duration)).astype(np.float32)
                self.audio_queue.put(fake_audio)

    def start(self):
        if not self.is_recording:
            self.is_recording = True
            self.thread = threading.Thread(target=self._record_loop)
            self.thread.start()

    def stop(self):
        self.is_recording = False
        if self.thread:
            self.thread.join()

    def get_audio(self):
        if not self.audio_queue.empty():
            return self.audio_queue.get()
        return None
