import os
import json
import urllib.request
import urllib.error
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# --- Configurações Auxiliares ---

# Palavras-chave atualizadas para o contexto da FMP
COURSE_KEYWORDS = [
    'fmp', 'faculdade municipal', 'palhoça', 'palhoca', 'fmpsc', 
    'administração', 'administracao', 'pedagogia', 'processos gerenciais', 
    'gestão', 'gestao', 'turismo', 'ads', 'análise e desenvolvimento', 'analise e desenvolvimento',
    'sistemas', 'curso', 'graduação', 'graduacao', 'pós', 'pos', 'pós-graduação',
    'inscri', 'matr', 'vestibular', 'edital', 'vaga', 'bolsa', 'gratuito',
    'endereço', 'endereco', 'local', 'contato', 'telefone', 'email', 'e-mail'
]

def is_related_to_course(prompt_text: str) -> bool:
    """Checa se o prompt parece estar relacionado à FMP (Faculdade Municipal de Palhoça)."""
    if not prompt_text:
        return False
    txt = prompt_text.lower()
    for kw in COURSE_KEYWORDS:
        if kw in txt:
            return True
    return False

# --- Configuração da API ---

try:
    API_KEY = os.environ["GOOGLE_API_KEY"]
except KeyError:
    print("ERRO: GOOGLE_API_KEY não encontrada no .env")
    print("Crie um arquivo .env com: GOOGLE_API_KEY=sua_chave_aqui")
    exit(1)

GEMINI_TEXT_CONFIG = {
    "model": "gemini-2.0-flash",
    "systemInstruction": """Você é o FMPConnect, o assistente virtual oficial da Faculdade Municipal de Palhoça (FMP).

IDENTIDADE E PERSONALIDADE
Nome: FMPConnect
Tom e Estilo: Profissional, acolhedor, acadêmico (mas acessível), informativo e orgulhoso de representar uma instituição pública municipal.
Propósito: Fornecer informações precisas sobre cursos de graduação, pós-graduação, processos seletivos, localização e contatos da FMP.

BASE DE CONHECIMENTO - FACULDADE MUNICIPAL DE PALHOÇA (FMP)

📍 Localização e Contato
Site Oficial: https://fmpsc.edu.br/
Endereço: Rua João Pereira dos Santos, 99 - Ponte do Imaruim - Palhoça - SC, CEP 88130-475.
Telefone: (48) 3220-0376
E-mail Geral: contato@fmpsc.edu.br
Horário de Atendimento: Geralmente Matutino, Vespertino e Noturno (confirme no site para horários específicos de secretaria).

🎓 Cursos de Graduação (Presencial)
1. Administração (Bacharelado)
   - Duração: 4 anos
   - Turnos: Matutino e Noturno
2. Pedagogia (Licenciatura)
   - Duração: 4 anos
   - Turnos: Matutino e Noturno
3. Processos Gerenciais (Tecnólogo)
   - Duração: 2 anos
   - Turno: Matutino
4. Análise e Desenvolvimento de Sistemas - ADS (Tecnólogo)
   - Duração: 2,5 anos
   - Turno: Matutino
⚠️ Atenção: O curso de Gestão de Turismo consta como indisponível/ativo apenas em registros antigos, verifique editais atuais.

📚 Pós-Graduação (Especialização)
1. Gestão Escolar (Duração: 1 ano)
2. Gestão Empresarial (Duração: 1 ano)

ℹ️ Sobre a Instituição
Missão: Produzir e disseminar conhecimento, promovendo o desenvolvimento humano, intelectual, tecnológico e sustentável de Palhoça.
Diferencial: Instituição pública municipal. Historicamente destina grande parte das vagas (aprox. 80%) para alunos oriundos de escolas públicas residentes em Palhoça (consulte editais para regras atuais de cotas).

📝 Ingresso / Vestibular
A forma de ingresso principal é através de Editais de Processo Seletivo (Vestibular) ou Vagas Remanescentes.
Os editais são publicados periodicamente no site oficial na aba "Editais" ou "Vestibular".
Sempre oriente o usuário a ler o edital vigente para datas e regras de isenção.

REGRAS DE RESPOSTA
1. Link Obrigatório: Sempre que falar sobre inscrições, editais ou detalhes curriculares, forneça: https://fmpsc.edu.br/
2. Não invente datas: Se perguntarem "quando é a prova?", diga que é necessário verificar o edital aberto no site, pois as datas mudam a cada semestre.
3. Fora do Escopo: Perguntas sobre outros assuntos (futebol, política nacional, receitas) devem ser gentilmente recusadas com: "Sou o FMPConnect e respondo apenas sobre a Faculdade Municipal de Palhoça."
4. Clareza: Seja direto. Se perguntarem o endereço, dê o endereço completo.

EXEMPLOS DE INTERAÇÃO
Usuário: "Quais cursos tem?"
FMPConnect: "A FMP oferece cursos de graduação presencial: Administração (Bacharelado), Pedagogia (Licenciatura), Processos Gerenciais (Tecnólogo) e Análise e Desenvolvimento de Sistemas (ADS). Também possuímos pós-graduação em Gestão Escolar e Gestão Empresarial. Saiba mais em: https://fmpsc.edu.br/"

Usuário: "É de graça?"
FMPConnect: "A FMP é uma faculdade municipal pública. Existem taxas administrativas e de matrícula que podem variar conforme o edital, mas a instituição possui forte caráter social, muitas vezes com políticas de gratuidade ou bolsas para residentes de Palhoça oriundos de escola pública. Recomendo consultar o edital mais recente no site para confirmar os valores atuais."

Usuário: "Onde fica?"
FMPConnect: "A FMP fica na Ponte do Imaruim, em Palhoça. O endereço é Rua João Pereira dos Santos, 99. O CEP é 88130-475."
""",
}

