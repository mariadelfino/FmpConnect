document.addEventListener("DOMContentLoaded", () => {


    const chatContainer = document.getElementById('chat-container');
    const input = document.getElementById('pergunta-input');
    const sendButton = document.getElementById('botao-enviar') || document.getElementById('botao-enviar-wave') || document.querySelector('.botao-enviar') || document.querySelector('button[title="Enviar"]');

    const COURSE_KEYWORDS = ['jovem programador','jovemprogramador','senac','curso','programador','programação','programacao','inscr','matr','dura','duração','duracao','certificado','conteúdo','conteudo','grade','horário','horario','valor','preço','preco','local','público','publico'];

    function isRelatedToCourse(text) {
        if (!text) return false;
        const txt = text.toLowerCase();
        return COURSE_KEYWORDS.some(kw => txt.includes(kw));
    }

    if (chatContainer) {
        chatContainer.innerHTML = '';
    }

    function adicionarMensagem(texto, tipo) {
        const wrapper = document.createElement('div');
        wrapper.classList.add('mensagem-wrapper', tipo);

        const balaoMensagem = document.createElement('div');
        balaoMensagem.classList.add('mensagem-balao', tipo);
        balaoMensagem.innerHTML = `<div class="mensagem-conteudo">${escapeHtml(texto)}</div>`;

        if (tipo === 'bot') {
            wrapper.appendChild(balaoMensagem);
        } else if (tipo === 'usuario') {
            wrapper.classList.add('user');

            const balaoUsuario = document.createElement('div');
            balaoUsuario.classList.add('mensagem-balao', 'usuario');
            balaoUsuario.innerHTML = `<p>${texto}</p>`;

            wrapper.appendChild(balaoUsuario);
            chatContainer.appendChild(wrapper);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return balaoUsuario;
        } else {
            wrapper.appendChild(balaoMensagem);
        }
        chatContainer.appendChild(wrapper);

        chatContainer.scrollTop = chatContainer.scrollHeight;

        return balaoMensagem;
    }
    function enviarMensagemDoUsuario() {
        const texto = input.value.trim(); 
    
        if (texto !== "") {
            adicionarMensagem(texto, 'usuario');

            /*
            input.value = "";
            if (!isRelatedToCourse(texto)) {
                const msg = "Desculpe — eu só respondo perguntas relacionadas ao curso 'Jovem Programador' oferecido pelo Senac. Por favor, pergunte sobre conteúdo, duração, matrícula, pré-requisitos, valor, certificação, cronograma, local ou público-alvo.";
                adicionarMensagem(msg, 'bot');
                return;
            }

            */

            const botBalao = adicionarMensagem('...', 'bot');
            (async () => {
                try {
                    const resp = await fetch(window.location.origin + '/text/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ prompt: texto })
                    });

                    if (!resp.ok) {
                        const text = await resp.text().catch(()=>null);
                        console.error('Fetch /text/chat erro:', resp.status, text);
                        botBalao.querySelector('.mensagem-conteudo').textContent = `Erro ${resp.status}: resposta do servidor inválida.`;
                        return;
                    }

                    const data = await resp.json().catch(err => {
                        console.error('Erro ao parsear JSON de /text/chat:', err);
                        return null;
                    });

                    if (!data) {
                        botBalao.querySelector('.mensagem-conteudo').textContent = 'Resposta inválida do servidor';
                        return;
                    }

                    if (data.answer) {
                        const md = data.answer;
                        botBalao.querySelector('.mensagem-conteudo').innerHTML = renderMarkdownToHtml(md);
                    } else if (data.error) {
                        botBalao.querySelector('.mensagem-conteudo').textContent = data.error;
                    } else {
                        botBalao.querySelector('.mensagem-conteudo').textContent = 'Resposta inesperada do servidor';
                    }
                } catch (e) {
                    botBalao.querySelector('.mensagem-conteudo').textContent = 'Erro ao contatar o servidor';
                }
            })();
        }
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function renderMarkdownToHtml(mdText) {
        if (!mdText) return '';
        let text = mdText.toString();

        text = text.replace(/```([\s\S]*?)```/g, function(_, code) {
            return '<pre><code>' + escapeHtml(code) + '</code></pre>';
        });
        text = text.replace(/^###\s*(.*)$/gm, '<h3>$1</h3>');
        text = text.replace(/^##\s*(.*)$/gm, '<h2>$1</h2>');
        text = text.replace(/^#\s*(.*)$/gm, '<h1>$1</h1>');
        text = text.replace(/(^|\n)-\s+(.*?)(?=\n|$)/g, function(_, prefix, item) {
            return '\n<ul><li>' + escapeHtml(item) + '</li></ul>';
        });
        text = text.replace(/`([^`]+)`/g, function(_, code) {
            return '<code>' + escapeHtml(code) + '</code>';
        });
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/__(.*?)__/g, '<strong>$1</strong>');
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        text = text.replace(/_(.*?)_/g, '<em>$1</em>');

        const parts = text.split(/(<pre>[\s\S]*?<\/pre>)/g);
        for (let i = 0; i < parts.length; i++) {
            if (!parts[i].startsWith('<pre>')) {

                parts[i] = escapeHtml(parts[i]);
                parts[i] = parts[i].replace(/&lt;h1&gt;(.*?)&lt;\/h1&gt;/g, '<h1>$1</h1>');
                parts[i] = parts[i].replace(/&lt;h2&gt;(.*?)&lt;\/h2&gt;/g, '<h2>$1</h2>');
                parts[i] = parts[i].replace(/&lt;h3&gt;(.*?)&lt;\/h3&gt;/g, '<h3>$1</h3>');
                parts[i] = parts[i].replace(/&lt;pre&gt;(.*?)&lt;\/pre&gt;/g, '<pre>$1</pre>');
                parts[i] = parts[i].replace(/&lt;code&gt;(.*?)&lt;\/code&gt;/g, '<code>$1</code>');
                parts[i] = parts[i].replace(/\n/g, '<br>');
            }
        }
        text = parts.join('');

        text = text.replace(/(<ul>\s*<li>.*?<\/li>\s*<\/ul>)+/gs, function(m) { return m; });

        return text;
    }

    function simularRespostaBot(pergunta) {
        adicionarMensagem("Esta é uma resposta automática. A IA ainda não está conectada.", 'bot');
    }
    if (sendButton) {
        sendButton.addEventListener('click', enviarMensagemDoUsuario);
    }

    input.addEventListener('keypress', (event) => {

        if (event.key === 'Enter') {
            event.preventDefault(); 
            enviarMensagemDoUsuario();
        }
    });

    console.log("Chat.js carregado com sucesso!");
    const WELCOME_KEY = 'senachat_welcome_shown_v1';
    const welcomeModal = document.getElementById('welcome-modal');
    const welcomeOptions = welcomeModal && welcomeModal.querySelectorAll('.welcome-option');

    let _modalShownAt = null; 
    let _lastPointerDown = 0; 

    document.addEventListener('pointerdown', () => { _lastPointerDown = Date.now(); }, true);

    function hideWelcomeModal(persist = true) {
        if (!welcomeModal) return;
        welcomeModal.classList.add('hidden');
        _modalShownAt = null;
        if (persist) {
            try { localStorage.setItem(WELCOME_KEY, '1'); console.log('[Welcome] flag salva em localStorage'); } catch (e) { console.warn('[Welcome] falha ao salvar flag', e); }
        } else {
            console.log('[Welcome] modal escondido sem persistir a flag (modo não-persistente)');
        }
    }

    function showWelcomeModalIfNeeded() {
        if (!welcomeModal) return;
        try {
            console.log('[Welcome] exibindo modal (ignorado localStorage para garantir visibilidade)');
        } catch (e) {}
        welcomeModal.classList.remove('hidden');
        _modalShownAt = Date.now();
    }

    if (welcomeOptions && welcomeOptions.length) {
        welcomeOptions.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const q = btn.textContent.trim();
                if (input) { input.value = q; }
                hideWelcomeModal(true);
                setTimeout(() => {
                    enviarMensagemDoUsuario();
                }, 120);
            });
        });
    }
    if (input) {
        input.addEventListener('focus', () => {
            if (!_modalShownAt) {
                hideWelcomeModal(false);
                return;
            }
            const elapsed = Date.now() - _modalShownAt;
            if (elapsed > 700) {
                const sincePointer = Date.now() - _lastPointerDown;
                const userClicked = sincePointer < 800; 
                hideWelcomeModal(userClicked);
            }
        });
    }
    setTimeout(showWelcomeModalIfNeeded, 400);

    window.forceShowWelcomeModal = function() {
        try { localStorage.removeItem(WELCOME_KEY); } catch (e) {}
        console.log('[Welcome] forceShowWelcomeModal chamado — removida flag e mostrando modal.');
        showWelcomeModalIfNeeded();
    };
});