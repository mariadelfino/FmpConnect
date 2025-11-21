import os
import json
import urllib.request
import urllib.error
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# --- CONFIGURAÇÕES GERAIS ---

try:
    API_KEY = os.environ["GOOGLE_API_KEY"]
except KeyError:
    print("❌ ERRO: GOOGLE_API_KEY não encontrada no .env")
    print("📝 Crie um arquivo .env com: GOOGLE_API_KEY=sua_chave_aqui")
    exit(1)

# Palavras-chave para filtro básico
COURSE_KEYWORDS = [
    'jovem programador', 'jovemprogramador', 'senac', 'senac\u00a0', 'jovem', 'programador', 'programação', 'programacao',
    'curso', 'inscri', 'matr', 'carga horária', 'carga horaria', 'dura', 'duração', 'duracao', 'certificado', 'pré-requisitos',
    'pre-requisitos', 'pre requisitos', 'conteúdo', 'conteudo', 'grade', 'horário', 'local', 'valor', 'preço', 'preco', 'público', 'publico'
]

# Configuração para o modo VOZ (WebSocket / Audio)
GEMINI_VOICE_CONFIG = {
    "model": "gemini-2.5-flash-native-audio-preview-09-2025",
    "systemInstruction": """Você é o Sena Chat, um assistente virtual amigável e prestativo do curso JOVEM PROGRAMADOR do SENAC.
    
Seu papel é:
- Ajudar estudantes com dúvidas sobre o curso e sobre programação
- Responder de forma clara, objetiva, cordial e profissional
- Ser motivador e educado
- Quando não souber algo, seja honesto e sugira onde encontrar a informação

Formatação:
- Ao responder, utilize formatação em Markdown quando for útil.
- NÃO remova os caracteres de Markdown (***, ###, etc.).
- Evite retornar HTML cru; prefira Markdown.

Responda sempre em tom amigável e direto.""",
    "voiceName": "Orus", 
    "apiVersion": "v1alpha"
}

# Configuração para o modo TEXTO (Chat tradicional)
GEMINI_TEXT_CONFIG = {
    "model": "gemini-2.0-flash",
    "systemInstruction": """Você é o SenaChat, um assistente virtual amigável e prestativo do SENAC - JOVEM PROGRAMADOR. 
    
Seu papel é:
- Ajudar estudantes com dúvidas sobre o curso e sobre programação
- Responder de forma clara, objetiva, cordial e profissional
- Ser motivador e educado

Formatação:
- Use Markdown para formatar suas respostas.
- NÃO remova ou proíba o uso de caracteres de Markdown.

Responda sempre de forma organizada, amigável e em Markdown.""",
}
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- FUNÇÕES AUXILIARES ---

def is_related_to_course(prompt_text: str) -> bool:
    """Filtra perguntas fora do escopo usando palavras-chave."""
    if not prompt_text:
        return False
    txt = prompt_text.lower()
    for kw in COURSE_KEYWORDS:
        if kw in txt:
            return True
    return False

# --- ROTAS DO SISTEMA (STATUS) ---

@app.route('/', methods=['GET'])
def home():
    """Status do servidor unificado."""
    return jsonify({
        "status": "online",
        "service": "SenaChat Backend Unificado (Voz + Texto)",
        "port": 5000,
        "endpoints_voz": ["/token", "/config"],
        "endpoints_texto": ["/text/token", "/text/config", "/text/chat"]
    })

@app.route('/public/<path:filename>')
def serve_public(filename):
    return send_from_directory('public', filename)

# --- ROTAS DE VOZ (Frontend de Áudio) ---

@app.route('/token', methods=['GET'])
def get_voice_token():
    """Retorna API Key para o frontend de Voz."""
    try:
        print("✅ [Voz] API Key solicitada")
        return jsonify({"token": API_KEY})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/config', methods=['GET'])
def get_voice_config():
    """Retorna configurações para o frontend de Voz."""
    try:
        print("📋 [Voz] Configurações enviadas")
        return jsonify(GEMINI_VOICE_CONFIG)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ROTAS DE TEXTO (Frontend de Chat) ---

@app.route('/text/token', methods=['GET'])
def get_text_token():
    """Retorna API Key para o frontend de Texto."""
    try:
        print("✅ [Texto] API Key solicitada")
        return jsonify({"token": API_KEY})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/text/config', methods=['GET'])
def get_text_config():
    """Retorna configurações para o frontend de Texto."""
    try:
        print("📋 [Texto] Configurações enviadas")
        return jsonify(GEMINI_TEXT_CONFIG)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/text/chat', methods=['POST'])
def text_chat():
    """Processa o chat de texto usando gemini-2.0-flash via generateContent."""
    try:
        data = request.get_json(force=True)
        prompt = data.get('prompt') if isinstance(data, dict) else None

        if not prompt:
            return jsonify({"error": "Campo 'prompt' é obrigatório"}), 400

        # Validação de escopo (Sua lógica original)

        # Pega o modelo correto (gemini-2.0-flash)
        model = GEMINI_TEXT_CONFIG.get('model')
        
        # --- MUDANÇA CRÍTICA: URL e JSON para Gemini 2.0 ---
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
        
        # Estrutura exigida pelo Gemini
        body = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            # Se quiser passar instruções de sistema no payload também (opcional, mas recomendado se a config acima não for pega automaticamente pelo modelo via API)
            "systemInstruction": {
                "parts": [{"text": GEMINI_TEXT_CONFIG["systemInstruction"]}]
            }
        }
        
        jsondata = json.dumps(body).encode('utf-8')
        req = urllib.request.Request(url, data=jsondata, method='POST')
        req.add_header('Content-Type', 'application/json; charset=utf-8')

        print(f"📡 [Texto] Chamando {model}...")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_body = resp.read()
                resp_json = json.loads(resp_body.decode('utf-8'))
                
                answer = None
                # Extração da resposta padrão do Gemini
                try:
                    if 'candidates' in resp_json and len(resp_json['candidates']) > 0:
                        answer = resp_json['candidates'][0]['content']['parts'][0]['text']
                except Exception:
                    pass

                if answer:
                    print("✅ [Texto] Resposta gerada com sucesso")
                    return jsonify({"answer": answer})
                else:
                    print("⚠️ [Texto] Resposta vazia ou formato inesperado")
                    return jsonify({"error": "Resposta vazia do modelo", "raw": resp_json}), 502

        except urllib.error.HTTPError as e:
            error_content = e.read().decode('utf-8')
            print(f"❌ [Texto] Erro {e.code}: {error_content}")
            return jsonify({"answer": "Erro técnico na IA.", "error": str(e), "details": error_content}), 500

    except Exception as e:
        print(f"❌ [Texto] Erro crítico: {e}")
        return jsonify({"error": str(e)}), 500
    

@app.route('/text/diag', methods=['GET'])
def text_diag():
    """Teste rápido de conexão com a API."""
    try:
        model = GEMINI_TEXT_CONFIG.get('model')
        url = f"https://generativelanguage.googleapis.com/v1beta2/models/{model}:generateText?key={API_KEY}"
        body = json.dumps({"prompt": {"text": "Oi"}, "maxOutputTokens": 5}).encode('utf-8')
        req = urllib.request.Request(url, data=body, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            return jsonify({"ok": True, "code": resp.getcode()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 SenaChat Backend UNIFICADO (Voz + Texto)")
    print("="*50)
    print("📡 Servidor rodando em: http://localhost:5000")
    print("🔑 Endpoints Voz: /token, /config")
    print("💬 Endpoints Texto: /text/token, /text/config, /text/chat")
    print("="*50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)