import sys
import os
import threading
import time
import json
import requests
import pythoncom
import speech_recognition as sr
import win32com.client
from datetime import datetime
from core.brain import ask_jarvis, is_waiting_for_authorization

jarvis_status = "INACTIVO"
voice_activity_logs = []

def add_log(sender: str, text: str):
    global voice_activity_logs
    voice_activity_logs.append({"sender": sender, "text": text})
    if len(voice_activity_logs) > 20:
        voice_activity_logs.pop(0)

def get_latest_voice_logs():
    global voice_activity_logs
    logs = voice_activity_logs.copy()
    voice_activity_logs.clear()
    return logs

def speak(text: str):
    global jarvis_status
    pythoncom.CoInitialize()
    
    jarvis_status = "HABLANDO"
    print(f"JARVIS: {text}")
    add_log("jarvis", text)
    
    try:
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        voices = speaker.GetVoices()
        
        selected_voice = None
        for voice in voices:
            desc = voice.GetDescription().lower()
            if "pablo" in desc or "raul" in desc or "david" in desc:
                selected_voice = voice
                break
                
        if selected_voice:
            speaker.Voice = selected_voice
        elif len(voices) > 0:
            speaker.Voice = voices[0]

        speaker.Rate = 1
        speaker.Speak(text)
        
    except Exception as e:
        print(f"[ERROR TTS]: {e}")
    finally:
        jarvis_status = "INACTIVO"
        pythoncom.CoUninitialize()

def process_command_text(command: str) -> str:
    global jarvis_status
    if not command:
        return ""
    
    jarvis_status = "PENSANDO"
    print(f"Tú: {command}")
    add_log("user", command)
    
    response = ask_jarvis(command)
    speak(response)
    return response

def listen_and_execute_direct():
    global jarvis_status
    pythoncom.CoInitialize()
    recognizer = sr.Recognizer()
    
    recognizer.pause_threshold = 2.0
    recognizer.non_speaking_duration = 0.5
    
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            jarvis_status = "ESCUCHANDO"
            
            if is_waiting_for_authorization():
                print("\n[ESPERANDO AUTORIZACIÓN] Diga 'Sí' o 'Cancelar'...")
            else:
                print("\n[OÍDOS ACTIVOS] Diga 'Jarvis' seguido de su orden...")
            
            try:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=20)
                jarvis_status = "PROCESANDO"
                
                text = recognizer.recognize_google(audio, language="es-ES").lower()
                print(f"Capturado: {text}")
                
                if is_waiting_for_authorization():
                    process_command_text(text)
                elif "jarvis" in text:
                    command = text.replace("jarvis", "").strip()
                    if command:
                        process_command_text(command)
                    else:
                        speak("Sí, señor, ¿qué orden me da?")
                        audio_sub = recognizer.listen(source, timeout=5, phrase_time_limit=15)
                        sub_text = recognizer.recognize_google(audio_sub, language="es-ES")
                        process_command_text(sub_text)
                else:
                    jarvis_status = "INACTIVO"
                        
            except sr.WaitTimeoutError:
                jarvis_status = "INACTIVO"
            except sr.UnknownValueError:
                jarvis_status = "INACTIVO"
            except Exception as e:
                jarvis_status = "INACTIVO"
    finally:
        pythoncom.CoUninitialize()

def background_listener():
    print("[SISTEMA DE VOZ] Bucle con memoria y atención directa iniciado, señor.")
    while True:
        try:
            listen_and_execute_direct()
        except Exception as e:
            print(f"[ERROR BUCLE VOZ]: {e}")
            time.sleep(1)

def start_voice_thread():
    t = threading.Thread(target=background_listener, daemon=True)
    t.start()