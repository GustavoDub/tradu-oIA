import cv2
from paddleocr import PaddleOCR
from matplotlib import pyplot as plt
from tkinter import filedialog, Tk, Toplevel, StringVar, Label, OptionMenu, Button
from googletrans import Translator

# Inicializando o OCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Use 'pt' se houver suporte para português

# Inicializando o tradutor
translator = Translator()

def selecionar_imagem():
    # Usando tkinter para abrir uma janela de seleção de arquivo
    root = Tk()
    root.withdraw()  # Oculta a janela principal
    file_path = filedialog.askopenfilename()  # Abre o seletor de arquivos
    return file_path

def draw_ocr_with_translations(image, boxes, texts, translations):
    # Desenhar retângulos e exibir textos e traduções
    for box, text, translation in zip(boxes, texts, translations):
        # Desenhar retângulo
        cv2.rectangle(image, (int(box[0][0]), int(box[0][1])), (int(box[2][0]), int(box[2][1])), (0, 255, 0), 2)
        # Desenhar texto original e tradução
        cv2.putText(image, f"{text} - {translation}", (int(box[0][0]), int(box[0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return image

def selecionar_idioma():
    # Janela para seleção de idioma
    lang_window = Toplevel()
    lang_window.title("Seleção de Idioma")

    # Variável para armazenar o idioma de saída
    dest_lang = StringVar(lang_window)
    dest_lang.set("pt")  # Idioma de saída padrão

    # Dicionário com os idiomas disponíveis
    idiomas = {
        'Português': 'pt',
        'Inglês': 'en',
        'Espanhol': 'es',
        'Francês': 'fr',
        'Alemão': 'de',
        'Italiano': 'it',
        'Chinês (Simplificado)': 'zh-cn',
        'Japonês': 'ja',
        'Russo': 'ru'
    }

    # Menu para seleção de idioma
    Label(lang_window, text="Idioma de Saída:").pack()
    OptionMenu(lang_window, dest_lang, *idiomas.values()).pack()

    # Botão para fechar a janela de seleção
    Button(lang_window, text="Confirmar", command=lang_window.destroy).pack()

    lang_window.wait_window()  # Espera o usuário selecionar e fechar a janela

    return dest_lang.get()

def processar_imagem_e_exibir_texto():
    # Selecionar a imagem desejada
    imagem_path = selecionar_imagem()
    if not imagem_path:
        print("Nenhuma imagem selecionada.")
        return

    # Selecionar o idioma de saída
    dest_lang = selecionar_idioma()

    # Carregar a imagem
    imagem = cv2.imread(imagem_path)
    if imagem is None:
        print("Erro ao carregar a imagem.")
        return

    # Executar OCR na imagem
    resultado = ocr.ocr(imagem_path, cls=True)

    # Extrair as caixas de texto e textos detectados
    caixas = []
    palavras = []
    traducoes = []
    for linha in resultado:
        for det in linha:
            caixas.append(det[0])  # Coordenadas do retângulo
            palavra = det[1][0]  # Texto detectado
            palavras.append(palavra)
            try:
                # Traduzir a palavra para o idioma de saída selecionado
                traducao = translator.translate(palavra, src='en', dest=dest_lang).text
            except Exception as e:
                traducao = "[Erro na tradução]"
                print(f"Erro ao traduzir '{palavra}': {e}")
            traducoes.append(traducao)

    # Desenhar retângulos e exibir textos e traduções
    imagem_annotada = draw_ocr_with_translations(imagem, caixas, palavras, traducoes)

    # Convertendo para RGB para exibir com matplotlib
    imagem_rgb = cv2.cvtColor(imagem_annotada, cv2.COLOR_BGR2RGB)

    # Definir o tamanho padrão da figura
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))  # Ajuste o tamanho conforme necessário

    # Exibindo a imagem no primeiro subplot
    axs[0].imshow(imagem_rgb)
    axs[0].axis('off')
    axs[0].set_title('Imagem')

    # Exibindo as traduções no segundo subplot
    text = '\n'.join([f"Texto: {palavra}\nTradução: {traducao}\n" for palavra, traducao in zip(palavras, traducoes)])
    axs[1].text(0.1, 0.9, text, fontsize=12, verticalalignment='top')
    axs[1].axis('off')
    axs[1].set_title('Textos Detectados e Traduções')

    # Exibir a figura
    plt.tight_layout()
    plt.show()

# Executa o processo completo
processar_imagem_e_exibir_texto()
