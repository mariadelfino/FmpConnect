/* ========================================
   Modal de Boas-vindas - Interatividade
   Controla o botão de arrastar no mobile
   e desktop
   ======================================== */

(function() {
    'use strict';

    // Elementos do DOM
    const modal = document.getElementById('modalBoasVindas');
    const botaoArrastar = document.getElementById('botaoArrastar');
    const botaoArrastarBotao = document.getElementById('botaoArrastarBotao');
    const trilho = botaoArrastar.querySelector('.botao-arrastar_trilho');

    // Variáveis de controle
    let estaArrastando = false;
    let posicaoInicialX = 0;
    let posicaoAtualX = 0;
    let foiCompletado = false;
    let ehDesktop = window.matchMedia('(min-width: 768px)').matches;

    // Constantes
    const LIMITE_CONCLUSAO = 0.8; // 80% do caminho
    const DELAY_FECHAR = 500; // Delay antes de fechar o modal (ms)

    /**
     * Inicializa os event listeners
     */
    function inicializar() {
        // Detecta mudanças de viewport
        const mediaQuery = window.matchMedia('(min-width: 768px)');
        mediaQuery.addEventListener('change', lidarComMudancaViewport);

        // Mobile - Touch events
        botaoArrastarBotao.addEventListener('touchstart', lidarComInicioToque, { passive: false });
        document.addEventListener('touchmove', lidarComMovimentoToque, { passive: false });
        document.addEventListener('touchend', lidarComFimToque);

        // Desktop e Mobile - Mouse events para arrastar
        botaoArrastarBotao.addEventListener('mousedown', lidarComInicioMouse);
        document.addEventListener('mousemove', lidarComMovimentoMouse);
        document.addEventListener('mouseup', lidarComFimMouse);
    }

    /**
     * Lida com mudanças de viewport
     */
    function lidarComMudancaViewport(e) {
        ehDesktop = e.matches;
    }

    /**
     * Touch Start Handler
     */
    function lidarComInicioToque(e) {
        if (foiCompletado) return;
        
        estaArrastando = true;
        posicaoInicialX = e.touches[0].clientX;
        // Desabilita apenas a transição do left para arrastar suave
        botaoArrastarBotao.style.transition = 'transform 250ms cubic-bezier(0.4, 0, 0.2, 1), box-shadow 250ms cubic-bezier(0.4, 0, 0.2, 1)';
    }

    /**
     * Touch Move Handler
     */
    function lidarComMovimentoToque(e) {
        if (!estaArrastando || foiCompletado) return;
        
        e.preventDefault();
        posicaoAtualX = e.touches[0].clientX;
        atualizarPosicaoBotao();
    }

    /**
     * Touch End Handler
     */
    function lidarComFimToque() {
        if (!estaArrastando || foiCompletado) return;
        
        estaArrastando = false;
        // Reativa todas as transições
        botaoArrastarBotao.style.transition = '';
        
        verificarConclusao();
    }

    /**
     * Mouse Down Handler
     */
    function lidarComInicioMouse(e) {
        if (foiCompletado) return;
        
        estaArrastando = true;
        posicaoInicialX = e.clientX;
        // Desabilita apenas a transição do left para arrastar suave
        botaoArrastarBotao.style.transition = 'transform 250ms cubic-bezier(0.4, 0, 0.2, 1), box-shadow 250ms cubic-bezier(0.4, 0, 0.2, 1)';
    }

    /**
     * Mouse Move Handler
     */
    function lidarComMovimentoMouse(e) {
        if (!estaArrastando || foiCompletado) return;
        
        e.preventDefault();
        posicaoAtualX = e.clientX;
        atualizarPosicaoBotao();
    }

    /**
     * Mouse End Handler
     */
    function lidarComFimMouse() {
        if (!estaArrastando || foiCompletado) return;
        
        estaArrastando = false;
        botaoArrastarBotao.style.transition = '';
        
        verificarConclusao();
    }

    /**
     * Atualiza a posição do botão durante o arraste
     */
    function atualizarPosicaoBotao() {
        const retanguloTrilho = trilho.getBoundingClientRect();
        const larguraBotao = botaoArrastarBotao.offsetWidth;
        const movimentoMaximo = retanguloTrilho.width - larguraBotao - 8; // 8px de margem
        
        let deltaX = posicaoAtualX - posicaoInicialX;
        deltaX = Math.max(0, Math.min(deltaX, movimentoMaximo));
        
        botaoArrastarBotao.style.left = `${4 + deltaX}px`;
    }

    /**
     * Verifica se o arraste completou o limite
     */
    function verificarConclusao() {
        const retanguloTrilho = trilho.getBoundingClientRect();
        const larguraBotao = botaoArrastarBotao.offsetWidth;
        const movimentoMaximo = retanguloTrilho.width - larguraBotao - 8;
        const deltaX = posicaoAtualX - posicaoInicialX;
        const progresso = deltaX / movimentoMaximo;
        
        if (progresso >= LIMITE_CONCLUSAO) {
            completarArraste();
        } else {
            // Volta para o início
            botaoArrastarBotao.style.left = '4px';
        }
    }

    /**
     * Completa o arraste e fecha o modal
     */
    function completarArraste() {
        if (foiCompletado) return;
        
        foiCompletado = true;
        
        // Move o botão para o final
        const retanguloTrilho = trilho.getBoundingClientRect();
        const larguraBotao = botaoArrastarBotao.offsetWidth;
        botaoArrastarBotao.style.left = `${retanguloTrilho.width - larguraBotao - 4}px`;
        
        // Adiciona classe de sucesso
        botaoArrastar.classList.add('botao-arrastar-completado');
        
        // Feedback visual e fecha modal
        setTimeout(() => {
            fecharModal();
        }, DELAY_FECHAR);
    }

    /**
     * Fecha o modal e mostra o conteúdo principal
     */
    function fecharModal() {
        modal.classList.add('modal-boas-vindas-fechando');
        
        setTimeout(() => {
            window.location.href = 'index.html'; // 🚀 A MÁGICA ACONTECE AQUI!
        }, 350)
    }

    // Inicializa quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializar);
    } else {
        inicializar();
    }

})();
