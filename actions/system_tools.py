import os
import subprocess

def open_application(app_name: str) -> str:
    """Abre aplicaciones comunes instaladas en el sistema."""
    app_name_clean = app_name.lower().strip()
    
    apps = {
        "chrome": "chrome.exe",
        "navegador": "chrome.exe",
        "code": "code",
        "visual studio code": "code",
        "vscode": "code",
        "calculadora": "calc.exe",
        "bloc de notas": "notepad.exe",
        "terminal": "wt.exe",
        "cmd": "cmd.exe",
        "explorador": "explorer.exe"
    }

    executable = apps.get(app_name_clean)
    if executable:
        try:
            subprocess.Popen(executable, shell=True)
            return f"Señor, abriendo {app_name}..."
        except Exception as e:
            return f"Error al intentar abrir {app_name}: {str(e)}"
    else:
        try:
            subprocess.Popen(app_name_clean, shell=True)
            return f"Ejecutando {app_name}, señor..."
        except Exception as e:
            return f"No se encontró la aplicación {app_name} en el sistema."