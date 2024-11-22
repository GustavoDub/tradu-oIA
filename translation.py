import google.generativeai as genai
import speech_recognition as sr
from paddleocr import PaddleOCR, draw_ocr
from googletrans import Translator
from PIL import Image
from langdetect import detect_langs, DetectorFactory
import os
from gtts import gTTS
import cv2
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Configurar para que a detecção de idioma seja consistente
DetectorFactory.seed = 0

# Inicializar PaddleOCR e o tradutor
ocr_paddle = PaddleOCR(use_angle_cls=True, lang='en')
translator = Translator()

# Função para detectar o idioma do texto
def detect_language(text):
    try:
        detected_languages = detect_langs(text)
        return detected_languages[0]
    except Exception as e:
        print(f"Erro na detecção de idioma: {e}")
        return None

# Função para reconhecer fala do microfone
def recognize_speech_from_mic():
    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        r.adjust_for_ambient_noise(source)
        print("Diga algo:")
        audio = r.listen(source)

        try:
            text = r.recognize_google(audio, language='pt-BR')
            print(f"Você disse: {text}")
            return text
        except sr.UnknownValueError:
            print("Não entendi o que você disse.")
            return None
        except sr.RequestError as e:
            print(f"Erro ao solicitar resultados do serviço de reconhecimento de fala; {e}")
            return None

# Função para reconhecer texto a partir de uma imagem usando PaddleOCR
def recognize_text_from_image(image_path):
    try:
        if not os.path.exists(image_path):
            print(f"Arquivo não encontrado: {image_path}")
            return None

        # Reconhecimento com PaddleOCR
        result = ocr_paddle.ocr(image_path, cls=True)
        boxes = []
        txts = []
        scores = []

        # Processar cada linha detectada
        for line in result:
            for res in line:
                box = res[0]
                text_detected = res[1][0]
                score = res[1][1]
                
                # Traduzir o texto detectado para português
                translation = translator.translate(text_detected, src='en', dest='pt').text
                boxes.append(box)
                txts.append(f"{text_detected} (Tradução: {translation})")
                scores.append(score)
                
        # Carregar imagem e desenhar o resultado
        img = cv2.imread(image_path)
        image_with_boxes = draw_ocr(img, boxes, txts, scores, font_path='path/to/arial.ttf')
        output_path = r'C:\Users\Gustavo\Desktop\codigos vs\static\uploads\www_detected_translated.jpg'
        cv2.imwrite(output_path, image_with_boxes)
        print("Imagem com tradução salva em:", output_path)
        Image.open(output_path).show()
        
        return None

    except Exception as e:
        print(f"Erro ao processar a imagem: {e}")
        return None

# Função para traduzir texto entre dois idiomas
def translate_text(text, language_from, language_to):
    genai.configure(api_key="AIzaSyBlGi12cREthT7r0AcAfRt5Tl664Rz7n9U")
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])

    prompt = f"Traduza o seguinte texto do idioma {language_from} para o idioma {language_to}: {text}"
    response = chat.send_message(prompt)
    
    return response.text

# Função para gerar áudio a partir do texto traduzido
def generate_speech(text, language):
    try:
        audio_folder = os.path.join('app', 'static', 'audio_files', 'audio')
        audio_file = os.path.join(audio_folder, 'audio_output.mp3')

        if not os.path.exists(audio_folder):
            os.makedirs(audio_folder)

        tts = gTTS(text=text, lang=language)
        tts.save(audio_file)

        print(f"Áudio gerado e salvo em: {audio_file}")
        return audio_file
    except Exception as e:
        print(f"Erro ao gerar o áudio: {e}")
        return None

# Exemplo de uso para selecionar uma imagem e reconhecer o texto com PaddleOCR
if __name__ == "__main__":
    Tk().withdraw()
    image_path = askopenfilename(title="Selecione uma imagem", filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
    if image_path:
        recognize_text_from_image(image_path)  # Agora sempre usa PaddleOCR
    else:
        print("Nenhuma imagem selecionada.")
