import re
import pyttsx3
import threading
import queue
import pyaudio
import json
import time
from vosk import Model, KaldiRecognizer

# Diccionario básico para palabras individuales (como respaldo)
NUMBERS_DICT = {
    "uno": "1", "dos": "2", "tres": "3", "cuatro": "4", "cinco": "5",
    "seis": "6", "siete": "7", "ocho": "8", "nueve": "9", "diez": "10",
    "once": "11", "doce": "12", "trece": "13", "catorce": "14", "quince": "15",
    "dieciséis": "16", "diecisiete": "17", "dieciocho": "18", "diecinueve": "19",
    "veinte": "20", "treinta": "30", "cuarenta": "40", "cincuenta": "50",
    "sesenta": "60", "setenta": "70", "ochenta": "80", "noventa": "90",
}

def spanish_text_to_int(text):
    text = text.strip().lower()
    base_numbers = {
        "cero": 0,
        "uno": 1, "una": 1,
        "dos": 2,
        "tres": 3,
        "cuatro": 4,
        "cinco": 5,
        "seis": 6,
        "siete": 7,
        "ocho": 8,
        "nueve": 9,
        "diez": 10,
        "once": 11,
        "doce": 12,
        "trece": 13,
        "catorce": 14,
        "quince": 15,
        "dieciséis": 16, "dieciseis": 16,
        "diecisiete": 17,
        "dieciocho": 18,
        "diecinueve": 19,
        "veinte": 20,
        "veintiuno": 21, "veintidós": 22, "veintidos": 22,
        "veintitrés": 23, "veintitres": 23,
        "veinticuatro": 24,
        "veinticinco": 25,
        "veintiséis": 26, "veintiseis": 26,
        "veintisiete": 27,
        "veintiocho": 28,
        "veintinueve": 29,
        "treinta": 30,
        "cuarenta": 40,
        "cincuenta": 50,
        "sesenta": 60,
        "setenta": 70,
        "ochenta": 80,
        "noventa": 90,
    }
    if text in base_numbers:
        return base_numbers[text]
    if " y " in text:
        parts = text.split(" y ")
        if len(parts) == 2:
            tens = base_numbers.get(parts[0].strip(), None)
            ones = base_numbers.get(parts[1].strip(), None)
            if tens is not None and ones is not None:
                return tens + ones
    for word in text.split():
        if word.isdigit():
            return int(word)
    return None


def convert_text_to_number(text):
    """
    Intenta convertir la respuesta reconocida a un número. Si no lo reconoce usa el diccionario
    """
    num = spanish_text_to_int(text)
    if num is not None:
        return str(num)
    words = text.split()
    numbers = [NUMBERS_DICT.get(word, "") for word in words if word in NUMBERS_DICT]
    return "".join(numbers) if any(numbers) else text


def preprocess_text(text):
    """
    Preprocesa el texto antes de enviarlo a reproducir la voz
    """
    text = re.sub(r'(\d)\s*x\s*(\d)', r'\1 por \2', text)
    return text

try:
    model = Model("model")
except Exception as e:
    print("No se pudo cargar el modelo Vosk. Asegúrate de tener el directorio 'model' con el modelo descargado.")
    model = None


def has_microphone():
    p = pyaudio.PyAudio()
    mic_count = 0
    for i in range(p.get_device_count()):
        device = p.get_device_info_by_index(i)
        if device.get('maxInputChannels') > 0:
            mic_count += 1
    p.terminate()
    return mic_count > 0


def list_microphones():
    p = pyaudio.PyAudio()
    devices = []
    for i in range(p.get_device_count()):
        device = p.get_device_info_by_index(i)
        if device.get('maxInputChannels') > 0:
            devices.append(device.get('name'))
    p.terminate()
    return devices


def listen_for_answer(timeout=3):
    """
    Escucha la respuesta del usuario usando Vosk de forma offline.
    """
    if model is None:
        return ""
    rec = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                        input=True, frames_per_buffer=8000)
    except Exception as e:
        print("Error al abrir el stream de audio:", e)
        p.terminate()
        return ""
    stream.start_stream()
    start_time = time.time()
    result_text = ""
    try:
        while True:
            if time.time() - start_time > timeout:
                break
            data = stream.read(4000, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                result_text = res.get("text", "")
                break
    except Exception as e:
        print("Error durante la grabación:", e)
    stream.stop_stream()
    stream.close()
    p.terminate()
    if result_text == "":
        res = json.loads(rec.FinalResult())
        result_text = res.get("text", "")
    return convert_text_to_number(result_text.lower())

# Cola para las solicitudes de voz
speech_queue = queue.Queue()

def speech_worker():
    """
    Se encarga de procesar las solicitudes de voz de forma secuencial.
    """
    engine = pyttsx3.init()
    while True:
        try:
            item = speech_queue.get()
            if item is None:
                break
            text, voice_type = item
            text = preprocess_text(text)
            voices = engine.getProperty('voices')
            rate = 150
            volume = 1.0
            selected_voice = None

            if voice_type == "happy":
                rate = 180
                if len(voices) > 1:
                    selected_voice = voices[1].id
            elif voice_type == "character":
                rate = 140
                if len(voices) > 0:
                    selected_voice = voices[0].id

            engine.setProperty('rate', rate)
            engine.setProperty('volume', volume)
            if selected_voice is not None:
                engine.setProperty('voice', selected_voice)
            else:
                engine.setProperty('voice', voices[0].id)

            print("Hablando:", text)
            engine.say(text)
            engine.runAndWait()
            speech_queue.task_done()
        except Exception as e:
            print("Error en speech_worker:", e)


worker_thread = threading.Thread(target=speech_worker, daemon=True)
worker_thread.start()

def speak_text(text, voice_type="default"):
    speech_queue.put((text, voice_type))

def speak_correct():
    speak_text("Respuesta correcta, ¡bien hecho!", voice_type="happy")


def speak_incorrect(answer):
    """Mensaje con entonación para respuesta incorrecta."""
    speak_text(f"Respuesta incorrecta, la respuesta es {answer}.", voice_type="character")
