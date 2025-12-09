/**
 * Controle de Animação da Áurea FMPConnect
 * Ativa animações quando detecta áudio do bot falando (Web Audio API)
 */

(function() {
    'use strict';

    const aureaFMPConnect = document.querySelector('.aurea-fmpconnect');
    
    if (!aureaFMPConnect) {
        console.error('[ÁUREA] Elemento .aurea-fmpconnect não encontrado');
        return;
    }

    // Web Audio API - Análise de Áudio    
    let audioContext = null;
    let analyser = null;
    let dataArray = null;
    let audioSource = null;
    let animationFrameId = null;
    let estaAtivo = false;
    let jaTevePrimeiraAtivacao = false;
    let frameCount = 0;
    let timeoutDesativacao = null;
    const DELAY_DESATIVACAO = 300;

    function inicializarAudioAnalyser() {
        if (audioContext) return;

        try {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 256;
            analyser.smoothingTimeConstant = 0.8;
            
            const bufferLength = analyser.frequencyBinCount;
            dataArray = new Uint8Array(bufferLength);
        } catch (error) {
            console.error('[ÁUREA] Erro ao inicializar Audio Analyser:', error);
        }
    }

    function conectarAudio(audioElement) {
        if (!audioContext || !analyser) {
            inicializarAudioAnalyser();
        }

        try {
            if (audioContext.state === 'suspended') {
                audioContext.resume();
            }

            if (audioSource) {
                audioSource.disconnect();
            }

            audioSource = audioContext.createMediaElementSource(audioElement);
            audioSource.connect(analyser);
            analyser.connect(audioContext.destination);
            
            iniciarMonitoramento();
        } catch (error) {
            console.error('[ÁUREA] Erro ao conectar áudio:', error);
        }
    }

    function monitorarAudio() {
        if (!analyser || !dataArray) return;

        analyser.getByteFrequencyData(dataArray);

        let soma = 0;
        const numFrequencias = 20;
        for (let i = 0; i < numFrequencias; i++) {
            soma += dataArray[i];
        }
        const volumeMedio = soma / numFrequencias;

        const THRESHOLD = 30;
        
        if (volumeMedio > THRESHOLD) {
            if (timeoutDesativacao) {
                clearTimeout(timeoutDesativacao);
                timeoutDesativacao = null;
            }
            
            if (!estaAtivo) {
                ativarAurea();
                estaAtivo = true;
                jaTevePrimeiraAtivacao = true;
            }
        } else {
            if (estaAtivo && !timeoutDesativacao) {
                timeoutDesativacao = setTimeout(() => {
                    pausarAurea();
                    estaAtivo = false;
                    timeoutDesativacao = null;
                }, DELAY_DESATIVACAO);
            }
        }

        animationFrameId = requestAnimationFrame(monitorarAudio);
    }

    function iniciarMonitoramento() {
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
        }
        frameCount = 0;
        monitorarAudio();
    }

    function pararMonitoramento() {
        if (timeoutDesativacao) {
            clearTimeout(timeoutDesativacao);
            timeoutDesativacao = null;
        }
        
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }
        
        if (jaTevePrimeiraAtivacao) {
            pausarAurea();
        } else {
            desativarAurea();
        }
        estaAtivo = false;
    }

    function ativarAurea() {
        aureaFMPConnect.classList.remove('pausado');
        aureaFMPConnect.classList.add('ativo');
    }

    function pausarAurea() {
        if (jaTevePrimeiraAtivacao) {
            aureaFMPConnect.classList.remove('ativo');
            aureaFMPConnect.classList.add('pausado');
        } else {
            desativarAurea();
        }
    }

    function desativarAurea() {
        aureaFMPConnect.classList.remove('ativo', 'pausado');
    }

    const observadorAudio = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.tagName === 'AUDIO') {
                    configurarElementoAudio(node);
                } else if (node.querySelector) {
                    const audioElement = node.querySelector('audio');
                    if (audioElement) {
                        configurarElementoAudio(audioElement);
                    }
                }
            });
        });
    });

    function configurarElementoAudio(audioElement) {
        audioElement.addEventListener('play', () => {
            conectarAudio(audioElement);
        });
        
        audioElement.addEventListener('ended', () => {
            pararMonitoramento();
        });
        
        audioElement.addEventListener('pause', () => {
            pararMonitoramento();
        });

        audioElement.addEventListener('error', (e) => {
            console.error('[ÁUREA] Erro no elemento de áudio:', e);
        });
    }

    observadorAudio.observe(document.body, {
        childList: true,
        subtree: true
    });

    const audiosExistentes = document.querySelectorAll('audio');
    audiosExistentes.forEach((audio) => {
        configurarElementoAudio(audio);
    });
    window.AureaAnimacao = {
        conectarAudioContext: (audioCtx, service = null) => {
            if (!audioCtx || !(audioCtx instanceof AudioContext)) {
                console.error('[ÁUREA] AudioContext inválido');
                return;
            }

            try {
                audioContext = audioCtx;
                
                analyser = audioContext.createAnalyser();
                analyser.fftSize = 256;
                analyser.smoothingTimeConstant = 0.8;
                
                const bufferLength = analyser.frequencyBinCount;
                dataArray = new Uint8Array(bufferLength);

                if (service && typeof service.registrarAnalyser === 'function') {
                    service.registrarAnalyser(analyser);
                }

                iniciarMonitoramento();
            } catch (error) {
                console.error('[ÁUREA] Erro ao conectar AudioContext:', error);
            }
        },

        conectarAudio: (audioElement) => {
            if (audioElement && audioElement.tagName === 'AUDIO') {
                conectarAudio(audioElement);
            }
        },

        inicializar: () => {
            inicializarAudioAnalyser();
        },

        parar: () => {
            pararMonitoramento();
        },

        estaAtivo: () => {
            return estaAtivo;
        },

        ativar: () => {
            ativarAurea();
        },

        desativar: () => {
            desativarAurea();
        }
    };
})();
