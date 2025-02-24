#!/usr/bin/env python3
import speech_recognition as sr
import sys
import pyaudio
from pathlib import Path
import logging

# Set up logging to stderr
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

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
    r = sr.Recognizer()
    logger.debug("Initializing recognizer")

    device_index = list_audio_devices()
    if device_index is None:
        logger.error("No input devices found!")
        sys.exit(1)

    try:
        logger.debug(f"Attempting to use microphone with device index {device_index}")
        with sr.Microphone(device_index=device_index) as source:
            logger.debug("\nAdjusting for ambient noise... Please wait...")
            r.adjust_for_ambient_noise(source, duration=2)

            logger.debug("\nListening... Press Ctrl+C to stop recording.")
            try:
                audio = r.listen(source, timeout=None, phrase_time_limit=5)
                logger.debug("Processing...")

                text = r.recognize_google(audio)
                logger.debug(f"Got recognition result: {text}")
                # Only output the recognized text to stdout
                print(text)
                return text

            except sr.WaitTimeoutError:
                logger.error("No speech detected")
                sys.exit(1)

    except OSError as e:
        logger.error(f"Error accessing microphone: {e}")
        sys.exit(1)
    except sr.UnknownValueError:
        logger.error("Could not understand audio")
        sys.exit(1)
    except sr.RequestError as e:
        logger.error(f"Could not request results: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Recording stopped by user")
        sys.exit(0)
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