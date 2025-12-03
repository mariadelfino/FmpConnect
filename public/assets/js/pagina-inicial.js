/**
 * Controle do Carrossel de Dúvidas - Página Inicial
 */

(function() {
    'use strict';

    const carrossel = document.getElementById('carrosselDuvidas');
    const setaEsquerda = document.querySelector('.carrossel-seta--esquerda');
    const setaDireita = document.querySelector('.carrossel-seta--direita');
    const indicadores = document.querySelectorAll('.indicador');

    if (!carrossel || !setaEsquerda || !setaDireita) return;

    const scrollAmount = 300;
    let currentPage = 0;
    const totalPages = indicadores.length;

    function atualizarSetas() {
        const isInicio = carrossel.scrollLeft <= 10;
        const isFim = carrossel.scrollLeft + carrossel.clientWidth >= carrossel.scrollWidth - 10;

        setaEsquerda.classList.toggle('oculto', isInicio);
        setaDireita.classList.toggle('oculto', isFim);
    }

    function atualizarIndicadores() {
        const scrollPercentage = carrossel.scrollLeft / (carrossel.scrollWidth - carrossel.clientWidth);
        const newPage = Math.round(scrollPercentage * (totalPages - 1));

        if (newPage !== currentPage) {
            indicadores[currentPage].classList.remove('ativo');
            indicadores[newPage].classList.add('ativo');
            currentPage = newPage;
        }
    }

    function scrollParaEsquerda() {
        carrossel.scrollBy({
            left: -scrollAmount,
            behavior: 'smooth'
        });
    }

    function scrollParaDireita() {
        carrossel.scrollBy({
            left: scrollAmount,
            behavior: 'smooth'
        });
    }

    function scrollParaPagina(index) {
        const scrollPerPage = (carrossel.scrollWidth - carrossel.clientWidth) / (totalPages - 1);
        carrossel.scrollTo({
            left: scrollPerPage * index,
            behavior: 'smooth'
        });
    }

    setaEsquerda.addEventListener('click', scrollParaEsquerda);
    setaDireita.addEventListener('click', scrollParaDireita);

    indicadores.forEach((indicador, index) => {
        indicador.addEventListener('click', () => scrollParaPagina(index));
    });

    carrossel.addEventListener('scroll', () => {
        atualizarSetas();
        atualizarIndicadores();
    });

    window.addEventListener('resize', atualizarSetas);

    atualizarSetas();
    
    const CHATBOT_BASE_URL = 'chat.html';
    const duvidaButtons = document.querySelectorAll('.secao-duvidas .duvida-btn');

    duvidaButtons.forEach(button => {
        button.addEventListener('click', function() {
            const pergunta = this.getAttribute('data-question');

            if (pergunta) {
                const perguntaCodificada = encodeURIComponent(pergunta);
                const urlDeRedirecionamento = `${CHATBOT_BASE_URL}?pergunta=${perguntaCodificada}`;
                window.location.href = urlDeRedirecionamento;
            }
        });
    });
})();
