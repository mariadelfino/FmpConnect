import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

COURSE_KEYWORDS = [
    'jovem programador', 'jovemprogramador', 'senac', 'senac\u00a0', 'jovem', 'programador', 'programação', 'programacao',
    'curso', 'inscri', 'matr', 'carga horária', 'carga horaria', 'dura', 'duração', 'duracao', 'certificado', 'pré-requisitos',
    'pre-requisitos', 'pre requisitos', 'conteúdo', 'conteudo', 'grade', 'horário', 'local', 'valor', 'preço', 'preco', 'público', 'publico'
]

def is_related_to_course(prompt_text: str) -> bool:
    """Checa se o prompt parece estar relacionado ao curso Jovem Programador/SENAC.

    A checagem é intencionalmente simples (palavras-chave). Isso evita chamadas desnecessárias
    à API generative para perguntas fora do escopo.
    """
    if not prompt_text:
        return False
    txt = prompt_text.lower()
    for kw in COURSE_KEYWORDS:
        if kw in txt:
            return True
    return False

try:
    API_KEY = os.environ["GOOGLE_API_KEY"]
except KeyError:
    print("❌ ERRO: GOOGLE_API_KEY não encontrada no .env")
    print("📝 Crie um arquivo .env com: GOOGLE_API_KEY=sua_chave_aqui")
    exit(1)


GEMINI_CONFIG = {
    "model": "gemini-2.5-flash-native-audio-preview-09-2025",
    "systemInstruction": """Você é o Sena Chat, um assistente virtual amigável e prestativo do curso JOVEM PROGRAMADOR do SENAC.
    
Seu papel é:
- Ajudar estudantes com dúvidas sobre o curso e sobre programação
- Responder de forma clara, objetiva, cordial e profissional
- Ser motivador e educado
- Quando não souber algo, seja honesto e sugira onde encontrar a informação

Formatação:
- Ao responder, utilize formatação em Markdown quando for útil (títulos com #, listas com -, negrito com **, código com ``` e ``, etc.).
- NÃO remova os caracteres de Markdown (***, ###, etc.) — mantenha a formatação. O frontend renderizará o Markdown.
- Evite retornar HTML cru; prefira Markdown.

Responda sempre em tom amigável e direto, e mantenha as respostas organizadas usando Markdown.""",
    
    "voiceName": "Orus", 
    "apiVersion": "v1alpha"
}

GEMINI_TEXT_CONFIG = {
    "model": "gemini-2.0-flash",  
    "systemInstruction": """Você é o SenaChat, um assistente virtual amigável e prestativo do SENAC - JOVEM PROGRAMADOR. 
    
Seu papel é:
- Ajudar estudantes com dúvidas sobre o curso e sobre programação
- Responder de forma clara, objetiva e profissional
- **IMPORTANTE:** Se o usuário já iniciou a conversa, NÃO diga 'Olá' novamente. Vá direto ao ponto.
- Seja motivador e educado.

Formatação:
- Use Markdown para formatar suas respostas.
- NÃO remova ou proíba o uso de caracteres de Markdown.
- Evite enviar HTML; prefira Markdown.

Responda sempre de forma organizada, amigável e em Markdown.""",
}

app = Flask(__name__)
CORS(app, resources={
    r"/*": {"origins": "*"}  
})


