import webview
import os

def main():
    html_path = os.path.abspath("ui/index.html")
    
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