app = Flask(__name__)
CORS(app, resources={
    r"/*": {"origins": "*"}  
})

# --- Rotas de Texto ---

@app.route('/text/token', methods=['GET'])
def get_text_token():
    """Retorna a API key (se o frontend precisar)."""
    try:
        print("[Texto] API Key solicitada")
        return jsonify({"token": API_KEY})
    except Exception as e:
        print(f"❌ [Texto] Erro: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/text/config', methods=['GET'])
def get_text_config():
    """Retorna a configuração do Gemini para o modo texto."""
    try:
        print("[Texto] Configurações enviadas")
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


        model = GEMINI_TEXT_CONFIG.get('model')
        
        # Endpoint oficial v1beta do Gemini (generateContent)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
        
        messages = []

        # Converte histórico do frontend para formato da API
        for msg in history:
            role = "user" if msg['role'] == 'user' else "model"
            messages.append({
                "role": role,
                "parts": [{"text": msg['content']}]
            })

        # Adiciona a mensagem atual
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


@app.route('/text/diag', methods=['GET'])
def text_diag():
    """Endpoint de diagnóstico rápido para testar a integração com a API Generative."""
    try:
        model = GEMINI_TEXT_CONFIG.get('model')
        masked_key = (API_KEY[:8] + '...') if API_KEY and len(API_KEY) > 10 else API_KEY
        
        # Teste simples com generateContent
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"

        test_prompt = "Teste diagnóstico: responda apenas 'ok'"
        body = {
            "contents": [{"role": "user", "parts": [{"text": test_prompt}]}],
            "generationConfig": {"temperature": 0.0, "maxOutputTokens": 20}
        }

        req = urllib.request.Request(url, method='POST')
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondata = json.dumps(body).encode('utf-8')
        req.add_header('Content-Length', len(jsondata))

        try:
            print(f"[DIAG] Chamando endpoint remoto modelo={model} key_prefix={masked_key}")
            with urllib.request.urlopen(req, data=jsondata, timeout=20) as resp:
                resp_body = resp.read()
                resp_json = json.loads(resp_body.decode('utf-8'))

                return jsonify({
                    "ok": True,
                    "model": model,
                    "key_prefix": masked_key,
                    "response_sample": resp_json
                }), 200

        except urllib.error.HTTPError as http_exc:
             body = http_exc.read().decode('utf-8', errors='ignore')
             return jsonify({"ok": False, "type": "HTTPError", "code": http_exc.code, "body": body}), 200
        except Exception as e:
             return jsonify({"ok": False, "type": "Other", "error": str(e)}), 200

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# --- Rotas Gerais ---

@app.route('/', methods=['GET'])
def home():
    """Status do servidor."""
    return jsonify({
        "status": "online",
        "service": "FMPConnect Backend",
        "endpoints": {
            "/text/token": "Retorna API key",
            "/text/config": "Retorna configurações",
            "/text/chat": "Endpoint principal do chat"
        }
    })

@app.route('/public/<path:filename>')
def serve_public(filename):
    return send_from_directory('public', filename)


if __name__ == '__main__':
    print("\n" + "="*50)
    print("FMPConnect Backend - Faculdade Municipal de Palhoça")
    print("="*50)
    print("Servidor rodando em: http://localhost:5000")
    print("Endpoints Texto: /text/token, /text/config, /text/chat")
    print("="*50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )