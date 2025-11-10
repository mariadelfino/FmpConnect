/* ========================================
   Gemini Service - Camada de Serviço
   Responsabilidades:
   - Buscar token e configurações do backend
   - Conectar com Gemini Live API
   - Processar áudio (encode/decode)
   - Gerenciar sessão e callbacks
   ======================================== */

import { GoogleGenAI, Modality } from '@google/genai';

class GeminiService {
    constructor() {
        // URLs do backend - usa o mesmo host do frontend
        const backendHost = window.location.hostname; // 127.0.0.1 ou localhost
        this.BACKEND_URL = `http://${backendHost}:5000`;
        this.TOKEN_URL = `${this.BACKEND_URL}/token`;
        this.CONFIG_URL = `${this.BACKEND_URL}/config`;
        
        console.log('🔗 Backend URL:', this.BACKEND_URL);
        
        // Configurações (virão do backend)
        this.config = null;
        
        // Estado
        this.session = null;
        this.isRecording = false;
        this.mediaStream = null;
        this.sourceNode = null;
        this.scriptProcessorNode = null;
        
        // Contextos de áudio
        this.inputAudioContext = new AudioContext({ sampleRate: 16000 });
        this.outputAudioContext = new AudioContext({ sampleRate: 24000 });
        this.nextStartTime = 0;
        this.sources = new Set();
        
        // Callbacks (serão configurados externamente)
        this.onStatusChange = null;
        this.onError = null;
        this.onAudioReceived = null;
    }

    /**
     * Inicializa a sessão
     */
    async inicializarSessao() {
        try {
            this._atualizarStatus('Carregando configurações...');
            
            // 1. Busca configurações do backend
            const configResponse = await fetch(this.CONFIG_URL);
            if (!configResponse.ok) {
                throw new Error('Falha ao buscar configurações');
            }
            this.config = await configResponse.json();
            
            this._atualizarStatus('Buscando token de acesso...');
            
            // 2. Busca token do backend
            const tokenResponse = await fetch(this.TOKEN_URL);
            if (!tokenResponse.ok) {
                throw new Error('Falha ao buscar token');
            }

            const tokenData = await tokenResponse.json();
            if (tokenData.error) {
                throw new Error(tokenData.error);
            }

            this._atualizarStatus('Token recebido. Conectando...');

            // 3. Inicializa cliente Gemini com configurações do backend
            const ai = new GoogleGenAI({
                apiKey: tokenData.token,
                httpOptions: { apiVersion: this.config.apiVersion }
            });

            // 4. Conecta à sessão Live
            this.session = await ai.live.connect({
                model: this.config.model,
                callbacks: {
                    onopen: () => this._atualizarStatus('Sessão aberta!'),
                    onmessage: (msg) => this._handleMessage(msg),
                    onerror: (e) => this._handleError(e.message),
                    onclose: (e) => this._atualizarStatus(`Sessão fechada: ${e.reason}`),
                },
                config: {
                    systemInstruction: this.config.systemInstruction,
                    responseModalities: [Modality.AUDIO],
                    speechConfig: {
                        voiceConfig: { 
                            prebuiltVoiceConfig: { voiceName: this.config.voiceName }
                        },
                    },
                },
            });

            this.nextStartTime = this.outputAudioContext.currentTime;
            this._atualizarStatus('Pronto! Toque para falar');
            
            return true;
        } catch (error) {
            this._handleError(`Erro ao iniciar sessão: ${error.message}`);
            return false;
        }
    }

