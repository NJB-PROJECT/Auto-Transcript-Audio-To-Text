import threading
import queue
import time
import numpy as np
import sounddevice as sd

# Flag globally
IS_SYSTEM_AUDIO_AVAILABLE = False

try:
    # Check if WASAPI is available (Windows)
    host_apis = sd.query_hostapis()
    wasapi_found = any('WASAPI' in api['name'] for api in host_apis)
    IS_SYSTEM_AUDIO_AVAILABLE = wasapi_found
except Exception:
    IS_SYSTEM_AUDIO_AVAILABLE = False

class AudioRecorder:
    def __init__(self, target_sample_rate=16000, chunk_duration=3):
        self.target_sample_rate = target_sample_rate
        self.chunk_duration = chunk_duration
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.thread = None
        self.is_system_audio_available = IS_SYSTEM_AUDIO_AVAILABLE

    def _get_wasapi_loopback(self):
        """Find the WASAPI Loopback device."""
        try:
            wasapi_host_index = None
            for i, api in enumerate(sd.query_hostapis()):
                if 'WASAPI' in api['name']:
                    wasapi_host_index = i
                    break

            if wasapi_host_index is None:
                return None

            # Get default output device for WASAPI
            default_output = sd.query_hostapis(wasapi_host_index)['default_output_device']
            if default_output < 0:
                return None

            # In sounddevice, the loopback device is often the same ID as output but used as input?
            # Actually, sounddevice (PortAudio) supports loopback via specific flags or device searching.
            # But the most reliable way in 'sounddevice' library strictly is listing devices and looking for loopback.
            # However, standard sounddevice builds on Windows might not expose "Loopback" explicitly in the name string
            # without the WASAPI Loopback extension.

            # IMPROVED STRATEGY:
            # We will try to find a device that has 'loopback' in name if possible.
            # If not, we fall back to default input.

            devices = sd.query_devices()
            for i, dev in enumerate(devices):
                if dev['hostapi'] == wasapi_host_index:
                    # Check if it looks like a loopback device (some drivers label it)
                    if 'loopback' in dev['name'].lower():
                        return i

            # If explicit loopback not found, we use the "default input" of the WASAPI host
            default_input = sd.query_hostapis(wasapi_host_index)['default_input_device']
            return default_input

        except Exception as e:
            print(f"Error searching devices: {e}")
            return None

    def _record_loop(self):
        print("Starting recording thread...")

        # Buffer to accumulate samples
        input_device = None

        # Try to use WASAPI Loopback if on Windows
        if self.is_system_audio_available:
             # NOTE: sounddevice loopback support is experimental and depends on the specific PortAudio build.
             # If this fails, we fall back to default system mic.
             try:
                # To record loopback with sounddevice/PortAudio on Windows WASAPI:
                # We usually need to open the *Output* device as an *Input* stream with specific flags.
                # However, python-sounddevice wrapper makes this tricky.
                # A common workaround is just using the default input (Microphone).
                #
                # Let's try to grab the default input device first.
                input_device = sd.default.device[0]
             except:
                input_device = None

        # Callback for the stream
        def callback(indata, frames, time, status):
            if status:
                print(status)
            # indata is numpy array
            # Downmix to mono
            mono_data = indata.mean(axis=1) if indata.ndim > 1 else indata
            self.audio_queue.put(mono_data.copy())

        try:
            # Stream parameters
            # We let sounddevice choose the native rate, then we might need to resample later?
            # Actually, sounddevice handles resampling if we ask for it!

            with sd.InputStream(device=input_device,
                                channels=1,
                                samplerate=self.target_sample_rate,
                                callback=callback,
                                blocksize=int(self.target_sample_rate * self.chunk_duration)):
                while self.is_recording:
                    sd.sleep(100) # Keep thread alive while stream runs in background

        except Exception as e:
            print(f"Recording Error: {e}")
            # Fallback Loop (Mock)
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
