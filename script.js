// Variáveis de controle para gravação e reconhecimento de fala
let isRecording = false;
let recognition;

// Função para ativar/desativar reconhecimento de fala
document.getElementById("translate-voice-button").addEventListener('click', async function () {
    const languageTo = document.getElementById("language-to-speech").value;
    const translationOutput = document.getElementById("translation-output-speech");
    const voiceIcon = document.getElementById("voice-icon");
    const recordingStatus = document.getElementById('recording-status');

    if (!isRecording) {
        isRecording = true;
        voiceIcon.innerText = '⏹';
        recordingStatus.style.display = 'block';

        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'pt-BR';
        recognition.start();

        recognition.onresult = async function(event) {
            const speechResult = event.results[0][0].transcript;

            try {
                const response = await fetch('/recognize-speech', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ language_to: languageTo, text: speechResult })
                });

                const data = await response.json();
                if (data.error) {
                    alert(data.error);
                } else {
                    translationOutput.innerText = data.translation;
                }
            } catch (error) {
                console.error("Erro ao reconhecer fala:", error);
                alert("Erro ao reconhecer fala. Por favor, tente novamente.");
            } finally {
                resetRecordingState();
            }
        };

        recognition.onerror = function(event) {
            console.error("Erro de reconhecimento de fala:", event.error);
            alert("Erro de reconhecimento de fala. Por favor, tente novamente.");
            resetRecordingState();
        };

    } else {
        recognition.stop();
        resetRecordingState();
    }
});

function resetRecordingState() {
    isRecording = false;
    document.getElementById("voice-icon").innerText = '🎤';
    document.getElementById('recording-status').style.display = 'none';
}

// Funções para abrir e fechar modais
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Abrir modais específicos
document.getElementById("btn-text-translation").onclick = function() {
    openModal('modal-text-translation');
};
document.getElementById("btn-speech-translation").onclick = function() {
    openModal('modal-speech-translation');
};
document.getElementById("btn-camera-text").onclick = function() {
    openModal('modal-camera-text');
};
document.getElementById("btn-image-text").onclick = function() {
    openModal('modal-image-text');
};

// Fechar modal ao clicar fora dele
window.onclick = function(event) {
    const modals = document.getElementsByClassName('modal');
    for (let i = 0; i < modals.length; i++) {
        if (event.target === modals[i]) {
            modals[i].style.display = "none";
        }
    }
};

// Variáveis e funções para controle dos ícones de Vassourinha e Megafone
let isSpeaking = false;
let synth = window.speechSynthesis;

// Função para limpar o texto de saída e desativar o ícone de Vassourinha
function clearText() {
    document.getElementById("translation-output-text").innerText = '';
    document.getElementById("clear-icon").classList.add("disabled");
    document.getElementById("clear-icon").disabled = true;
}

// Função para alternar entre fala e silêncio
function toggleSpeak() {
    const outputText = document.getElementById("translation-output-text").innerText;
    const speakerIcon = document.getElementById("speaker-icon");

    if (outputText && !isSpeaking) {
        let utterance = new SpeechSynthesisUtterance(outputText);
        synth.speak(utterance);
        isSpeaking = true;
        speakerIcon.textContent = "🔇"; // Ícone de megafone silenciado
        utterance.onend = () => {
            isSpeaking = false;
            speakerIcon.textContent = "📢"; // Retorna ao ícone de megafone normal
        };
    } else if (isSpeaking) {
        synth.cancel();
        isSpeaking = false;
        speakerIcon.textContent = "📢"; // Retorna ao ícone de megafone normal
    }
}

// Habilitar/desabilitar o ícone de Vassourinha com base no conteúdo do texto de saída
document.getElementById("text-input").addEventListener('input', function () {
    const clearIcon = document.getElementById("clear-icon");
    const outputText = document.getElementById("translation-output-text").innerText;

    if (outputText.trim() === "") {
        clearIcon.classList.add("disabled");
        clearIcon.disabled = true;
    } else {
        clearIcon.classList.remove("disabled");
        clearIcon.disabled = false;
    }
});

// Função para enviar o texto do textarea para tradução
document.getElementById("translate-text-button").onclick = async function () {
    const textInput = document.getElementById("text-input").value;
    const languageTo = document.getElementById("language-to-text").value;
    const translationOutput = document.getElementById("translation-output-text");

    if (!textInput.trim()) {
        alert("Por favor, insira o texto para tradução.");
        return;
    }

    try {
        const response = await fetch('/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: textInput, language_to: languageTo })
        });

        const result = await response.json();
        if (result.error) {
            alert(result.error);
        } else {
            translationOutput.innerText = result.translation;
            enableClearButton();
        }
    } catch (error) {
        console.error("Erro ao traduzir:", error);
        alert("Erro ao traduzir. Por favor, tente novamente.");
    }
};

// Função para ativar o botão de limpar após tradução
function enableClearButton() {
    const clearIcon = document.getElementById("clear-icon");
    clearIcon.disabled = false;
    clearIcon.classList.remove("disabled");
}

