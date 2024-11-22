from flask import Blueprint, render_template, request, jsonify, Response
from .translation import translate_text, recognize_speech_from_mic, recognize_text_from_image, detect_language, generate_speech
from werkzeug.utils import secure_filename
import os
import cv2  # Import da OpenCV para manipular a câmera
import subprocess  # Import do módulo subprocess
import base64
import numpy as np
import pytesseract
from deep_translator import GoogleTranslator

main = Blueprint('main', __name__)

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    return render_template('index.html')

# Função para capturar o feed da câmera
def generate_camera_feed():
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # 0 indica a câmera padrão, CAP_DSHOW para compatibilidade
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Rota para acessar o feed da câmera
@main.route('/video_feed')
def video_feed():
    return Response(generate_camera_feed(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@main.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()

    if not data or 'text' not in data or 'language_to' not in data:
        return jsonify({'error': 'Dados de entrada inválidos.'}), 400

    text = data['text']
    language_to = data['language_to']

    detected_language = detect_language(text)
    if detected_language:
        language_from = detected_language.lang
        translation = translate_text(text, language_from, language_to)

        if translation:
            return jsonify({'translation': translation}), 200
        else:
            return jsonify({'error': 'Falha na tradução.'}), 500
    else:
        return jsonify({'error': 'Não foi possível detectar o idioma.'}), 400

@main.route('/recognize-speech', methods=['POST'])
def recognize_speech():
    language_to = request.json.get('language_to')
    if not language_to:
        return jsonify({'error': 'O idioma de saída é necessário.'}), 400

    text = recognize_speech_from_mic()
    if text:
        detected_language = detect_language(text)
        if detected_language:
            language_from = detected_language.lang
            translation = translate_text(text, language_from, language_to)
            audio_url = generate_speech(translation, language_to)

            return jsonify({'translation': translation, 'audio_url': audio_url}), 200
        else:
            return jsonify({'error': 'Não foi possível detectar o idioma.'}), 400
    return jsonify({'error': 'Falha ao reconhecer a fala.'}), 500

@main.route('/recognize-image-text', methods=['POST'])
def recognize_image_text():
    if 'image' not in request.files:
        return jsonify({'error': 'Nenhuma imagem enviada.'}), 400

    language_to = request.form.get('language_to')
    if not language_to:
        return jsonify({'error': 'Idioma de saída (language_to) não foi enviado.'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado.'}), 400

    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        image.save(filepath)

        try:
            text = recognize_text_from_image(filepath)
            os.remove(filepath)

            if not text:
                return jsonify({'error': 'Nenhum texto reconhecido na imagem.'}), 500

            detected_language = detect_language(text)
            if detected_language:
                language_from = detected_language.lang
                translation = translate_text(text, language_from, language_to)

                if translation:
                    return jsonify({'text': text, 'translation': translation}), 200
                else:
                    return jsonify({'error': 'Falha na tradução do texto reconhecido.'}), 500
            else:
                return jsonify({'error': 'Não foi possível detectar o idioma do texto reconhecido.'}), 400

        except Exception as e:
            print(f"Erro ao processar OCR: {e}")
            return jsonify({'error': 'Erro no processamento do OCR.'}), 500
    else:
        return jsonify({'error': 'Arquivo inválido. Apenas imagens .png, .jpg e .jpeg são permitidas.'}), 400

# Rota para iniciar a câmera e executar o script Python para OCR
@main.route('/start-camera', methods=['POST'])
def start_camera():
    try:
        # Capturar a imagem da câmera
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return jsonify({'error': 'Falha ao capturar a imagem da câmera.'}), 500

        # Salvar a imagem capturada
        image_path = os.path.join(UPLOAD_FOLDER, 'captured_image.jpg')
        cv2.imwrite(image_path, frame)

        # Reconhecer texto na imagem
        recognized_text = pytesseract.image_to_string(frame)

        # Traduzir o texto reconhecido
        target_language = request.form.get('language_to')
        translator = GoogleTranslator(source='auto', target=target_language)
        translated_text = translator.translate(recognized_text)

        # Desenhar bounding boxes na imagem
        d = pytesseract.image_to_data(frame, output_type=pytesseract.Output.DICT)
        n_boxes = len(d['text'])
        for i in range(n_boxes):
            if int(d['conf'][i]) > 0:
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Converter a imagem com bounding boxes para base64
        ret, buffer = cv2.imencode('.jpg', frame)
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'image': image_base64,
            'original_text': recognized_text,
            'translated_text': translated_text
        }), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao iniciar a câmera OCR: {str(e)}'}), 500

# Rota para executar o script word_detection.py
@main.route('/start-image-detection', methods=['POST'])
def start_image_detection():
    try:
        script_path = r'C:\Users\Gustavo\Desktop\codigos vs\projeto\app\word_detection.py'
        subprocess.Popen(['python', script_path])
        return jsonify({'message': 'Identificação automática de textos via imagem iniciada com sucesso.'}), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao iniciar a identificação de textos via imagem: {str(e)}'}), 500
