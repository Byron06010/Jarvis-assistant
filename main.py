import sys
import os
import time
import threading
import webview
from datetime import datetime
from core.voice import start_voice_thread, jarvis_status, speak
from core.brain import ask_jarvis

# Servidor Flask opcional o API local si lo requiere la UI
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class JarvisAPIHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            prompt = data.get('prompt', '')
            
            response_text = ask_jarvis(prompt)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"response": response_text}).encode('utf-8'))

    def do_GET(self):
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": jarvis_status}).encode('utf-8'))

def run_server():
    server = HTTPServer(('127.0.0.1', 8000), JarvisAPIHandler)
    server.serve_forever()

def initial_greeting():
    time.sleep(2.0)
    now = datetime.now()
    hora = now.hour
    minutos = now.strftime("%M")
    
    if 5 <= hora < 12:
        momento = f"las {hora} y {minutos} de la mañana"
    elif 12 <= hora < 19:
        hora_12 = hora if hora <= 12 else hora - 12
        momento = f"las {hora_12} y {minutos} de la tarde"
    else:
        hora_12 = hora if hora <= 12 else hora - 12
        momento = f"las {hora_12} y {minutos} de la noche"
    
    # Saludo de alta información y motivación
    saludo_inicial = f"Hola señor, son {momento}. Espero que tengas un excelente día. Los sistemas de J.A.R.V.I.S. están operando al ciento por ciento y listos para tus órdenes."
    speak(saludo_inicial)

def main():
    print("[JARVIS OS] Iniciando secuencia de arranque general, señor...")
    
    # Iniciar servidor local para la UI en un hilo separado
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Iniciar saludo inicial en segundo plano
    greeting_thread = threading.Thread(target=initial_greeting, daemon=True)
    greeting_thread.start()
    
    # Iniciar bucle de escucha de voz
    start_voice_thread()
    
    # Cargar interfaz web en una ventana amplia de 1280x720
    html_path = os.path.abspath("ui/index.html")
    print(f"[HUD] Desplegando interfaz visual amplia desde: {html_path}")
    
    window = webview.create_window(
        "J.A.R.V.I.S. // BYRON OS",
        f"file:///{html_path}",
        width=1280,
        height=720,
        frameless=False,
        transparent=False,
        on_top=False,
        resizable=True
    )
    
    webview.start()

if __name__ == "__main__":
    main()