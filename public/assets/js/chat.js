document.addEventListener("DOMContentLoaded", () => {
    const chatContainer = document.getElementById('chat-container');
    const input = document.getElementById('pergunta-input');
    const sendButton = document.getElementById('botao-enviar') || document.getElementById('botao-enviar-wave'); 
    const micButton = document.getElementById('botao-microfone');

    if (micButton) {
        micButton.addEventListener('click', () => {
            window.location.href = 'voz.html';
        });
    }

    const HISTORICO_KEY = 'senachat_sessao_atual_v1';
    const welcomeModal = document.getElementById('welcome-modal');
    const welcomeOptions = welcomeModal && welcomeModal.querySelectorAll('.welcome-option');

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

        const historicoContexto = obterHistoricoParaAPI();

        adicionarMensagemVisual(texto, 'usuario');
        input.value = ""; 

        const botBalao = adicionarMensagemVisual('...', 'bot');

        (async () => {
            try {
                const resp = await fetch(window.location.origin + '/text/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: texto,
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
            }
        })();
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
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

    if (sendButton) sendButton.addEventListener('click', enviarMensagemDoUsuario);
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

    if (welcomeOptions) {
        welcomeOptions.forEach(btn => {
            btn.addEventListener('click', () => {
                const q = btn.textContent.trim();
                input.value = q;
                if (welcomeModal) welcomeModal.classList.add('hidden');
                setTimeout(() => enviarMensagemDoUsuario(q), 200); 
            });
        });
    }

    if (input && welcomeModal) {
        input.addEventListener('focus', () => {
            welcomeModal.classList.add('hidden');
        });
    }

    window.resetChat = function() {
        sessionStorage.removeItem(HISTORICO_KEY);
        location.reload();
    };
});