@app.route('/token', methods=['GET'])
def get_token():
    """
    Retorna a API Key para o frontend.
    
    NOTA: Em produção, usar autenticação mais segura.
    Para projeto integrador está OK.
    """
    try:
        print("✅ API Key enviada para o frontend")
        return jsonify({"token": API_KEY})
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/config', methods=['GET'])
def get_config():
    """
    Retorna as configurações do Gemini para o frontend usar.
    Centralizando configurações no backend!
    """
    try:
        print("📋 Configurações enviadas para o frontend")
        return jsonify(GEMINI_CONFIG)
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/text/token', methods=['GET'])
def get_text_token():
    """Retorna a mesma API key usada pelo backend de texto (compatível com `chat.py`)."""
    try:
        print("✅ [Texto] API Key enviada para o frontend via /text/token")
        return jsonify({"token": API_KEY})
    except Exception as e:
        print(f"❌ [Texto] Erro: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/text/config', methods=['GET'])
def get_text_config():
    """Retorna a configuração do Gemini para o modo texto (compatível com `chat.py`)."""
    try:
        print("📋 [Texto] Configurações enviadas para o frontend via /text/config")
        return jsonify(GEMINI_TEXT_CONFIG)
    except Exception as e:
        print(f"❌ [Texto] Erro: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/text/chat', methods=['POST'])
def text_chat():
    """Processa o chat de texto COM MEMÓRIA (Histórico)."""
    try:
        data = request.get_json(force=True)
        prompt = data.get('prompt')
        history = data.get('history', []) 

        if not prompt:
            return jsonify({"error": "Campo 'prompt' é obrigatório"}), 400

 
        if not is_related_to_course(prompt):
            pass 

        import urllib.request
        import json

        model = GEMINI_TEXT_CONFIG.get('model')
        

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
        
        messages = []

        for msg in history:
            role = "user" if msg['role'] == 'user' else "model"
            messages.append({
                "role": role,
                "parts": [{"text": msg['content']}]
            })

        messages.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })

        # Corpo da requisição
        body = {
            "contents": messages,
            "systemInstruction": {
                "parts": [{"text": GEMINI_TEXT_CONFIG["systemInstruction"]}]
            },
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 512
            }
        }

        print(f"📡 [Texto] Chamando {model} com {len(messages)} mensagens de contexto...")

        jsondata = json.dumps(body).encode('utf-8')
        req = urllib.request.Request(url, data=jsondata, method='POST')
        req.add_header('Content-Type', 'application/json; charset=utf-8')

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_body = resp.read()
                resp_json = json.loads(resp_body.decode('utf-8'))
                
                answer = None
                try:
                    if 'candidates' in resp_json and len(resp_json['candidates']) > 0:
                        candidate = resp_json['candidates'][0]
                        if 'content' in candidate and 'parts' in candidate['content']:
                            answer = candidate['content']['parts'][0]['text']
                except Exception as e:
                    print(f"⚠️ Erro ao extrair resposta: {e}")
                    pass

                if answer:
                    return jsonify({"answer": answer})
                else:
                    return jsonify({"error": "Resposta vazia ou bloqueada pelo modelo", "raw": resp_json}), 502

        except urllib.error.HTTPError as e:
            error_content = e.read().decode('utf-8')
            print(f"❌ [Texto] Erro {e.code}: {error_content}")
            return jsonify({"answer": "Erro técnico na IA.", "error": str(e), "details": error_content}), 500

        except Exception as e:
            print(f"❌ [Texto] Erro crítico: {e}")
            return jsonify({"error": str(e)}), 500
        
        import urllib.request
        import json

        model = GEMINI_TEXT_CONFIG.get('model') or 'gemini-2.5-flash-preview-09-2025'
        masked_key = (API_KEY[:8] + '...') if API_KEY and len(API_KEY) > 10 else API_KEY
        url = f"https://generativelanguage.googleapis.com/v1beta2/models/{model}:generateText?key={API_KEY}"
        print(f"📡 Chamando API Generative - modelo={model} key_prefix={masked_key}")

        body = {
            "prompt": {"text": prompt},
            "temperature": 0.2,
            "maxOutputTokens": 512
        }

        req = urllib.request.Request(url, method='POST')
        req.add_header('Content-Type', 'application/json; charset=utf-8')

        jsondata = json.dumps(body).encode('utf-8')
        req.add_header('Content-Length', len(jsondata))

        try:
            print(f"📨 Payload size: {len(jsondata)} bytes. Enviando requisição...")
            with urllib.request.urlopen(req, data=jsondata, timeout=30) as resp:
                resp_body = resp.read()
                print(f"📥 Recebido {len(resp_body)} bytes do serviço remoto")
                try:
                    resp_json = json.loads(resp_body.decode('utf-8'))
                    print("✅ Resposta JSON parseada com sucesso do modelo")
                    if isinstance(resp_json, dict):
                        keys = list(resp_json.keys())
                        print(f"🗂 Chaves no JSON de resposta: {keys}")
                except Exception as parse_exc:
                    print(f"⚠️ Falha ao parsear JSON da resposta remota: {parse_exc}")
                    resp_json = None
        except Exception as http_exc:
            try:
                import urllib.error
                if isinstance(http_exc, urllib.error.HTTPError):
                    body = http_exc.read().decode('utf-8', errors='ignore')
                    print(f"❌ HTTPError {http_exc.code} ao chamar API Generative: {body}")
                    friendly = "Desculpe, tivemos um problema técnico ao gerar a resposta. Tente novamente em alguns minutos." 
                    return jsonify({"answer": friendly, "error": f"HTTP Error {http_exc.code}: {http_exc.reason}", "remote_body": body})
                elif isinstance(http_exc, urllib.error.URLError):
                    print(f"❌ URLError ao chamar API Generative: {http_exc.reason}")
                    friendly = "Desculpe, não consegui contatar o serviço de geração de texto. Tente novamente mais tarde." 
                    return jsonify({"answer": friendly, "error": f"URL Error: {http_exc.reason}"})
            except Exception:
                pass
            print(f"❌ Erro genérico ao chamar API Generative: {http_exc}")
            friendly = "Desculpe, ocorreu um erro ao gerar a resposta. Tente novamente em alguns instantes." 
            return jsonify({"answer": friendly, "error": str(http_exc)})

        answer = None
        if isinstance(resp_json, dict):
            if 'candidates' in resp_json and isinstance(resp_json['candidates'], list) and len(resp_json['candidates'])>0:
                answer = resp_json['candidates'][0].get('output') or resp_json['candidates'][0].get('content')

            if not answer:
                def find_output(obj):
                    if isinstance(obj, str):
                        return obj
                    if isinstance(obj, dict):
                        for k,v in obj.items():
                            res = find_output(v)
                            if res:
                                return res
                    if isinstance(obj, list):
                        for el in obj:
                            res = find_output(el)
                            if res:
                                return res
                    return None
                answer = find_output(resp_json)

        if not answer:
            return jsonify({"error": "Não foi possível extrair resposta do modelo", "raw": resp_json}), 502

        return jsonify({"answer": answer})

    except Exception as e:
        print(f"❌ Erro em /text/chat: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/text/diag', methods=['GET'])
def text_diag():
    """Endpoint de diagnóstico rápido para testar a integração com a API Generative.

    Retorna um JSON com resultado da tentativa de chamada (sem expor a chave completa),
    útil para depuração quando /text/chat falha.
    """
    try:
        import urllib.request
        import json

        model = GEMINI_TEXT_CONFIG.get('model') or 'gemini-2.5-flash-preview-09-2025'
        masked_key = (API_KEY[:8] + '...') if API_KEY and len(API_KEY) > 10 else API_KEY
        url = f"https://generativelanguage.googleapis.com/v1beta2/models/{model}:generateText?key={API_KEY}"

        test_prompt = "Teste diagnóstico: responda apenas 'ok'"
        body = {
            "prompt": {"text": test_prompt},
            "temperature": 0.0,
            "maxOutputTokens": 20
        }

        req = urllib.request.Request(url, method='POST')
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondata = json.dumps(body).encode('utf-8')
        req.add_header('Content-Length', len(jsondata))

        try:
            print(f"[DIAG] Chamando endpoint remoto modelo={model} key_prefix={masked_key}")
            with urllib.request.urlopen(req, data=jsondata, timeout=20) as resp:
                resp_body = resp.read()
                try:
                    resp_json = json.loads(resp_body.decode('utf-8'))
                except Exception as pe:
                    return jsonify({
                        "ok": False,
                        "reason": "não foi possível parsear JSON da resposta remota",
                        "parse_error": str(pe),
                        "remote_body": resp_body.decode('utf-8', errors='ignore')
                    }), 200

                return jsonify({
                    "ok": True,
                    "model": model,
                    "key_prefix": masked_key,
                    "remote_keys": list(resp_json.keys()) if isinstance(resp_json, dict) else None,
                    "sample": (resp_json if isinstance(resp_json, dict) else str(resp_json))
                }), 200

        except Exception as http_exc:
            try:
                import urllib.error
                if isinstance(http_exc, urllib.error.HTTPError):
                    body = http_exc.read().decode('utf-8', errors='ignore')
                    return jsonify({
                        "ok": False,
                        "type": "HTTPError",
                        "code": getattr(http_exc, 'code', None),
                        "reason": getattr(http_exc, 'reason', str(http_exc)),
                        "remote_body": body
                    }), 200
                elif isinstance(http_exc, urllib.error.URLError):
                    return jsonify({
                        "ok": False,
                        "type": "URLError",
                        "reason": str(http_exc)
                    }), 200
            except Exception:
                pass

            return jsonify({
                "ok": False,
                "type": "other",
                "error": str(http_exc)
            }), 200

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/', methods=['GET'])
def home():
    """Status do servidor."""
    return jsonify({
        "status": "online",
        "service": "SenaChat Backend",
        "endpoints": {
            "/token": "Retorna API key",
            "/config": "Retorna configurações do Gemini"
        }
    })

from flask import send_from_directory

@app.route('/public/<path:filename>')
def serve_public(filename):
    return send_from_directory('public', filename)


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 SenaChat Backend")
    print("="*50)
    print("📡 Servidor: http://localhost:5000")
    print("🔑 Endpoints:")
    print("   - GET /token  → API Key")
    print("   - GET /config → Configurações do Gemini")
    print("="*50)
    
    print("\n🔍 Rotas registradas no Flask:")
    for rule in app.url_map.iter_rules():
        print(f"   {rule.methods} {rule.rule}")
    print("="*50)
    
    print("💡 Deixe este terminal aberto!\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )