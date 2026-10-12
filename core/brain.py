import os
import webbrowser
import requests
import time
from datetime import datetime
import json
import pyautogui
import pywhatkit

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3

pending_authorization = None
conversation_history = []

def is_waiting_for_authorization() -> bool:
    global pending_authorization
    return pending_authorization is not None

def ask_jarvis(prompt: str) -> str:
    global pending_authorization, conversation_history
    prompt_lower = prompt.lower().strip()
    
    conversation_history.append(f"Usuario: {prompt}")
    if len(conversation_history) > 10:
        conversation_history.pop(0)

    # 1. GESTIÓN DE AUTORIZACIÓN PENDIENTE (WhatsApp)
    if pending_authorization is not None:
        affirmative_words = ["sí", "si", "dale", "hazlo", "mándalo", "mandalo", "autorizo", "envíalo", "envialo", "adelante", "ok", "por favor", "claro", "confirmo", "bueno"]
        negative_words = ["no", "cancela", "cancelar", "detente", "espera", "mejor no"]
        
        if any(w in prompt_lower for w in affirmative_words):
            action = pending_authorization
            pending_authorization = None
            res = execute_pending_action(action)
            conversation_history.append(f"JARVIS: {res}")
            return res
        elif any(w in prompt_lower for w in negative_words):
            pending_authorization = None
            res = "De acuerdo, acción cancelada, señor."
            conversation_history.append(f"JARVIS: {res}")
            return res

    # 2. DETECCIÓN DIRECTA Y RÁPIDA DE WHATSAPP / CORREO
    is_email = any(w in prompt_lower for w in ["correo", "email", "gmail"])
    is_message = any(k in prompt_lower for k in ["whatsapp", "mensaje", "manda", "envía", "escribe", "dile"])
    
    if is_message or is_email:
        if any(p in prompt_lower for p in [" a ", " para ", " a la "]):
            message_text = "Hola, espero que estés bien."
            recipient = ""
            
            temp_prompt = prompt_lower
            for marker in ["que diga", "diciendo", "texto", "con el texto"]:
                if marker in temp_prompt:
                    parts = temp_prompt.split(marker, 1)
                    temp_prompt = parts[0].strip()
                    message_text = parts[1].strip()
                    break
            
            for prep in [" a ", " para "]:
                if prep in temp_prompt:
                    sub_parts = temp_prompt.split(prep)
                    candidate = sub_parts[-1].strip()
                    for cleaner in ["y envíale un correo", "y envíale un mensaje", "y envíale", "y enviale", "y dile", "envíale", "enviale", "manda", "mensaje", "un correo", "correo"]:
                        candidate = candidate.replace(cleaner, "").strip()
                    recipient = candidate
                    break

            for garbage in ["whatsapp", "abre", "contacto", "a"]:
                if recipient.startswith(garbage + " "):
                    recipient = recipient[len(garbage)+1:].strip()

            if recipient and len(recipient) > 1:
                if is_email:
                    pending_authorization = {
                        "type": "email_dynamic",
                        "recipient": recipient,
                        "message": message_text
                    }
                    res = f"Señor, he preparado un correo para '{recipient}' que dice: '{message_text}'. ¿Me autoriza a abrir su cliente de correo?"
                else:
                    pending_authorization = {
                        "type": "whatsapp_dynamic",
                        "recipient": recipient,
                        "message": message_text
                    }
                    res = f"Señor, he preparado un mensaje de WhatsApp para '{recipient}' que dice: '{message_text}'. ¿Me autoriza a enviarlo?"
                
                conversation_history.append(f"JARVIS: {res}")
                return res

    # 3. INTERRUPTOR DIRECTO MULTIMEDIA (Evita fallos de Ollama)
    if any(w in prompt_lower for w in ["reproduce", "reproducir", "canción", "cancion", "musica", "música", "video"]):
        # Limpiamos la frase para quedarnos con lo que hay que buscar
        search_query = prompt_lower
        for cleaner in ["jarvis", "abre chrome", "abre brave", "abre", "chrome", "brave", "reproduce", "reproducir", "la canción", "la cancion", "una canción", "una cancion", "música", "musica", "de"]:
            search_query = search_query.replace(cleaner, "").strip()
        
        if not search_query:
            search_query = prompt
            
        # Ejecución directa e infalible con pywhatkit
        try:
            pywhatkit.playonyt(search_query)
            res = f"Reproduciendo '{search_query}', señor."
            conversation_history.append(f"JARVIS: {res}")
            return res
        except Exception as e:
            print(f"[ERROR PYWHATKIT]: {e}")

    # 4. ANALIZADOR INTELIGENTE CON OLLAMA (Llama 3.2) PARA EL RESTO DE ORDENES
    context_prompt = "\n".join(conversation_history[-6:])
    system_instruction = """
    Eres J.A.R.V.I.S., un asistente operativo de IA en español. Analiza la orden del usuario.
    Devuelve estrictamente un JSON plano con estas claves:
    - "action": "open_app", "search_web", o "chat"
    - "target": aplicación (ej. "brave", "chrome", "spotify") o vacío.
    - "query": término a buscar en la web, o vacío.
    - "reply": tu respuesta educada dirigiéndote al usuario como "señor".
    
    Ejemplo JSON:
    {"action": "search_web", "target": "chrome", "query": "autos mas vendidos 2026", "reply": "Enseguida busco la información en la web, señor."}
    """
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": f"{system_instruction}\n\nHistorial:\n{context_prompt}\nPetición actual: {prompt}\nJSON:",
                "stream": False,
                "format": "json"
            },
            timeout=8
        )
        if response.status_code == 200:
            data = json.loads(response.json().get("response", "{}"))
            action = data.get("action", "chat")
            target = data.get("target", "").strip().lower()
            query = data.get("query", "").strip()
            reply = data.get("reply", "Orden procesada, señor.")
            
            if action == "open_app" and target:
                open_system_app(target)
            elif action == "search_web":
                if target:
                    open_system_app(target)
                    time.sleep(1)
                search_term = query if query else prompt
                pywhatkit.search(search_term)
            
            conversation_history.append(f"JARVIS: {reply}")
            return reply
            
    except Exception as e:
        print(f"[OLLAMA INTENT ERROR]: {e}")

    # Respuestas de respaldo locales
    if "hora" in prompt_lower:
        now = datetime.now().strftime("%H:%M:%S")
        res = f"La hora actual es {now}, señor."
        conversation_history.append(f"JARVIS: {res}")
        return res

    res = "Orden recibida y ejecutada, señor."
    conversation_history.append(f"JARVIS: {res}")
    return res

