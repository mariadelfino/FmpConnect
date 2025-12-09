document.addEventListener("DOMContentLoaded", () => {
    const chatContainer = document.getElementById('chat-container');
    const input = document.getElementById('pergunta-input');
    
    const sendButton = document.getElementById('botao-enviar');
    const micButton = document.getElementById('botao-microfone');
    const resetButton = document.getElementById('botao-reset');
    
    const SURDEZ_KEY = 'fmpconnect_modo_surdez';
    const HISTORICO_KEY = 'fmpconnect_sessao_atual_v1';
    
    const welcomeModal = document.getElementById('welcome-modal');
    const welcomeOptions = welcomeModal && welcomeModal.querySelectorAll('.welcome-option');
    const deafModeOption = document.getElementById('opcao-modo-surdez'); 
    
    // --- Configuração de Voz (Mantida igual) ---
    if (micButton) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.lang = 'pt-BR'; 
            recognition.continuous = false; 
            recognition.interimResults = false; 
    
            micButton.addEventListener('click', (e) => {
                e.preventDefault();
                if (micButton.classList.contains('gravando')) {
                    recognition.stop();
                    return;
                }
                try { recognition.start(); } catch (error) { console.error(error); }
            });
    
            recognition.onstart = () => {
                micButton.classList.add('gravando');
                input.placeholder = "Ouvindo... Fale agora.";
            };
    
            recognition.onend = () => {
                micButton.classList.remove('gravando');
                input.placeholder = "Faça a sua pergunta";
            };
    
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                if (transcript) {
                    input.value = transcript;
                    setTimeout(() => enviarMensagemDoUsuario(), 500);
                }
            };
        } else {
            micButton.style.display = 'none';
        }
    }
    
    function rolarParaOFinal() {
        if (chatContainer) {
            setTimeout(() => {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }, 50);
        }
    }
    
    function salvarSessaoLocal() {
        const mensagens = [];
        const wrappers = chatContainer.querySelectorAll('.mensagem-wrapper');
    
        wrappers.forEach(wrapper => {
            const isUser = wrapper.classList.contains('user');
            const role = isUser ? 'user' : 'model';
            let texto = "";
    
            if (isUser) {
                const p = wrapper.querySelector('.mensagem-balao p');
                texto = p ? p.innerText : "";
            } else {
                const conteudo = wrapper.querySelector('.mensagem-conteudo');
                texto = conteudo ? conteudo.innerText : "";
            }
    
            if (texto && texto !== '...' && texto !== 'Desculpe, não entendi.') {
                mensagens.push({ role, content: texto });
            }
        });
    
        sessionStorage.setItem(HISTORICO_KEY, JSON.stringify(mensagens));
    }
    
    function obterHistoricoParaAPI() {
        const historico = [];
        const wrappers = document.querySelectorAll('.area-mensagens .mensagem-wrapper');
    
        wrappers.forEach(wrapper => {
            if (wrapper.innerText.trim() === '...') return;
            if (wrapper.innerText.includes("Erro de conexão")) return;
    
            const isUser = wrapper.classList.contains('user');
            const role = isUser ? 'user' : 'model';
            let content = "";
    
            if (isUser) {
                const p = wrapper.querySelector('.mensagem-balao p');
                if (p) content = p.innerText.trim();
            } else {
                const divConteudo = wrapper.querySelector('.mensagem-conteudo');
                if (divConteudo) content = divConteudo.innerText.trim();
            }
            if (content && content.length > 0) {
                historico.push({ role: role, content: content });
            }
        });
        return historico;
    }
    
    function criarBotaoAudio(texto) {
        const btnAudio = document.createElement('button');
        btnAudio.className = 'botao-ler-texto';
        btnAudio.title = "Ouvir mensagem";
        btnAudio.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 17 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M0.75 6.51749C0.75 5.41292 1.64543 4.51749 2.75 4.51749H4.75C5.30228 4.51749 5.75 4.9652 5.75 5.51749V12.5175C5.75 13.0698 5.30228 13.5175 4.75 13.5175H2.75C1.64543 13.5175 0.75 12.6221 0.75 11.5175V6.51749Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M12.8556 0.964703L6.85557 3.9647C6.178 4.30349 5.75 4.99601 5.75 5.75356V12.1634C5.75 12.9812 6.2479 13.7166 7.00722 14.0204L13.0072 16.4204C14.3209 16.9459 15.75 15.9784 15.75 14.5634V2.75356C15.75 1.26679 14.1854 0.299802 12.8556 0.964703Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
        `;
        btnAudio.addEventListener('click', () => lerTexto(texto, btnAudio));
        return btnAudio;
    }
    
    function adicionarMensagemVisual(texto, tipo) {
        const wrapper = document.createElement('div');
        wrapper.classList.add('mensagem-wrapper', tipo);
    
        const balaoMensagem = document.createElement('div');
        balaoMensagem.classList.add('mensagem-balao', tipo);
    
        if (tipo === 'bot') {
            balaoMensagem.innerHTML = `<div class="mensagem-conteudo">${renderMarkdownToHtml(texto)}</div>`;
            wrapper.appendChild(balaoMensagem);
    
            if (texto !== '...') {
                const btnAudio = criarBotaoAudio(texto);
                wrapper.appendChild(btnAudio);
            }
        } else {
            wrapper.classList.add('user');
            const balaoUsuario = document.createElement('div');
            balaoUsuario.classList.add('mensagem-balao', 'usuario');
            balaoUsuario.innerHTML = `<p>${texto}</p>`;
            wrapper.appendChild(balaoUsuario);
        }
    
        chatContainer.appendChild(wrapper);
        rolarParaOFinal();
        
        return { balao: balaoMensagem, wrapper: wrapper };
    }
    
    function toggleInput(disable) {
        if (input) input.disabled = disable;
        if (sendButton) sendButton.disabled = disable;
        const inputContainer = document.querySelector('.area-input-pergunta .container-input');
        if (inputContainer) {
            inputContainer.classList.toggle('input-disabled', disable);
        }
    }
    
    function carregarSessaoAnterior() {
        const salvo = sessionStorage.getItem(HISTORICO_KEY);
        if (salvo && chatContainer) {
            try {
                const mensagens = JSON.parse(salvo);
                chatContainer.innerHTML = '';
                mensagens.forEach(msg => {
                    adicionarMensagemVisual(msg.content, msg.role === 'user' ? 'usuario' : 'bot');
                });
                return true;
            } catch (e) {
                console.error("Erro ao carregar sessão", e);
            }
        }
        return false;
    }
    
    function enviarMensagemDoUsuario(textoAutomatico) {
        const texto = textoAutomatico ? textoAutomatico.trim() : input.value.trim();
        if (texto === "") return;
        
        toggleInput(true);
        
        const modoSurdezAtivo = sessionStorage.getItem(SURDEZ_KEY) === 'true';
        const modoEnvio = modoSurdezAtivo ? 'surdez' : 'normal';
    
        const historicoContexto = obterHistoricoParaAPI();
    
        adicionarMensagemVisual(texto, 'usuario');
        input.value = "";
    
        const botElementos = adicionarMensagemVisual('...', 'bot');
        const botBalao = botElementos.balao;
        const botWrapper = botElementos.wrapper;
    
        (async () => {
            try {
                const resp = await fetch(window.location.origin + '/text/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: texto,
                        history: historicoContexto,
                        mode: modoEnvio 
                    })
                });
                if (!resp.ok) throw new Error(`Erro ${resp.status}`);
    
                const data = await resp.json();
    
                if (data.answer) {
                    const htmlFinal = renderMarkdownToHtml(data.answer);
                    botBalao.querySelector('.mensagem-conteudo').innerHTML = htmlFinal;
    
                    const btnAudio = criarBotaoAudio(data.answer);
                    botWrapper.appendChild(btnAudio);
    
                    salvarSessaoLocal();
                    rolarParaOFinal();
                } else {
                    botBalao.querySelector('.mensagem-conteudo').textContent = "Desculpe, não entendi.";
                }
            } catch (e) {
                console.error(e);
                botBalao.querySelector('.mensagem-conteudo').textContent = "Erro de conexão.";
            } finally {
                toggleInput(false);
                input.focus(); 
            }
        })();
    }
    
    function renderMarkdownToHtml(mdText) {
        if (!mdText) return '';
        if (mdText === '...') return '...';
    
        let text = mdText.toString();
    
        // Links
        text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
        // Negrito
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Itálico
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
        // Tratamento de quebras e listas
        if (text.includes('\n') || text.includes('- ')) {
            const lines = text.split('\n');
            let output = '';
            let inList = false;
    
            lines.forEach(line => {
                let trimmed = line.trim();
                
                if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
                    if (!inList) { output += '<ul>'; inList = true; }
                    output += `<li>${trimmed.substring(2)}</li>`;
                } else {
                    if (inList) { output += '</ul>'; inList = false; }
                    if (trimmed.length > 0) {
                        output += `<p>${line}</p>`;
                    }
                }
            });
            if (inList) output += '</ul>';
            return output;
        } 
        return `<p>${text}</p>`; 
    }
    
    // Event Listeners
    if (sendButton) {
        sendButton.addEventListener('click', (e) => {
            e.preventDefault(); 
            enviarMensagemDoUsuario();
        });
    }
    
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                enviarMensagemDoUsuario();
            }
        });
        // Desativar surdez ao focar no input se o modal ainda estivesse ativo (opcional, mas mantido da sua lógica)
        input.addEventListener('focus', () => {
            if (welcomeModal && !welcomeModal.classList.contains('hidden')) {
                welcomeModal.classList.add('hidden');
                sessionStorage.setItem(SURDEZ_KEY, 'false');
            }
        });
    }
    
    // --- LÓGICA DO MODAL E URL ---
    const params = new URLSearchParams(window.location.search);
    const perguntaPreDefinida = params.get('pergunta');
    
    if (perguntaPreDefinida) {
        history.replaceState(null, '', window.location.pathname);
    }
    
    const temHistorico = carregarSessaoAnterior();
    
    // Se há pergunta na URL
    if (perguntaPreDefinida) {
        if (welcomeModal) welcomeModal.classList.add('hidden');
        setTimeout(() => enviarMensagemDoUsuario(perguntaPreDefinida), 200);
    } 
    // Se NÃO tem histórico e o modal existe, mostra o modal
    else if (!temHistorico && welcomeModal) {
        setTimeout(() => {
            welcomeModal.classList.remove('hidden');
        }, 500);
    }
    
    // Configura os botões do Modal
    if (deafModeOption) {
        deafModeOption.addEventListener('click', () => {
            sessionStorage.setItem(SURDEZ_KEY, 'true');
            if (welcomeModal) welcomeModal.classList.add('hidden');
            document.body.classList.add('modo-surdez-ativo');
    
            // Envia mensagem inicial para o backend registrar o contexto
            setTimeout(() => enviarMensagemDoUsuario("Olá, ativei o modo acessibilidade."), 200);
        });
    }
    
    if (welcomeOptions) {
        welcomeOptions.forEach(btn => {
            if (btn.id === 'opcao-modo-surdez') return;
            btn.addEventListener('click', () => {
                const q = btn.textContent.trim();
                input.value = q;
                sessionStorage.setItem(SURDEZ_KEY, 'false');
                document.body.classList.remove('modo-surdez-ativo');
    
                if (welcomeModal) welcomeModal.classList.add('hidden');
                setTimeout(() => enviarMensagemDoUsuario(q), 200);
            });
        });
    }
    
    // Restaura classe visual se recarregar a página
    if (sessionStorage.getItem(SURDEZ_KEY) === 'true') {
        document.body.classList.add('modo-surdez-ativo');
    }
    
    window.resetChat = function() {
        sessionStorage.removeItem(HISTORICO_KEY);
        sessionStorage.removeItem(SURDEZ_KEY); 
        location.reload();
    };
    
    if (resetButton) {
        resetButton.addEventListener('click', () => {
            window.resetChat();
        });
    }
});

let audioAtual = null; 

function limparTextoParaAudio(textoMarkdown) {
    let texto = textoMarkdown.toString();
    texto = texto.replace(/\*\*/g, '') 
                .replace(/\*/g, '')    
                .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') 
                .replace(/^#+\s+/gm, '') 
                .replace(/- /g, ', ')    
                .replace(/\n\n/g, '. ') 
                .replace(/\n/g, ' ');   
    return texto.trim();
}

async function lerTexto(texto, botaoElemento) {
    if (audioAtual) {
        audioAtual.pause();
        audioAtual = null;
        document.querySelectorAll('.botao-ler-texto').forEach(b => b.classList.remove('falando'));
    
        if (botaoElemento.classList.contains('tocando-agora')) {
            botaoElemento.classList.remove('tocando-agora');
            return;
        }
    }
    document.querySelectorAll('.botao-ler-texto').forEach(b => {
        b.classList.remove('falando');
        b.classList.remove('tocando-agora');
    });
    
    const textoLimpo = limparTextoParaAudio(texto);
    
    try {
        botaoElemento.classList.add('falando'); 
        botaoElemento.classList.add('tocando-agora');
    
        const response = await fetch(window.location.origin + '/text/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: textoLimpo })
        });
    
        if (!response.ok) throw new Error("Erro ao gerar áudio");
    
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        
        audioAtual = new Audio(url);
        
        audioAtual.onended = () => {
            botaoElemento.classList.remove('falando');
            botaoElemento.classList.remove('tocando-agora');
            audioAtual = null;
        };
        
        audioAtual.play();
    
    } catch (error) {
        console.error("Erro no TTS:", error);
        botaoElemento.classList.remove('falando');
        botaoElemento.classList.remove('tocando-agora');
    }
}