/**
 * Sistema Global de Acessibilidade
 * Injeta e controla o painel de acessibilidade em todas as páginas
 */

(function() {
    'use strict';

    const PAINEL_HTML_PATH = './assets/html/painel-acessibilidade.html';
    const STORAGE_KEY = 'Fmpconnect-acessibilidade';
    const PAINEL_OPEN_KEY = 'Fmpconnect-acessibilidade-painel-aberto';
    
    // Estado da acessibilidade
    let estadoAtual = {
        tema: null, // será definido pela detecção do sistema
        contraste: false,
        scaleFactor: 1,
        filtroDaltonismo: 'none'
    };

    // Detecta preferência do sistema
    function detectarTemaDoSistema() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
            return 'claro';
        }
        return 'escuro';
    }

    // Carrega preferências salvas ou usa padrão do sistema
    function carregarPreferencias() {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
            try {
                estadoAtual = JSON.parse(saved);
            } catch (e) {
                console.error('[Acessibilidade] Erro ao carregar preferências:', e);
            }
        }
        
        // Se não há tema salvo, usa a preferência do sistema
        if (!estadoAtual.tema) {
            estadoAtual.tema = detectarTemaDoSistema();
        }
        
        aplicarEstado();
    }

    // Salva preferências
    function salvarPreferencias() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(estadoAtual));
    }

    // Aplica o estado atual
    function aplicarEstado() {
        // Aplica tema
        if (estadoAtual.tema === 'claro') {
            document.documentElement.setAttribute('data-theme', 'light');
        } else {
            document.documentElement.setAttribute('data-theme', 'dark');
        }

        // Aplica escala de fonte
        document.documentElement.style.setProperty('--scale-factor', estadoAtual.scaleFactor);

        // Aplica filtro de daltonismo
        aplicarFiltroDaltonismoCSS(estadoAtual.filtroDaltonismo);

        // Aplica alto contraste no MAIN em vez do body
        const mains = document.querySelectorAll('main');
        mains.forEach(main => {
            if (estadoAtual.contraste) {
                main.classList.add('alto-contraste');
            } else {
                main.classList.remove('alto-contraste');
            }
        });
        
        // Marca no body para referência e ativa otimizações
        if (estadoAtual.contraste) {
            document.body.setAttribute('data-alto-contraste', 'true');
            document.body.classList.add('filtros-ativos'); // Ativa otimizações (remove shadows)
        } else {
            document.body.removeAttribute('data-alto-contraste');
            // Só remove filtros-ativos se também não tiver filtro de daltonismo
            if (estadoAtual.filtroDaltonismo === 'none') {
                document.body.classList.remove('filtros-ativos');
            }
        }
    }
    
    async function carregarPainelAcessibilidade() {
        try {
            const response = await fetch(PAINEL_HTML_PATH);
            const html = await response.text();
            
            const container = document.createElement('div');
            container.innerHTML = html;
            document.body.appendChild(container.firstElementChild);
            
            inicializarPainel();
            atualizarUIParaEstadoAtual();
            // Se o usuário deixou o painel aberto em navegações anteriores, mantê-lo aberto
            try {
                if (localStorage.getItem(PAINEL_OPEN_KEY) === '1') {
                    const painel = document.getElementById('painelAcessibilidade');
                    if (painel) painel.classList.add('ativo');
                }
            } catch (e) {
                // localStorage pode falhar em ambientes restritos; ignorar sem quebrar
                console.warn('[Acessibilidade] Não foi possível ler estado do painel:', e);
            }
        } catch (error) {
            console.error('[Acessibilidade] Erro ao carregar painel:', error);
        }
    }

    // Atualiza a UI do painel para refletir o estado atual
    function atualizarUIParaEstadoAtual() {
        // Atualiza tema
        const opcoesTema = document.querySelectorAll('[data-opcao^="tema-"]');
        opcoesTema.forEach(opt => {
            const isTemaEscuro = opt.dataset.opcao === 'tema-escuro';
            const isTemaClaro = opt.dataset.opcao === 'tema-claro';
            const isAtivo = (isTemaEscuro && estadoAtual.tema === 'escuro') || 
                           (isTemaClaro && estadoAtual.tema === 'claro');
            
            opt.classList.toggle('ativo', isAtivo);
            const status = opt.querySelector('.opcao-acessibilidade_status');
            if (status) status.textContent = isAtivo ? 'Ativo' : 'Inativo';
        });

        // Atualiza alto contraste
        const altoContraste = document.querySelector('[data-opcao="alto-contraste"]');
        if (altoContraste) {
            altoContraste.classList.toggle('ativo', estadoAtual.contraste);
            const status = altoContraste.querySelector('.opcao-acessibilidade_status');
            if (status) status.textContent = estadoAtual.contraste ? 'Ativo' : 'Inativo';
        }

        // Atualiza filtro daltonismo
        const opcoesDaltonismo = document.querySelectorAll('[data-opcao^="daltonismo-"]');
        opcoesDaltonismo.forEach(opt => {
            const tipo = opt.dataset.opcao.replace('daltonismo-', '');
            const isAtivo = (tipo === 'desativar' && estadoAtual.filtroDaltonismo === 'none') ||
                           estadoAtual.filtroDaltonismo === tipo;
            opt.classList.toggle('ativo', isAtivo);
        });

        // Atualiza descrição do tamanho da fonte
        atualizarDescricaoFonte();
    }

    function inicializarPainel() {
        const painel = document.getElementById('painelAcessibilidade');
        const botoesAbrir = document.querySelectorAll('.botao-acessibilidade');
        const botaoFechar = painel.querySelector('.painel-acessibilidade_fechar');
        const conteudo = painel.querySelector('.painel-acessibilidade_conteudo');
        const opcoes = painel.querySelectorAll('.opcao-acessibilidade');
        const botaoResetar = painel.querySelector('.painel-acessibilidade_resetar');

        function abrirPainel() {
            painel.classList.add('ativo');
            try { localStorage.setItem(PAINEL_OPEN_KEY, '1'); } catch (e) { /* ignore */ }
        }

        function fecharPainel() {
            painel.classList.remove('ativo');
            try { localStorage.removeItem(PAINEL_OPEN_KEY); } catch (e) { /* ignore */ }
        }

        botoesAbrir.forEach(botao => {
            botao.addEventListener('click', (e) => {
                e.stopPropagation();
                abrirPainel();
            });
        });

        botaoFechar.addEventListener('click', fecharPainel);

        // Intencionalmente NÃO fecha o painel ao clicar fora ou ao pressionar Escape.
        // O objetivo é que o usuário mantenha o painel aberto até fechar manualmente com o botão X.

        opcoes.forEach(opcao => {
            opcao.addEventListener('click', () => {
                const tipo = opcao.dataset.opcao;
                handleOpcaoClick(tipo, opcao);
            });
        });

        // Listener específico para o botão de resetar
        if (botaoResetar) {
            botaoResetar.addEventListener('click', () => {
                resetarTudo();
            });
        }
    }

    function handleOpcaoClick(tipo, elemento) {
        console.log(`[Acessibilidade] Opção clicada: ${tipo}`);
        
        switch(tipo) {
            case 'tema-escuro':
                alterarTema('escuro');
                break;
            case 'tema-claro':
                alterarTema('claro');
                break;
            case 'alto-contraste':
                toggleAltoContraste();
                break;
            case 'fonte-aumentar':
                ajustarFonte('+');
                break;
            case 'fonte-diminuir':
                ajustarFonte('-');
                break;
            case 'fonte-resetar':
                ajustarFonte('reset');
                break;
            case 'daltonismo-protanopia':
                aplicarFiltroDaltonismo('protanopia');
                break;
            case 'daltonismo-deuteranopia':
                aplicarFiltroDaltonismo('deuteranopia');
                break;
            case 'daltonismo-tritanopia':
                aplicarFiltroDaltonismo('tritanopia');
                break;
            case 'daltonismo-desativar':
                aplicarFiltroDaltonismo('none');
                break;
            case 'resetar-tudo':
                resetarTudo();
                break;
        }
    }

    function alterarTema(tema) {
        estadoAtual.tema = tema;
        aplicarEstado();
        salvarPreferencias();
        atualizarUIParaEstadoAtual();
    }

    function toggleAltoContraste() {
        estadoAtual.contraste = !estadoAtual.contraste;
        aplicarEstado();
        salvarPreferencias();
        atualizarUIParaEstadoAtual();
    }

    function ajustarFonte(acao) {
        if (acao === '+') {
            // Se já está no máximo, volta ao normal
            if (estadoAtual.scaleFactor >= 1.5) {
                estadoAtual.scaleFactor = 1;
            } else {
                estadoAtual.scaleFactor = Math.min(
                    Math.round((estadoAtual.scaleFactor + 0.1) * 10) / 10, 
                    1.5
                );
            }
        } else if (acao === '-') {
            // Se já está no mínimo, volta ao normal
            if (estadoAtual.scaleFactor <= 0.8) {
                estadoAtual.scaleFactor = 1;
            } else {
                estadoAtual.scaleFactor = Math.max(
                    Math.round((estadoAtual.scaleFactor - 0.1) * 10) / 10, 
                    0.8
                );
            }
        } else if (acao === 'reset') {
            estadoAtual.scaleFactor = 1;
        }
        
        aplicarEstado();
        salvarPreferencias();
        atualizarDescricaoFonte();
        
        console.log('[Acessibilidade] Fonte ajustada:', estadoAtual.scaleFactor);
    }

    function atualizarDescricaoFonte() {
        const descricoes = document.querySelectorAll('[data-opcao^="fonte-"] .opcao-acessibilidade_descricao');
        descricoes.forEach(desc => {
            let texto = 'Tamanho: ';
            if (estadoAtual.scaleFactor > 1) {
                const porcentagem = Math.round((estadoAtual.scaleFactor - 1) * 100);
                texto += `+${porcentagem}%`;
            } else if (estadoAtual.scaleFactor < 1) {
                const porcentagem = Math.round((1 - estadoAtual.scaleFactor) * 100);
                texto += `-${porcentagem}%`;
            } else {
                texto += 'Normal';
            }
            desc.textContent = texto;
        });
    }

    function aplicarFiltroDaltonismo(tipo) {
        estadoAtual.filtroDaltonismo = tipo;
        aplicarEstado();
        salvarPreferencias();
        atualizarUIParaEstadoAtual();
    }

    function aplicarFiltroDaltonismoCSS(tipo) {
        // Remove filtros anteriores do BODY E MAIN
        document.body.classList.remove('filtro-protanopia', 'filtro-deuteranopia', 'filtro-tritanopia');
        
        // Aplica filtro no MAIN em vez do body para não afetar o painel fixo
        const mains = document.querySelectorAll('main');
        mains.forEach(main => {
            main.classList.remove('filtro-protanopia', 'filtro-deuteranopia', 'filtro-tritanopia');
            if (tipo !== 'none') {
                main.classList.add(`filtro-${tipo}`);
            }
        });
        
        // Exclui marquee de patrocinadores dos filtros (logos devem manter cores originais)
        const marquees = document.querySelectorAll('.secao-patrocinadores, .marquee, .marquee_track');
        marquees.forEach(marquee => {
            marquee.classList.remove('filtro-protanopia', 'filtro-deuteranopia', 'filtro-tritanopia');
        });
        
        // Marca no body para referência (sem aplicar filtro)
        if (tipo !== 'none') {
            document.body.setAttribute('data-filtro-daltonismo', tipo);
            document.body.classList.add('filtros-ativos'); // Ativa otimizações (remove shadows)
        } else {
            document.body.removeAttribute('data-filtro-daltonismo');
            document.body.classList.remove('filtros-ativos'); // Remove otimizações
        }
    }

    function resetarTudo() {
        console.log('[Acessibilidade] Resetando todas as configurações...');
        
        estadoAtual = {
            tema: detectarTemaDoSistema(),
            contraste: false,
            scaleFactor: 1,
            filtroDaltonismo: 'none'
        };
        
        aplicarEstado();
        salvarPreferencias();
        atualizarUIParaEstadoAtual();
        
        console.log('[Acessibilidade] Configurações resetadas para:', estadoAtual);
    }

    // Carrega preferências ao iniciar
    carregarPreferencias();

    // Injeta filtros SVG para daltonismo
    function injetarFiltrosSVG() {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('style', 'position: absolute; width: 0; height: 0;');
        svg.setAttribute('aria-hidden', 'true');
        
        svg.innerHTML = `
            <defs>
                <!-- Protanopia (Deficiência de VERMELHO) - Matriz ajustada -->
                <filter id="protanopia-filter" color-interpolation-filters="linearRGB">
                    <feColorMatrix type="matrix" values="
                        0.56667, 0.43333, 0,      0, 0
                        0.55833, 0.44167, 0,      0, 0
                        0,       0.24167, 0.75833, 0, 0
                        0,       0,       0,       1, 0"/>
                </filter>
                
                <!-- Deuteranopia (Deficiência de VERDE) - Matriz mais diferenciada -->
                <filter id="deuteranopia-filter" color-interpolation-filters="linearRGB">
                    <feColorMatrix type="matrix" values="
                        0.625,  0.375,  0,      0, 0
                        0.7,    0.3,    0,      0, 0
                        0,      0.3,    0.7,    0, 0
                        0,      0,      0,      1, 0"/>
                </filter>
                
                <!-- Tritanopia (Deficiência de AZUL) - Mantida -->
                <filter id="tritanopia-filter" color-interpolation-filters="linearRGB">
                    <feColorMatrix type="matrix" values="
                        0.95,  0.05,  0,      0, 0
                        0,     0.433, 0.567,  0, 0
                        0,     0.475, 0.525,  0, 0
                        0,     0,     0,      1, 0"/>
                </filter>
            </defs>
        `;
        
        document.body.insertBefore(svg, document.body.firstChild);
    }

    injetarFiltrosSVG();

    // Troca o mascote para a versão branca quando o tema estiver em modo escuro.
    // Compatível com as páginas que usam a classe .FMPConnect_mascote e <img src=".../fmpconnect.svg">.
    (function () {
        function updateMascoteForTheme() {
            try {
                const root = document.documentElement;
                const body = document.body;
                const themeAttr = root.getAttribute('data-theme') || body.getAttribute('data-theme');
                const isDark = themeAttr === 'dark' || (!themeAttr && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);

                document.querySelectorAll('.FMPConnect_mascote img').forEach(img => {
                    if (!img || !img.src) return;

                        // Se a URL já referencia uma das versões do mascote, substitui pelo nome correto
                        const match = img.src.match(/fmpconnect(?:-branco)?\.svg/);
                        if (match) {
                            const desired = isDark ? 'fmpconnect-branco.svg' : 'fmpconnect.svg';
                            if (!img.src.includes(desired)) {
                                img.src = img.src.replace(/fmpconnect(?:-branco)?\.svg/, desired);
                            }
                            return;
                        }

                        // Fallback: troca apenas o último segmento do path para o arquivo desejado
                        try {
                            const parts = img.src.split('/');
                            parts[parts.length - 1] = isDark ? 'fmpconnect-branco.svg' : 'fmpconnect.svg';
                            img.src = parts.join('/');
                        } catch (e) {
                            // não faz nada se não for possível modificar
                        }
                });
            } catch (e) {
                // não interrompe execução
            }
        }

        // Atualiza no carregamento do DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', updateMascoteForTheme);
        } else {
            updateMascoteForTheme();
        }

        // Observa mudanças no atributo data-theme para alternar dinamicamente
        try {
            const observer = new MutationObserver(mutations => {
                for (const m of mutations) {
                    if (m.type === 'attributes' && (m.attributeName === 'data-theme')) {
                        updateMascoteForTheme();
                        break;
                    }
                }
            });
            observer.observe(document.documentElement, { attributes: true });
        } catch (e) {
            // browsers antigos podem falhar aqui
        }
    })();

    // Atualiza logos de patrocinadores conforme o tema (troca para versões brancas no modo escuro)
    (function () {
        function updateSponsorLogosForTheme() {
            try {
                const root = document.documentElement;
                const body = document.body;
                const themeAttr = root.getAttribute('data-theme') || body.getAttribute('data-theme');
                const isDark = themeAttr === 'dark' || (!themeAttr && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);

                // Seleciona imagens de patrocinadores (áreas de patrocinadores / marquee)
                const imgs = document.querySelectorAll('.secao-patrocinadores img, .marquee img, .marquee_track img');
                imgs.forEach(img => {
                    if (!img || !img.src) return;

                    // Guarda o src original (colorido) para restaurar posteriormente
                    if (!img.dataset.originalSrc) img.dataset.originalSrc = img.src;
                    const original = img.dataset.originalSrc;

                    if (!isDark) {
                        // No modo claro, restaura a versão original colorida
                        if (img.src !== original) img.src = original;
                        return;
                    }

                    // Modo escuro: tenta carregar uma versão branca equivalente
                    // Possíveis sufixos: -branco, -white, _white
                    const trySuffixes = ['-branco', '-white', '_white'];
                    // Resolve path components
                    try {
                        const url = new URL(original, location.href);
                        const pathParts = url.pathname.split('/');
                        const file = pathParts.pop();
                        const m = file.match(/(.+)(\.[a-zA-Z0-9]+)$/);
                        if (!m) return;
                        const name = m[1];
                        const ext = m[2];

                        let tried = 0;
                        const tryNext = () => {
                            if (tried >= trySuffixes.length) {
                                // Nenhuma variante branca encontrada — mantém a original
                                return;
                            }
                            const candidateFile = name + trySuffixes[tried] + ext;
                            const candidatePath = pathParts.concat([candidateFile]).join('/');
                            const candidateUrl = url.origin + candidatePath;

                            const testImg = new Image();
                            testImg.onload = function () {
                                // Substitui apenas se o carregamento foi bem-sucedido
                                img.src = candidateUrl;
                                img.dataset.currentVariant = candidateFile;
                            };
                            testImg.onerror = function () {
                                tried += 1;
                                tryNext();
                            };
                            // Tenta carregar sem cache-buster — se houver cache problemático, podemos adicionar depois
                            testImg.src = candidateUrl;
                        };

                        // Se já estiver apontando para uma variante branca correta, não faz nada
                        if (/fmpconnect(?:-branco|-white|_white)?\.svg/.test(img.src) || /.+(?:-branco|-white|_white)\.[a-zA-Z0-9]+$/.test(img.src)) {
                            return;
                        }

                        tryNext();
                    } catch (e) {
                        // Se URL falhar, ignora
                    }
                });
            } catch (e) {
                // não interrompe execução
            }
        }

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', updateSponsorLogosForTheme);
        } else {
            updateSponsorLogosForTheme();
        }

        // Observa mudanças no atributo data-theme para alternar dinamicamente
        try {
            const observer = new MutationObserver(mutations => {
                for (const m of mutations) {
                    if (m.type === 'attributes' && (m.attributeName === 'data-theme')) {
                        updateSponsorLogosForTheme();
                        break;
                    }
                }
            });
            observer.observe(document.documentElement, { attributes: true });
        } catch (e) {
            // browsers antigos podem falhar aqui
        }
    })();

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', carregarPainelAcessibilidade);
    } else {
        carregarPainelAcessibilidade();
    }

    // Observa mudanças na preferência do sistema
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (e) => {
            // Só atualiza se o usuário não tiver uma preferência salva explícita
            const saved = localStorage.getItem(STORAGE_KEY);
            if (!saved || !JSON.parse(saved).tema) {
                estadoAtual.tema = e.matches ? 'claro' : 'escuro';
                aplicarEstado();
                atualizarUIParaEstadoAtual();
            }
        });
    }

    window.Acessibilidade = {
        abrir: () => {
            const painel = document.getElementById('painelAcessibilidade');
            if (painel) {
                painel.classList.add('ativo');
                try { localStorage.setItem(PAINEL_OPEN_KEY, '1'); } catch (e) { /* ignore */ }
            }
        },
        fechar: () => {
            const painel = document.getElementById('painelAcessibilidade');
            if (painel) {
                painel.classList.remove('ativo');
                try { localStorage.removeItem(PAINEL_OPEN_KEY); } catch (e) { /* ignore */ }
            }
        },
        getEstado: () => estadoAtual,
        setTema: (tema) => alterarTema(tema)
    };
})();