    /**
     * Inicia a gravação de áudio
     */
    async iniciarGravacao() {
        if (this.isRecording || !this.session) return false;

        this.inputAudioContext.resume();
        this._atualizarStatus('Pedindo permissão do microfone...');

        try {
            // Captura áudio do microfone
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                },
                video: false,
            });

            this._atualizarStatus('Ouvindo...');

            // Processa áudio
            this.sourceNode = this.inputAudioContext.createMediaStreamSource(this.mediaStream);
            const bufferSize = 256;
            this.scriptProcessorNode = this.inputAudioContext.createScriptProcessor(
                bufferSize, 1, 1
            );

            // Envia chunks de áudio para o Gemini
            this.scriptProcessorNode.onaudioprocess = (event) => {
                if (!this.isRecording || !this.session) return;

                const pcmData = event.inputBuffer.getChannelData(0);

                try {
                    this.session.sendRealtimeInput({ 
                        media: this._createBlob(pcmData) 
                    });
                } catch (error) {
                    this._handleError(`Erro ao enviar áudio: ${error.message}`);
                    this.pararGravacao();
                }
            };

            this.sourceNode.connect(this.scriptProcessorNode);
            this.scriptProcessorNode.connect(this.inputAudioContext.destination);

            this.isRecording = true;
            return true;
        } catch (error) {
            this._handleError(`Erro ao gravar: ${error.message}`);
            this.pararGravacao();
            return false;
        }
    }

    /**
     * Para a gravação de áudio
     */
    pararGravacao() {
        if (!this.isRecording && !this.mediaStream) return;

        this._atualizarStatus('Parando gravação...');
        this.isRecording = false;

        // Desconecta nodes
        if (this.scriptProcessorNode && this.sourceNode) {
            this.scriptProcessorNode.disconnect();
            this.sourceNode.disconnect();
            this.scriptProcessorNode = null;
            this.sourceNode = null;
        }

        // Para stream do microfone
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach((track) => track.stop());
            this.mediaStream = null;
        }

        this._atualizarStatus('Toque para falar');
    }

    /**
     * Reinicia a sessão
     */
    async reiniciarSessao() {
        this.pararGravacao();
        
        if (this.session) {
            this.session.close();
        }
        
        // Para todos os áudios
        for (const source of this.sources.values()) {
            source.stop();
            this.sources.delete(source);
        }
        
        await this.inicializarSessao();
    }

    /**
     * Processa mensagens recebidas do Gemini
     * @private
     */
    async _handleMessage(message) {
        const audio = message.serverContent?.modelTurn?.parts[0]?.inlineData;

        if (audio) {
            // Garante sequência de áudio
            this.nextStartTime = Math.max(
                this.nextStartTime, 
                this.outputAudioContext.currentTime
            );

            // Decodifica áudio
            const audioBuffer = await this._decodeAudioData(
                this._decode(audio.data),
                this.outputAudioContext,
                24000,
                1
            );

            // Toca áudio
            const source = this.outputAudioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(this.outputAudioContext.destination);
            source.addEventListener('ended', () => {
                this.sources.delete(source);
            });
            source.start(this.nextStartTime);
            this.nextStartTime = this.nextStartTime + audioBuffer.duration;
            this.sources.add(source);

            // Callback para UI atualizar (aurora pulsante)
            if (this.onAudioReceived) {
                this.onAudioReceived(audioBuffer.duration);
            }
        }

        // Interrupção (usuário falou por cima)
        const interrupted = message.serverContent?.interrupted;
        if (interrupted) {
            for (const source of this.sources.values()) {
                source.stop();
                this.sources.delete(source);
            }
            this.nextStartTime = 0;
        }
    }

    /**
     * Cria blob de áudio PCM
     * @private
     */
    _createBlob(data) {
        const length = data.length;
        const int16 = new Int16Array(length);
        
        for (let i = 0; i < length; i++) {
            int16[i] = data[i] * 32768;
        }
        
        return {
            data: this._encode(new Uint8Array(int16.buffer)),
            mimeType: 'audio/pcm;rate=16000',
        };
    }

    /**
     * Decodifica áudio recebido
     * @private
     */
    async _decodeAudioData(data, ctx, sampleRate, numChannels) {
        const buffer = ctx.createBuffer(
            numChannels,
            data.length / 2 / numChannels,
            sampleRate
        );
        
        const dataInt16 = new Int16Array(data.buffer);
        const length = dataInt16.length;
        const dataFloat32 = new Float32Array(length);
        
        for (let i = 0; i < length; i++) {
            dataFloat32[i] = dataInt16[i] / 32768.0;
        }
        
        buffer.copyToChannel(dataFloat32, 0);
        return buffer;
    }

    /**
     * Encode base64
     * @private
     */
    _encode(bytes) {
        let binary = '';
        const length = bytes.byteLength;
        
        for (let i = 0; i < length; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        
        return btoa(binary);
    }

    /**
     * Decode base64
     * @private
     */
    _decode(base64) {
        const binaryString = atob(base64);
        const length = binaryString.length;
        const bytes = new Uint8Array(length);
        
        for (let i = 0; i < length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        
        return bytes;
    }

    /**
     * Atualiza status (callback)
     * @private
     */
    _atualizarStatus(mensagem) {
        if (this.onStatusChange) {
            this.onStatusChange(mensagem);
        }
    }

    /**
     * Trata erros (callback)
     * @private
     */
    _handleError(mensagem) {
        if (this.onError) {
            this.onError(mensagem);
        }
    }
}

export default GeminiService;
