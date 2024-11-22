import cv2
import pytesseract
import numpy as np
from deep_translator import GoogleTranslator
import tkinter as tk
from tkinter import ttk

# Configuração do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Função para listar câmeras
def list_cameras():
    max_index = 10
    available_cameras = []
    for i in range(max_index):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
    return available_cameras

# Função para solicitar a língua de destino
def get_target_language():
    root = tk.Tk()
    root.title("Selecionar Língua de Destino")
    root.attributes("-topmost", True)  # Mantém a janela no topo
    root.resizable(False, False)  # Desabilita os botões de minimizar e maximizar

    label = tk.Label(root, text="Selecione a língua de destino:")
    label.pack(pady=10)

    languages = [
        "Inglês (en)", "Espanhol (es)", "Francês (fr)", "Alemão (de)",
        "Italiano (it)", "Português (pt)", "Russo (ru)", "Chinês (zh)",
        "Japonês (ja)", "Coreano (ko)"
    ]

    language_var = tk.StringVar()
    language_var.set(languages[0])  # Definir o valor padrão

    language_menu = ttk.Combobox(root, textvariable=language_var, values=languages)
    language_menu.pack(pady=10)

    def on_select():
        selected_language = language_var.get().split(" ")[1].strip("()")
        root.destroy()
        return selected_language

    select_button = tk.Button(root, text="Selecionar", command=on_select)
    select_button.pack(pady=10)

    root.mainloop()

    return language_var.get().split(" ")[1].strip("()")

# Verificar se há câmeras disponíveis
available_cameras = list_cameras()
if not available_cameras:
    print("Nenhuma câmera encontrada.")
    exit()

# Solicitar ao usuário a língua de destino
target_language = get_target_language()
if not target_language:
    print("Língua de destino não especificada. Encerrando o programa.")
    exit()

# Inicializar a primeira câmera
cap = cv2.VideoCapture(available_cameras[0], cv2.CAP_DSHOW)
if not cap.isOpened():
    print("Erro: Não foi possível abrir a câmera.")
    exit()

cap.set(3, 640)  # Largura
cap.set(4, 480)  # Altura

# Inicializar o tradutor
translator = GoogleTranslator(source='auto', target=target_language)

text_recognized = False

while not text_recognized:
    ret, frame = cap.read()
    if not ret:
        print("Falha ao capturar o quadro.")
        break

    try:
        # Reconhecer texto na imagem
        recognized_text = pytesseract.image_to_string(frame)

        # Verifica se o texto reconhecido não está vazio
        if recognized_text.strip():
            # Traduzir o texto reconhecido
            translated_text = translator.translate(recognized_text)
            display_text = f"Original: {recognized_text.strip()}"
            display_translated_text = f"Traduzido: {translated_text}"
            text_recognized = True  # Sinaliza que o texto foi reconhecido
        else:
            display_text = "Nenhum texto reconhecido."
            display_translated_text = ""

        # Exibir o texto reconhecido e traduzido no vídeo
        cv2.putText(frame, display_text, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, display_translated_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.imshow("Detecção e Tradução de Texto em Tempo Real", frame)
    except Exception as e:
        print(f"Erro ao processar o quadro: {e}")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