def execute_pending_action(action: dict) -> str:
    if action["type"] == "whatsapp_dynamic":
        recipient = action["recipient"]
        msg = action["message"]
        try:
            os.startfile("whatsapp://")
            time.sleep(2.2)
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.4)
            pyautogui.write(recipient, interval=0.05)
            time.sleep(1.0)
            pyautogui.press('enter')
            time.sleep(0.5)
            pyautogui.write(msg, interval=0.03)
            time.sleep(0.3)
            pyautogui.press('enter')
            return f"Mensaje enviado a {recipient}, señor."
        except Exception as e:
            return f"Error en WhatsApp, señor: {e}"
            
    elif action["type"] == "email_dynamic":
        recipient = action["recipient"]
        msg = action["message"]
        try:
            import urllib.parse
            subject = urllib.parse.quote("Enviado por J.A.R.V.I.S.")
            body = urllib.parse.quote(msg)
            os.system(f'start "" "mailto:{recipient}?subject={subject}&body={body}"')
            return f"He abierto su cliente de correo con el mensaje para {recipient}, señor."
        except Exception as e:
            return f"Error al intentar abrir el correo, señor: {e}"
            
    return "Acción ejecutada, señor."

def open_system_app(app_name: str) -> str:
    app_name = app_name.strip().lower()
    system_tools = {
        "administrador de tareas": "taskmgr",
        "explorador de archivos": "explorer",
        "bloc de notas": "notepad",
        "calculadora": "calc",
        "whatsapp": "whatsapp://",
        "steam": "steam://",
        "spotify": "spotify:"
    }
    if app_name in system_tools:
        cmd = system_tools[app_name]
        try:
            if cmd.endswith("://") or cmd.endswith(":"):
                os.startfile(cmd)
            else:
                os.system(f"start {cmd}")
            return f"Abriendo {app_name}, señor."
        except Exception:
            pass

    try:
        ret = os.system(f'start "" "{app_name}"')
        if ret == 0:
            return f"Aplicación {app_name} iniciada, señor."
    except Exception:
        pass

    start_menu_paths = [
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%AppData%\Microsoft\Windows\Start Menu\Programs")
    ]
    
    found_lnk = None
    for path in start_menu_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".lnk") and app_name in file.lower():
                    found_lnk = os.path.join(root, file)
                    break
            if found_lnk:
                break
        if found_lnk:
            break
            
    if found_lnk:
        try:
            os.startfile(found_lnk)
            return f"Abriendo {app_name}, señor."
        except Exception:
            pass

    return f"Aplicación {app_name} iniciada, señor."