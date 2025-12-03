(function() {
    'use strict';
    const botaoIniciar = document.getElementById('botaoIniciar');
    
    function irParaPaginaInicial() {
        botaoIniciar.classList.add('botao-iniciar-completado');
        setTimeout(() => {
            window.location.href = './paginainicial.html';
        }, 300);
    }
    
    function inicializar() {
        if (!botaoIniciar) {
            console.error('Botão iniciar não encontrado!');
            return;
        }
        botaoIniciar.addEventListener('click', irParaPaginaInicial);
        botaoIniciar.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                irParaPaginaInicial();
            }
        });
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializar);
    } else {
        inicializar();
    }
})();
