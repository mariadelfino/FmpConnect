/* ========================================
   Página de Voz - Controller (UI apenas)
   Responsabilidades:
   - Controlar interações da UI
   - Gerenciar animações visuais
   - Delegar lógica de áudio para GeminiService
   ======================================== */

import GeminiService from './services/gemini-service.js';

(function() {
    'use strict';

    // ========================================
    // Elementos do DOM
    // ========================================
    
    const botaoMicrofone = document.getElementById('botaoMicrofone');
    const indicadorAudio = document.getElementById('indicadorAudio');
    const statusGravacao = document.getElementById('statusGravacao');
    const botaoVoltar = document.querySelector('.botao-voltar');
    const botaoAcessibilidade = document.querySelector('.botao-acessibilidade');

    // ========================================
    // Serviço Gemini
    // ========================================
    
    const geminiService = new GeminiService();
    
    // Configura callbacks
    geminiService.onStatusChange = atualizarStatus;
    geminiService.onError = mostrarErro;
    geminiService.onAudioReceived = (duracao) => {
        // Futuramente: animar aurora pulsante aqui
        console.log('Áudio recebido, duração:', duracao);
    };

    // ========================================
    // Estado da UI
    // ========================================
    
    let estaGravando = false;

    // ========================================
    // Inicialização
    // ========================================
    
    async function inicializar() {
        // Event listeners
        botaoMicrofone.addEventListener('click', alternarGravacao);
        botaoVoltar.addEventListener('click', voltarParaInicio);
        botaoAcessibilidade.addEventListener('click', abrirAcessibilidade);

        // Inicializa sessão Gemini
        atualizarStatus('Inicializando...');
        await geminiService.inicializarSessao();
    }

    // ========================================
    // Controles de Gravação
    // ========================================
    
    async function alternarGravacao() {
        if (estaGravando) {
            pararGravacao();
        } else {
            await iniciarGravacao();
        }
    }

    async function iniciarGravacao() {
        const sucesso = await geminiService.iniciarGravacao();
        
        if (sucesso) {
            estaGravando = true;
            botaoMicrofone.classList.add('gravando');
            indicadorAudio.classList.add('ativo');
        }
    }

    function pararGravacao() {
        geminiService.pararGravacao();
        
        estaGravando = false;
        botaoMicrofone.classList.remove('gravando');
        indicadorAudio.classList.remove('ativo');
    }

    // ========================================
    // Navegação
    // ========================================
    
    function voltarParaInicio() {
        // Para gravação se estiver ativa
        if (estaGravando) {
            pararGravacao();
        }
        
        // Volta para index.html
        window.location.href = './index.html';
    }

    function abrirAcessibilidade() {
        // Futuramente: abrir modal de acessibilidade
        console.log('Abrir painel de acessibilidade');
        alert('Painel de acessibilidade em desenvolvimento!');
    }

    // ========================================
    // Feedback Visual
    // ========================================
    
    function atualizarStatus(mensagem) {
        statusGravacao.textContent = mensagem;
        statusGravacao.style.color = '';
    }

    function mostrarErro(mensagem) {
        statusGravacao.textContent = mensagem;
        statusGravacao.style.color = 'rgba(239, 68, 68, 0.9)';
        
        setTimeout(() => {
            atualizarStatus('Toque para falar');
        }, 3000);
    }

    // ========================================
    // Inicialização da Página
    // ========================================
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializar);
    } else {
        inicializar();
    }

})();

