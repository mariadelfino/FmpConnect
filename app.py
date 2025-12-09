import os
import json
import urllib.request
import urllib.error
import asyncio       # Necessário para a voz
import edge_tts      # Biblioteca de voz da Microsoft
import tempfile      # Para salvar o áudio temporário
from flask import Flask, jsonify, request, send_from_directory, send_file 
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

try:
    API_KEY = os.environ["GOOGLE_API_KEY"]
except KeyError:
    print("ERRO: GOOGLE_API_KEY não encontrada no .env")
    print("Crie um arquivo .env com: GOOGLE_API_KEY=sua_chave_aqui")
    exit(1)


GEMINI_TEXT_CONFIG = {
    "model": "gemini-2.5-flash", 
    "systemInstruction": """Você é o FMPConnect, o assistente virtual oficial da Faculdade Municipal de Palhoça (FMP).

IDENTIDADE E PERSONALIDADE
Nome: FMPConnect
Tom e Estilo: Profissional, acolhedor, acadêmico (mas acessível), informativo e orgulhoso de representar uma instituição pública municipal.
Propósito: Fornecer informações precisas sobre cursos, serviços ao aluno, biblioteca, laboratórios e contatos da FMP.

BASE DE CONHECIMENTO - FACULDADE MUNICIPAL DE PALHOÇA (FMP)

📍 Localização e Acesso Digital
Site Oficial: https://fmpsc.edu.br/
Portal do Aluno (SGA): http://sga.fmpsc.edu.br/portal (Para notas, faltas e serviços acadêmicos).
Endereço: Rua João Pereira dos Santos, 99 - Ponte do Imaruim - Palhoça - SC, CEP 88130-475.
Telefone Geral: (48) 3220-0376
E-mail Geral: contato@fmpsc.edu.br
Horário de Atendimento Geral: Matutino, Vespertino e Noturno (confirme no site para setores específicos).

🎓 Cursos de Graduação (Presencial)
1. Administração (Bacharelado)
   - Duração: 4 anos | Turnos: Matutino e Noturno
2. Pedagogia (Licenciatura)
   - Duração: 4 anos | Turnos: Matutino e Noturno
3. Processos Gerenciais (Tecnólogo)
   - Duração: 2 anos | Turno: Matutino
4. Análise e Desenvolvimento de Sistemas - ADS (Tecnólogo)
   - Duração: 2,5 anos | Turno: Matutino
⚠️ Atenção: O curso de Gestão de Turismo consta como indisponível/ativo apenas em registros antigos.

📚 Pós-Graduação (Especialização)
1. Gestão Escolar (Duração: 1 ano)
2. Gestão Empresarial (Duração: 1 ano)

📖 Biblioteca
Uso exclusivo para alunos, docentes e funcionários.
Contato: biblioteca@fmpsc.edu.br | Telefone: (48) 3220-0376
Equipe: Karla Linhares (Bibliotecária – CRB-14/1135 - karla.linhares@fmpsc.edu.br).
Horários de Atendimento:
- Geral: Segunda a sexta, das 07h às 13h e das 13h às 21h.
- Atendimento específico (Karla Linhares): Segunda a sexta das 15h às 21h.

Regras e Prazos de Empréstimo:
- Alunos Graduação: 3 livros por 7 dias.
- Alunos TCC e Pós-graduação: 3 livros por 15 dias.
- Professores e funcionários: 5 livros por 30 dias.
⚠️ Multa: Em caso de atraso na devolução, a multa será a suspensão na biblioteca de três dias por cada dia de atraso.

🧩 Programas, Laboratórios e Núcleos

1. Programa da Maturidade (Extensão)
   - Descrição: Implantado em 2007, atende pessoas a partir de 50 anos, promovendo inclusão social e qualidade de vida. Oferece disciplinas optativas e atende cerca de 80 idosos com atividades lúdicas, físicas, artísticas e culturais.
   - Atividades: Segunda a quinta-feira, das 14h às 17h.
   - Inscrições: Semestrais na COPER.
   - Local: COPER (Coordenação de Pesquisa, Extensão e Responsabilidade Social) – Térreo, próximo à entrada.
   - Horário de Atendimento COPER (Externo): Seg a Qui (13h-19h), Sex (08h-14h).
   - Responsável: Deisi Cord (Link Lattes: http://lattes.cnpq.br/4093440617073291).
   - Contato: coper@fmpsc.edu.br | (48) 3220-0376.

2. iLAB – Inovação e Tecnologia
   - Descrição: Programa de Pesquisa vinculado ao curso de ADS. Visa ampliar conhecimentos sobre inovação e tecnologia, aproximando alunos do mercado via desenvolvimento de soluções digitais.
   - Ingresso: Interesse espontâneo ao longo do ano ou convite. Aberto a todas as fases.
   - Funcionamento: Atendimento diário após a aula no período matutino. Encontros de projetos uma vez por semana.
   - Responsável: Prof. Daniela Amorim.
   - Contato: iLAB@fmpsc.edu.br

3. Serviço de Orientação ao Acadêmico (SOA)
   - Descrição: Ofertado desde 2005. Objetivo: Promover atendimento, apoio e monitoramento da aprendizagem para prevenir a evasão e contribuir para o pleno desenvolvimento do ensino (conforme PDI 2019).
   - Contato: soa@fmpsc.edu.br

4. Laboratório de Práticas Pedagógicas / Brinquedoteca
   - Descrição: Laboratório do Curso de Pedagogia, atende crianças de 3 a 12 anos, incentivando o brincar livre, jogos e literatura. Integrada à matriz curricular e atualmente em articulação com o CRIAS.
   - Responsável: Juliane Di Paula Queiroz Odinino.
   - Contato: juliane.odinino@fmpsc.edu.br

ℹ️ Sobre a Instituição
Missão: Produzir e disseminar conhecimento, promovendo o desenvolvimento humano, intelectual, tecnológico e sustentável de Palhoça.
Diferencial: Instituição pública municipal. Historicamente destina grande parte das vagas (aprox. 80%) para alunos oriundos de escolas públicas residentes em Palhoça.

📝 Ingresso / Vestibular
A forma de ingresso principal é através de Editais de Processo Seletivo (Vestibular) ou Vagas Remanescentes publicados no site oficial.

REGRAS DE RESPOSTA GERAL:
1. Link Obrigatório:
   - Para notas/faltas: Envie http://sga.fmpsc.edu.br/portal
   - Para editais/cursos: Envie https://fmpsc.edu.br/
2. Não invente datas.
3. Responda apenas sobre a FMP.
""",
}