// Função para abrir o modal
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = "block";
    }
}

// Função para fechar o modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = "none";
    }
}

// Adicionar eventos aos botões do menu principal
document.getElementById("btn-text-translation").addEventListener("click", () => openModal("modal-text-translation"));
document.getElementById("btn-speech-translation").addEventListener("click", () => openModal("modal-speech-translation"));
document.getElementById("btn-camera-text").addEventListener("click", () => openModal("modal-camera-text"));
document.getElementById("btn-image-text").addEventListener("click", () => openModal("modal-image-text"));

// Fechar o modal ao clicar fora da área de conteúdo
window.addEventListener("click", function (event) {
    const modals = document.querySelectorAll(".modal");
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
});

// Função para limpar o texto da área de entrada
function clearText() {
    const textInput = document.getElementById("text-input");
    if (textInput) {
        textInput.value = "";
        const clearIcon = document.getElementById("clear-icon");
        clearIcon.classList.add("disabled");
        clearIcon.disabled = true;
    }
}

// Monitorar mudanças no textarea para habilitar/desabilitar o botão de limpeza
document.getElementById("text-input").addEventListener("input", function () {
    const clearIcon = document.getElementById("clear-icon");
    if (this.value.trim()) {
        clearIcon.classList.remove("disabled");
        clearIcon.disabled = false;
    } else {
        clearIcon.classList.add("disabled");
        clearIcon.disabled = true;
    }
});

// Função para ativar/desativar o áudio do texto traduzido
function toggleSpeak() {
    const translationOutput = document.getElementById("translation-output-text").innerText;
    if (translationOutput.trim()) {
        const utterance = new SpeechSynthesisUtterance(translationOutput);
        utterance.lang = document.getElementById("language-to-text").value;
        window.speechSynthesis.speak(utterance);
    }
}

// Função de troca de idiomas
document.getElementById("swap-languages-button").addEventListener("click", function () {
    const languageFrom = document.getElementById("language-from-text");
    const languageTo = document.getElementById("language-to-text");
    const temp = languageFrom.value;
    languageFrom.value = languageTo.value;
    languageTo.value = temp;
});

// Função para iniciar o OCR da câmera
document.getElementById("btn-camera-ocr").addEventListener("click", function() {
    fetch('/start-camera', {
        method: 'POST',
        body: new URLSearchParams({
            'language_to': document.getElementById("language-to-text").value
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            // Exibir a imagem capturada com os bounding boxes
            const imageElement = document.createElement('img');
            imageElement.src = `data:image/jpeg;base64,${data.image}`;
            document.getElementById("image-text-output-camera").appendChild(imageElement);

            // Exibir o texto original capturado
            const originalTextElement = document.createElement('p');
            originalTextElement.textContent = `Texto Original: ${data.original_text}`;
            document.getElementById("image-text-output-camera").appendChild(originalTextElement);

            // Exibir a tradução do texto
            const translatedTextElement = document.createElement('p');
            translatedTextElement.textContent = `Tradução: ${data.translated_text}`;
            document.getElementById("image-text-output-camera").appendChild(translatedTextElement);

            // Tornar a div de saída visível
            document.getElementById("image-text-output-camera").style.display = "block";
        }
    })
    .catch(error => {
        console.error("Erro ao iniciar o OCR da câmera:", error);
    });
});

// Função para selecionar a imagem do computador
document.getElementById("btn-select-image").addEventListener("click", function() {
    document.getElementById("image-selection-container").style.display = "block";
});

// Função para iniciar o OCR da imagem selecionada
document.getElementById("btn-start-ocr").addEventListener("click", function() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = function(event) {
        const file = event.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('image', file);
            formData.append('language_to', document.getElementById("language-to-image").value);

            const loader = document.getElementById('loader-image-text');
            loader.style.display = 'block';

            fetch('/recognize-image-text', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    // Exibir a imagem com os bounding boxes
                    const imageElement = document.createElement('img');
                    imageElement.src = `data:image/jpeg;base64,${data.image}`;
                    document.getElementById("image-selection-container").appendChild(imageElement);

                    // Exibir o texto original capturado e a tradução
                    const textArea = document.getElementById("image-text-output");
                    textArea.value = `Texto Original: ${data.text}\nTradução: ${data.translation}`;

                    // Exibir o botão para mostrar a imagem com bounding boxes
                    document.getElementById("btn-show-image").style.display = "block";

                    // Exibir o contêiner de seleção de imagem
                    document.getElementById("image-selection-container").style.display = "block";
                }
            })
            .catch(error => {
                console.error("Erro ao processar a imagem:", error);
            })
            .finally(() => {
                loader.style.display = 'none';
            });
        }
    };
    input.click();
});

// Função para exibir a imagem com bounding boxes
document.getElementById("btn-show-image").addEventListener("click", function() {
    const imageElement = document.getElementById("image-selection-container").querySelector('img');
    if (imageElement) {
        const win = window.open();
        win.document.write(imageElement.outerHTML);
        win.document.close();
    }
});
