#!/usr/bin/env python3
import speech_recognition as sr
import sys
import pyaudio
from pathlib import Path
import logging
import queue
import threading
import time

# Set up logging to stderr
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

class VoiceRecorder:
    """Records voice input with explicit stop command or long pause."""

    def __init__(self, device_index=None, stop_phrases=None):
        self.device_index = device_index
        self.stop_phrases = stop_phrases or ["stop recording", "end recording", "finish recording"]
        self.recognizer = sr.Recognizer()
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.text_segments = []

    def record_chunk(self, source):
        """Record a chunk of audio and add it to the queue."""
        try:
            while self.is_recording:
                logger.debug("Listening for next chunk...")
                try:
                    # Use a shorter timeout for chunks to allow for stop checking
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=None)
                    self.audio_queue.put(audio)
                except sr.WaitTimeoutError:
                    continue  # Keep listening if timeout
        except Exception as e:
            logger.error(f"Error in recording thread: {e}")
            self.is_recording = False

    def process_audio(self):
        """Process audio chunks from the queue."""
        while self.is_recording or not self.audio_queue.empty():
            try:
                audio = self.audio_queue.get(timeout=1)
                text = self.recognizer.recognize_google(audio)
                logger.debug(f"Recognized: {text}")

                # Check for stop command
                if any(phrase in text.lower() for phrase in self.stop_phrases):
                    logger.debug("Stop command detected")
                    self.is_recording = False
                    break

                self.text_segments.append(text)
            except queue.Empty:
                continue
            except sr.UnknownValueError:
                logger.debug("Could not understand audio chunk")
            except Exception as e:
                logger.error(f"Error processing audio: {e}")

    def record(self):
        """Start recording with microphone."""
        with sr.Microphone(device_index=self.device_index) as source:
            logger.debug("\nAdjusting for ambient noise... Please wait...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)

            logger.debug("\nListening... Say 'stop recording' when finished.")
            self.is_recording = True

            # Start recording thread
            record_thread = threading.Thread(target=self.record_chunk, args=(source,))
            process_thread = threading.Thread(target=self.process_audio)

            record_thread.start()
            process_thread.start()

            try:
                while self.is_recording:
                    time.sleep(0.1)  # Small sleep to prevent CPU hogging
            except KeyboardInterrupt:
                logger.debug("Recording stopped by user")
                self.is_recording = False

            record_thread.join()
            process_thread.join()

            return " ".join(self.text_segments)

def list_audio_devices():
    """List available audio devices to stderr."""
    logger.debug("\nAvailable audio devices:")
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    logger.debug(f"Found {numdevices} audio devices")

    # Look specifically for the webcam mic
    webcam_index = None
    devices = []

    for i in range(numdevices):
        device_info = p.get_device_info_by_index(i)
        if device_info.get('maxInputChannels') > 0:  # If it has input channels
            logger.debug(f"Device {i}: {device_info}")
            if "0x46d:0x825" in device_info.get('name', ''):  # Webcam ID
                webcam_index = i
                logger.debug(f"{i}: {device_info.get('name')} (WEBCAM)")
            devices.append(i)

    p.terminate()
    selected_device = webcam_index if webcam_index is not None else devices[0] if devices else None
    logger.debug(f"Selected device index: {selected_device}")
    return selected_device

def record_voice() -> str:
    """Record voice input and return transcribed text."""
    device_index = list_audio_devices()
    if device_index is None:
        logger.error("No input devices found!")
        sys.exit(1)

    try:
        recorder = VoiceRecorder(device_index=device_index)
        text = recorder.record()
        if text:
            # Don't print here, let main() handle output
            return text
        else:
            logger.error("No text was recorded")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: record_voice.py <note_type>", file=sys.stderr)
        sys.exit(1)

    note_type = sys.argv[1]
    logger.debug(f"Starting recording for note type: {note_type}")
    text = record_voice()
    print(text)  # Output to stdout for piping

if __name__ == "__main__":
    main()
