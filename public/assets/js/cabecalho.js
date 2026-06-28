(function () {
    'use strict';

    var menuBtn    = document.querySelector('.cabecalho__menu-btn');
    var menuMobile = document.querySelector('.cabecalho__menu-mobile');

    if (!menuBtn || !menuMobile) return;

    menuBtn.addEventListener('click', function () {
        menuMobile.classList.contains('aberto') ? fecharMenu() : abrirMenu();
    });

    function abrirMenu() {
        menuMobile.classList.add('aberto');
        menuBtn.setAttribute('aria-expanded', 'true');
        menuBtn.setAttribute('aria-label', 'Fechar menu de navegação');
        menuMobile.removeAttribute('aria-hidden');
        document.addEventListener('click', fecharAoClicarFora, true);
        document.addEventListener('keydown', fecharAoPressEsc);
    }

    function fecharMenu() {
        menuMobile.classList.remove('aberto');
        menuBtn.setAttribute('aria-expanded', 'false');
        menuBtn.setAttribute('aria-label', 'Abrir menu de navegação');
        menuMobile.setAttribute('aria-hidden', 'true');
        document.removeEventListener('click', fecharAoClicarFora, true);
        document.removeEventListener('keydown', fecharAoPressEsc);
    }

    function fecharAoClicarFora(e) {
        var cabecalho = document.querySelector('.cabecalho');
        if (cabecalho && !cabecalho.contains(e.target)) {
            fecharMenu();
        }
    }

    function fecharAoPressEsc(e) {
        if (e.key === 'Escape') {
            fecharMenu();
            menuBtn.focus();
        }
    }
}());
