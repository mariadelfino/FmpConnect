document.addEventListener("DOMContentLoaded", () => {
    const chatContainer = document.getElementById('chat-container');
    const input = document.getElementById('pergunta-input');
    // Captura direta do botão de envio
    const sendButton = document.getElementById('botao-enviar');
    const micButton = document.getElementById('botao-microfone');
    const resetButton = document.getElementById('botao-reset');
    
    const SURDEZ_KEY = 'senachat_modo_surdez';
    const INSTRUCAO_SURDEZ = 'INSTRUÇÃO ESPECIAL: Responda de forma extremamente concisa e clara. Use frases curtas, evite gírias, ironias, metáforas e termos difíceis. Se usar um termo técnico, explique-o rapidamente com um exemplo concreto. Aplique todas as regras de comunicação acessível para pessoas com deficiência auditiva em português.';

    const HISTORICO_KEY = 'senachat_sessao_atual_v1';
    const welcomeModal = document.getElementById('welcome-modal');
    const welcomeOptions = welcomeModal && welcomeModal.querySelectorAll('.welcome-option');
    const deafModeOption = document.getElementById('opcao-modo-surdez'); 

    // --- Lógica de Voz (Web Speech API) ---
    if (micButton) {
        // Verifica compatibilidade com a API
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.lang = 'pt-BR'; 
            recognition.continuous = false; // Para de gravar ao detectar silêncio
            recognition.interimResults = false; 

            micButton.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Se já estiver gravando, para
                if (micButton.classList.contains('gravando')) {
                    recognition.stop();
                    return;
                }

                try {
                    recognition.start();
                } catch (error) {
                    console.error("Erro ao iniciar reconhecimento:", error);
                }
            });

            recognition.onstart = () => {
                console.log("Gravando...");
                micButton.classList.add('gravando');
                input.placeholder = "Ouvindo... Fale agora.";
            };

            recognition.onend = () => {
                console.log("Gravação finalizada.");
                micButton.classList.remove('gravando');
                input.placeholder = "Faça a sua pergunta";
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                if (transcript) {
                    console.log("Transcrição:", transcript);
                    input.value = transcript;
                    
                    // Pequeno delay para o usuário ver o texto antes de enviar
                    setTimeout(() => {
                        enviarMensagemDoUsuario();
                    }, 500);
                }
            };

            recognition.onerror = (event) => {
                console.error("Erro voz:", event.error);
                micButton.classList.remove('gravando');
                if(event.error === 'not-allowed') {
                    alert("Permita o uso do microfone para usar o chat de voz.");
                }
            };
        } else {
            console.log("Navegador não suporta Web Speech API");
            micButton.style.display = 'none';
        }
    }
    // --- Fim Lógica de Voz ---

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

            if (texto) mensagens.push({ role, content: texto });
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

    function adicionarMensagemVisual(texto, tipo) {
        const wrapper = document.createElement('div');
        wrapper.classList.add('mensagem-wrapper', tipo);

        const balaoMensagem = document.createElement('div');
        balaoMensagem.classList.add('mensagem-balao', tipo);

        if (tipo === 'bot') {
            balaoMensagem.innerHTML = `<div class="mensagem-conteudo">${texto}</div>`;
            wrapper.appendChild(balaoMensagem);
        } else {
            wrapper.classList.add('user');
            const balaoUsuario = document.createElement('div');
            balaoUsuario.classList.add('mensagem-balao', 'usuario');
            balaoUsuario.innerHTML = `<p>${texto}</p>`;
            wrapper.appendChild(balaoUsuario);
        }
        chatContainer.appendChild(wrapper);
        rolarParaOFinal();
        return balaoMensagem;
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
        let promptFinal = texto;
        const modoSurdezAtivo = sessionStorage.getItem(SURDEZ_KEY) === 'true';
        const historicoContexto = obterHistoricoParaAPI();

        if (modoSurdezAtivo && historicoContexto.length === 0) {
            promptFinal = `${INSTRUCAO_SURDEZ} ${texto}`;
        }
        adicionarMensagemVisual(texto, 'usuario');
        input.value = "";

        const botBalao = adicionarMensagemVisual('...', 'bot');

        (async () => {
            try {
                const resp = await fetch(window.location.origin + '/text/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: promptFinal,
                        history: historicoContexto
                    })
                });
                if (!resp.ok) throw new Error(`Erro ${resp.status}`);

                const data = await resp.json();

                if (data.answer) {
                    const htmlFinal = renderMarkdownToHtml(data.answer);
                    botBalao.querySelector('.mensagem-conteudo').innerHTML = htmlFinal;
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
                // Foca de volta no input após responder
                input.focus(); 
            }
        })();
    }

    function renderMarkdownToHtml(mdText) {
        if (!mdText) return '';
        let text = mdText.toString();

        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');

        const listPattern = /(^|\n)[ \t]*([\*+-])[ \t]+(.*?)(?=\n|$)/g;
        text = text.replace(listPattern, '$1<li>$3</li>');
        text = text.replace(/((<li>.*?<\/li>[\s\S]*?)+)/g, '<ul>$1</ul>');

        text = text.replace(/\n/g, '<br>');

        return text;
    }

    if (sendButton) {
        sendButton.addEventListener('click', (e) => {
            e.preventDefault(); 
            enviarMensagemDoUsuario();
        });
    }

    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            enviarMensagemDoUsuario();
        }
    });

    const params = new URLSearchParams(window.location.search);
    const perguntaPreDefinida = params.get('pergunta');

    if (perguntaPreDefinida) {
        history.replaceState(null, '', window.location.pathname);
    }

    const temHistorico = carregarSessaoAnterior();

    if (perguntaPreDefinida) {
        if (welcomeModal) welcomeModal.classList.add('hidden');
        setTimeout(() => enviarMensagemDoUsuario(perguntaPreDefinida), 200);

    } else if (!temHistorico && welcomeModal) {
        setTimeout(() => {
            welcomeModal.classList.remove('hidden');
        }, 500);
    }

    if (deafModeOption) {
        deafModeOption.addEventListener('click', () => {
            const instrucaoAcessivel = 'Sou deficiente auditivo e desejo que você me responda de forma mais acessível e clara em português.';
            sessionStorage.setItem(SURDEZ_KEY, 'true');

            if (welcomeModal) welcomeModal.classList.add('hidden');
            setTimeout(() => enviarMensagemDoUsuario(instrucaoAcessivel), 200);
        });
    }

    if (welcomeOptions) {
        welcomeOptions.forEach(btn => {
            if (btn.id === 'opcao-modo-surdez') return;
            btn.addEventListener('click', () => {
                const q = btn.textContent.trim();
                input.value = q;
                sessionStorage.setItem(SURDEZ_KEY, 'false');

                if (welcomeModal) welcomeModal.classList.add('hidden');
                setTimeout(() => enviarMensagemDoUsuario(q), 200);
            });
        });
    }

    if (input && welcomeModal) {
        input.addEventListener('focus', () => {
            welcomeModal.classList.add('hidden');
            sessionStorage.setItem(SURDEZ_KEY, 'false');
        });
    }

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