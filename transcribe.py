import numpy as np
import datetime
import pyaudio
import re
import os
import ctypes
import psutil
import GPUtil
from fuzzywuzzy import fuzz
import threading
import time
from pystyle import Center, Colors, Colorate
from faster_whisper import WhisperModel

# Ustawienie wysokiego priorytetu dla procesu
psutil.Process(os.getpid()).nice(psutil.HIGH_PRIORITY_CLASS)

# Konfiguracja parametrów nagrywania i transkrypcji
CONFIG = {
    "CHUNK_SIZE": 2048,
    "FORMAT": pyaudio.paInt16,
    "CHANNELS": 1,
    "RATE": 20000,
    "RECORD_SECONDS": 12,
    "MICROPHONE_NAME": "Microphone (SM950 Microphone )",
    "THRESHOLD_DB": 73,
    "IGNORE_PHRASES_FILE": "ignore_phrases.txt",
    "TRANSCRIPTIONS_FILE": "transcriptions.txt",
    "MODEL_SIZE": "large-v3",
    "DEVICE": "cuda",
    "COMPUTE_TYPE": "float16",
    "TITLE_UPDATE_INTERVAL": 0.1,
    "LOGO_TEXT": """
        ███████╗██╗     ██╗   ██╗███████╗██╗██╗   ██╗███████╗
        ██╔════╝██║     ██║   ██║██╔════╝██║██║   ██║██╔════╝
        █████╗  ██║     ██║   ██║███████╗██║██║   ██║█████╗  
        ██╔══╝  ██║     ██║   ██║╚════██║██║╚██╗ ██╔╝██╔══╝  
        ███████╗███████╗╚██████╔╝███████║██║ ╚████╔╝ ███████╗
        ╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝  ╚══════╝
                        Discord: elusive1337
    """
}

# Lista kolorów do wyświetlania tekstu
color_list = [
    Colors.orange,
    Colors.purple,
    Colors.cyan,
    Colors.green,
    Colors.gray
]

def initialize_model():
    """Inicjalizuje model Whisper."""
    return WhisperModel(
        CONFIG["MODEL_SIZE"],
        device=CONFIG["DEVICE"],
        compute_type=CONFIG["COMPUTE_TYPE"]
    )