app = Flask(__name__)
CORS(app, resources={
    r"/*": {"origins": "*"}  
})

# --- Rota de Text-to-Speech (Voz Humana) ---
@app.route('/text/tts', methods=['POST'])
def text_tts():
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({"error": "Texto vazio"}), 400

        VOICE = "pt-BR-AntonioNeural" 
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_filename = fp.name

        async def generate_audio():
            communicate = edge_tts.Communicate(text, VOICE)
            await communicate.save(temp_filename)

        asyncio.run(generate_audio())

        return send_file(temp_filename, mimetype="audio/mpeg")

    except Exception as e:
        print(f"❌ Erro no TTS: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/text/token', methods=['GET'])
def get_text_token():
    try:
        return jsonify({"token": API_KEY})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/text/config', methods=['GET'])
def get_text_config():
    try:
        return jsonify(GEMINI_TEXT_CONFIG)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ROTA DE CHAT INTELIGENTE ---
@app.route('/text/chat', methods=['POST'])
def text_chat():
    """Processa o chat de texto COM MEMÓRIA e MODO SURDEZ OTIMIZADO."""
    try:
        data = request.get_json(force=True)
        prompt = data.get('prompt')
        history = data.get('history', []) 
        mode = data.get('mode', 'normal') 

        if not prompt:
            return jsonify({"error": "Campo 'prompt' é obrigatório"}), 400

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

        # Pegamos a instrução padrão
        current_system_instruction = GEMINI_TEXT_CONFIG["systemInstruction"]
        temperature_setting = 0.4 # Padrão mais criativo

        # --- LÓGICA DO MODO SURDEZ ---
        if mode == 'surdez':
            temperature_setting = 0.1 # Reduz a criatividade para ser mais exato
            
            # Verifica se é o início da conversa (histórico vazio)
            is_start_of_conversation = len(history) == 0

            accessibility_rules = """
            [MODO ACESSIBILIDADE/SURDEZ ATIVO]
            PERFIL: O usuário necessita de objetividade máxima, clareza visual e português simplificado.
            
            REGRAS DE FORMATAÇÃO E ESTILO:
            1. Use frases curtas (Sujeito + Verbo + Predicado).
            2. Prefira listas (bullet points) ao invés de parágrafos longos.
            3. Evite conectivos complexos (portanto, contudo, todavia).
            4. Seja direto: Dê a informação imediatamente.
            """

            if is_start_of_conversation:
                # Na primeira mensagem, permite uma saudação curta
                accessibility_rules += """
                REGRA DE INÍCIO:
                - Você PODE dizer "Olá. Modo acessibilidade ativado." uma única vez.
                - Em seguida, responda a pergunta se houver, ou aguarde o comando.
                """
            else:
                # Nas mensagens seguintes, PROÍBE saudações
                accessibility_rules += """
                REGRA CRÍTICA - ZERO REPETIÇÃO:
                - É ESTRITAMENTE PROIBIDO usar saudações como: "Olá", "Oi", "Tudo bem", "Sou o FMPConnect".
                - É PROIBIDO frases de enchimento como: "Com certeza", "Entendo sua dúvida", "Aqui está a informação".
                - Comece a resposta DIRETAMENTE com o dado solicitado.
                Exemplo Errado: "Olá! O curso de ADS dura 2,5 anos."
                Exemplo Correto: "O curso de ADS dura 2,5 anos."
                """
            
            current_system_instruction += accessibility_rules

        body = {
            "contents": messages,
            "systemInstruction": {
                "parts": [{"text": current_system_instruction}]
            },
            "generationConfig": {
                "temperature": temperature_setting,
                "maxOutputTokens": 800 
            }
        }

        print(f"📡 [Texto] Chamando {model} | Modo: {mode} | Histórico: {len(history)} msgs")

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


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "service": "FMPConnect Backend"
    })

@app.route('/public/<path:filename>')
def serve_public(filename):
    return send_from_directory('public', filename)


if __name__ == '__main__':
    print("\n" + "="*50)
    print("FMPConnect Backend - Otimizado para Acessibilidade")
    print("="*50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )