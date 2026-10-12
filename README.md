# 🤖 J.A.R.V.I.S. - Asistente Personal de Escritorio Local

J.A.R.V.I.S. es un asistente virtual operativo de escritorio desarrollado en Python, diseñado para ejecutarse localmente con total privacidad y velocidad. Cuenta con una interfaz gráfica flotante moderna, procesamiento de lenguaje natural mediante **Llama 3.2 (Ollama)**, control por voz avanzado y automatización de tareas en Windows.

## Características Principales

- **Interfaz Gráfica Local:** Ventana flotante interactiva construida con HTML/JS y backend en Python (`desktop_widget.py`).
- **Inteligencia Local (NLP):** Procesamiento de intenciones ultrarrápido y privado mediante **Llama 3.2** a través de Ollama.
- **Reconocimiento de Voz Robusto:** Sistema de escucha continua con matriz de alias fonéticos para evitar falsos positivos.
- **Automatización de Mensajería:** Capacidad de abrir WhatsApp, buscar contactos, redactar mensajes y solicitar autorización de seguridad antes de enviar.
- **Multimedia y Web:** Búsquedas web directas y reproducción automática de música y vídeos en YouTube sin errores de enfoque.

## Estructura del Proyecto

jarvis_assistant/
├── actions/ (Acciones y herramientas del sistema)
├── assets/ (Recursos visuales y multimedia)
├── core/ (Núcleo de inteligencia con brain.py y voice.py)
├── logs/ (Registros de actividad del sistema)
├── ui/ (Interfaz gráfica HTML/CSS/JS)
├── desktop_widget.py (Lanzador de ventana flotante)
├── main.py (Script principal de inicio)
└── requirements.txt (Dependencias del proyecto)

## Requisitos e Instalación

Para poner en marcha el proyecto en tu entorno local, abre tu terminal en la raíz de la carpeta y ejecuta los siguientes comandos de forma secuencial:

1. Clona el repositorio y accede al directorio: `git clone https://github.com/Byron06010/Jarvis-assistant.git` y luego `cd jarvis_assistant`.
2. Crea y activa tu entorno virtual de Python: `python -m venv venv` y `venv\Scripts\activate`.
3. Instala las dependencias requeridas: `pip install -r requirements.txt`.
4. Asegúrate de tener Ollama activo localmente y el modelo descargado: `ollama run llama3.2`.
5. Ejecuta el asistente: `python main.py`.

---
Desarrollado con 💻 por **Byron Alejandro Leiva Garcés**.