def display_logo():
    """Wyświetla logotyp w konsoli."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Colorate.Horizontal(Colors.rainbow, Center.XCenter(CONFIG["LOGO_TEXT"])))
    print(Colorate.Horizontal(Colors.rainbow, "~ T R A N S K R Y P C J A ~\nZacznij rozmawiać :)\n\n"))

def change_console_title(title):
    """Zmienia tytuł okna konsoli."""
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def get_system_usage():
    """Pobiera aktualne użycie zasobów systemowych."""
    process = psutil.Process(os.getpid())
    ram_usage = process.memory_percent()

    try:
        gpus = GPUtil.getGPUs()
        gpu_usage = gpus[0].memoryUtil * 100 if gpus else 0.0
    except Exception:
        gpu_usage = 0.0

    return gpu_usage, ram_usage

def update_console_title(start_time, chunk_number):
    """Aktualizuje tytuł okna konsoli w regularnych odstępach czasu."""
    while True:
        elapsed_time = datetime.datetime.now() - start_time
        gpu_usage, ram_usage = get_system_usage()
        title = (
            f"[# {chunk_number}] ElusiveSTT v1.5 | "
            f"Czas: {str(elapsed_time).split('.')[0]} | "
            f"GPU: {gpu_usage:.1f}% | RAM: {ram_usage:.1f}%"
        )
        change_console_title(title)
        time.sleep(CONFIG["TITLE_UPDATE_INTERVAL"])

def load_ignore_phrases():
    """Wczytuje frazy do ignorowania z pliku tekstowego lub tworzy nowy plik z domyślnymi frazami."""
    if not os.path.exists(CONFIG["IGNORE_PHRASES_FILE"]):
        default_phrases = ["przykładowa fraza do ignorowania"]
        with open(CONFIG["IGNORE_PHRASES_FILE"], "w", encoding="utf-8") as file:
            for phrase in default_phrases:
                file.write(f"{phrase}\n")
        return [phrase.lower() for phrase in default_phrases]
    else:
        with open(CONFIG["IGNORE_PHRASES_FILE"], "r", encoding="utf-8") as file:
            return [line.strip().lower() for line in file.readlines()]

def is_phrase_ignored(text, ignore_phrases):
    """Sprawdza, czy przetranskrybowany tekst powinien być ignorowany."""
    normalized_text = re.sub(r'[^\w\s]', '', text.lower())
    for phrase in ignore_phrases:
        similarity = fuzz.ratio(normalized_text, phrase)
        if similarity > 90:
            return True
    return False

def rms_level(data):
    """Oblicza RMS sygnału audio."""
    audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32)
    rms = np.sqrt(np.mean(np.square(audio_array)))
    return 20 * np.log10(rms) if rms > 0 else -np.inf

def transcribe_audio(model, audio_data):
    """Transkrybuje dane audio na tekst przy użyciu modelu Whisper i łączy segmenty."""
    audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
    segments, _ = model.transcribe(
        audio_array,
        beam_size=5,
        language="pl",
        task="transcribe"
    )

    # Łączenie wszystkich segmentów w jeden spójny tekst
    combined_text = " ".join([segment.text.strip() for segment in segments])
    return combined_text

def save_transcription(text):
    """Zapisuje transkrypcję do pliku."""
    with open(CONFIG["TRANSCRIPTIONS_FILE"], "a", encoding="utf-8") as file:
        file.write(f"{text}\n")

def find_microphone(p):
    """Znajduje indeks wybranego mikrofonu."""
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if CONFIG["MICROPHONE_NAME"] in device_info.get('name'):
            return i
    return None

def record_and_transcribe():
    """Główna funkcja nagrywania i transkrypcji audio."""
    p = pyaudio.PyAudio()
    device_index = find_microphone(p)

    if device_index is None:
        print(f"Nie znaleziono mikrofonu '{CONFIG['MICROPHONE_NAME']}'.")
        return

    stream = p.open(
        format=CONFIG["FORMAT"],
        channels=CONFIG["CHANNELS"],
        rate=CONFIG["RATE"],
        input=True,
        frames_per_buffer=CONFIG["CHUNK_SIZE"],
        input_device_index=device_index
    )

    model = initialize_model()
    ignore_phrases = load_ignore_phrases()
    display_logo()

    start_time = datetime.datetime.now()
    chunk_number = 0

    threading.Thread(
        target=update_console_title,
        args=(start_time, chunk_number),
        daemon=True
    ).start()

    try:
        while True:
            chunk_number += 1
            frames = []
            recording = False
            print(Colorate.Horizontal(Colors.blue_to_purple, '<<<OCZEKIWANIE NA DŹWIĘK>>>'))

            while not recording:
                data = stream.read(CONFIG["CHUNK_SIZE"], exception_on_overflow=False)
                if rms_level(data) > CONFIG["THRESHOLD_DB"]:
                    recording = True
                    frames.append(data)
                    print(Colorate.Horizontal(Colors.red_to_blue, '<<<NAGRYWANIE ROZPOCZĘTE>>>'))

            try:
                for _ in range(0, int(CONFIG["RATE"] / CONFIG["CHUNK_SIZE"] * CONFIG["RECORD_SECONDS"])):
                    data = stream.read(CONFIG["CHUNK_SIZE"], exception_on_overflow=False)
                    frames.append(data)
            except OSError as e:
                print(f"Audio stream error: {e}")
                break

            audio_data = b''.join(frames)
            combined_text = transcribe_audio(model, audio_data)

            if combined_text:
                if not is_phrase_ignored(combined_text, ignore_phrases):
                    current_time = datetime.datetime.now()
                    elapsed_seconds = (current_time - start_time).total_seconds()
                    color = color_list[chunk_number % len(color_list)]  # Wybieranie koloru na podstawie chunk_number

                    formatted_text = (
                        f"{Colors.yellow}[#{chunk_number} "
                        f"{Colors.green}{current_time.strftime('%H:%M:%S')}{Colors.yellow}, "
                        f"{Colors.cyan}{elapsed_seconds:.2f}s{Colors.yellow}] "
                        f"{color}{combined_text}{Colors.reset}"
                    )
                    print(formatted_text)
                    save_transcription(combined_text)

    except KeyboardInterrupt:
        print("Nagrywanie zakończone przez użytkownika.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    record_and_transcribe()