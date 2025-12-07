document.addEventListener('DOMContentLoaded', () => {
    const carrossel = document.querySelector('.carrossel-horizontal');
    const prevButton = document.querySelector('.carrossel-botao.prev');
    const nextButton = document.querySelector('.carrossel-botao.next');

    if (!carrossel || !prevButton || !nextButton) {
        return;
    }

    let autoScrollInterval;

    const scrollNext = () => {
        const scrollAmount = carrossel.clientWidth;
        // Se está perto do fim, volta para o começo
        if (carrossel.scrollLeft + scrollAmount >= carrossel.scrollWidth - 1) {
            carrossel.scrollTo({ left: 0, behavior: 'smooth' });
        } else {
            carrossel.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        }
    };

    const scrollPrev = () => {
        const scrollAmount = carrossel.clientWidth;
        carrossel.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    };

    const startAutoScroll = () => {
        autoScrollInterval = setInterval(scrollNext, 4000);
    };

    const stopAutoScroll = () => {
        clearInterval(autoScrollInterval);
    };

    nextButton.addEventListener('click', () => {
        scrollNext();
        stopAutoScroll();
        startAutoScroll(); // Reinicia o timer
    });

    prevButton.addEventListener('click', () => {
        scrollPrev();
        stopAutoScroll();
        startAutoScroll(); // Reinicia o timer
    });

    // Inicia o carrossel automático
    startAutoScroll();
});
