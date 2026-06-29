import os
import sys
import json
import urllib.request
import urllib.error
import asyncio

# Garante que prints com emoji não travem no terminal Windows (cp1252)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import edge_tts
import tempfile
from datetime import datetime, timezone, timedelta
from functools import wraps

import jwt as pyjwt
from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

import database
import rpa

load_dotenv()

try:
    API_KEY = os.environ["GOOGLE_API_KEY"]
except KeyError:
    print("ERRO: GOOGLE_API_KEY não encontrada no .env")
    print("Crie um arquivo .env com: GOOGLE_API_KEY=sua_chave_aqui")
    exit(1)

JWT_SECRET = os.environ.get("JWT_SECRET", "fmpconnect-jwt-secret-change-in-production")
JWT_EXPIRY_HOURS = 8

BASE_SYSTEM_INSTRUCTION = """Você é o FMPConnect, o assistente virtual oficial da Faculdade Municipal de Palhoça (FMP).

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
"""

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# ──────────────────────────────────────────────
# Decoradores de autenticação
# ──────────────────────────────────────────────

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "").strip()
        if not token:
            return jsonify({"error": "Token não fornecido"}), 401
        try:
            payload = pyjwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.current_user = payload
        except pyjwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado, faça login novamente"}), 401
        except pyjwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    @wraps(f)
    @require_auth
    def decorated(*args, **kwargs):
        if request.current_user.get("role") != "admin":
            return jsonify({"error": "Acesso restrito a administradores"}), 403
        return f(*args, **kwargs)
    return decorated


# ──────────────────────────────────────────────
# Rotas de Autenticação Admin
# ──────────────────────────────────────────────

@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json(force=True)
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Usuário e senha são obrigatórios"}), 400

    conn = database.get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username=? AND active=1", (username,)
    ).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Usuário ou senha incorretos"}), 401

    exp = datetime.now(tz=timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
    token = pyjwt.encode(
        {"user_id": user["id"], "username": user["username"],
         "name": user["name"], "role": user["role"], "exp": exp},
        JWT_SECRET, algorithm="HS256"
    )

    return jsonify({
        "token": token,
        "user": {"id": user["id"], "username": user["username"],
                 "name": user["name"], "role": user["role"]}
    })


@app.route("/admin/verify", methods=["GET"])
@require_auth
def admin_verify():
    return jsonify({"valid": True, "user": request.current_user})


@app.route("/admin/change-password", methods=["POST"])
@require_auth
def admin_change_password():
    data = request.get_json(force=True)
    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")

    if not current_password or not new_password:
        return jsonify({"error": "Campos obrigatórios ausentes"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Nova senha deve ter ao menos 6 caracteres"}), 400

    conn = database.get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id=?", (request.current_user["user_id"],)
    ).fetchone()

    if not user or not check_password_hash(user["password_hash"], current_password):
        conn.close()
        return jsonify({"error": "Senha atual incorreta"}), 401

    conn.execute(
        "UPDATE users SET password_hash=? WHERE id=?",
        (generate_password_hash(new_password), request.current_user["user_id"])
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Senha alterada com sucesso"})


# ──────────────────────────────────────────────
# Rotas de Base de Conhecimento
# ──────────────────────────────────────────────

@app.route("/admin/knowledge", methods=["GET"])
@require_auth
def list_knowledge():
    items = database.get_knowledge_items(active_only=False)
    return jsonify({"items": items})


@app.route("/admin/knowledge", methods=["POST"])
@require_auth
def create_knowledge():
    data = request.get_json(force=True)
    category = data.get("category", "").strip()
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()

    if not category or not title or not content:
        return jsonify({"error": "Categoria, título e conteúdo são obrigatórios"}), 400

    conn = database.get_db()
    cursor = conn.execute(
        "INSERT INTO knowledge_items (category, title, content, created_by) VALUES (?, ?, ?, ?)",
        (category, title, content, request.current_user["user_id"])
    )
    item_id = cursor.lastrowid
    conn.commit()
    item = conn.execute("SELECT * FROM knowledge_items WHERE id=?", (item_id,)).fetchone()
    conn.close()
    return jsonify({"message": "Item criado com sucesso", "item": dict(item)}), 201


@app.route("/admin/knowledge/<int:item_id>", methods=["PUT"])
@require_auth
def update_knowledge(item_id):
    data = request.get_json(force=True)
    category = data.get("category", "").strip()
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()

    if not category or not title or not content:
        return jsonify({"error": "Categoria, título e conteúdo são obrigatórios"}), 400

    conn = database.get_db()
    existing = conn.execute("SELECT id FROM knowledge_items WHERE id=?", (item_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "Item não encontrado"}), 404

    conn.execute(
        "UPDATE knowledge_items SET category=?, title=?, content=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (category, title, content, item_id)
    )
    conn.commit()
    item = conn.execute("SELECT * FROM knowledge_items WHERE id=?", (item_id,)).fetchone()
    conn.close()
    return jsonify({"message": "Item atualizado", "item": dict(item)})


@app.route("/admin/knowledge/<int:item_id>", methods=["DELETE"])
@require_auth
def delete_knowledge(item_id):
    conn = database.get_db()
    existing = conn.execute("SELECT id FROM knowledge_items WHERE id=?", (item_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "Item não encontrado"}), 404

    conn.execute("UPDATE knowledge_items SET active=0 WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Item removido"})


@app.route("/admin/knowledge/<int:item_id>/restore", methods=["POST"])
@require_auth
def restore_knowledge(item_id):
    conn = database.get_db()
    conn.execute("UPDATE knowledge_items SET active=1 WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Item restaurado"})


# ──────────────────────────────────────────────
# Rotas de Gerenciamento de Usuários (admin only)
# ──────────────────────────────────────────────

@app.route("/admin/users", methods=["GET"])
@require_admin
def list_users():
    conn = database.get_db()
    rows = conn.execute(
        "SELECT id, username, email, name, role, created_at, active FROM users ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return jsonify({"users": [dict(r) for r in rows]})


@app.route("/admin/users", methods=["POST"])
@require_admin
def create_user():
    data = request.get_json(force=True)
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    name = data.get("name", "").strip()
    password = data.get("password", "")
    role = data.get("role", "editor")

    if not username or not email or not name or not password:
        return jsonify({"error": "Todos os campos são obrigatórios"}), 400

    if role not in ("admin", "editor"):
        return jsonify({"error": "Papel inválido (use 'admin' ou 'editor')"}), 400

    if len(password) < 6:
        return jsonify({"error": "Senha deve ter ao menos 6 caracteres"}), 400

    conn = database.get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (username, email, name, password_hash, role) VALUES (?, ?, ?, ?, ?)",
            (username, email, name, generate_password_hash(password), role)
        )
        user_id = cursor.lastrowid
        conn.commit()
        user = conn.execute(
            "SELECT id, username, email, name, role, created_at FROM users WHERE id=?", (user_id,)
        ).fetchone()
        conn.close()
        return jsonify({"message": "Usuário criado", "user": dict(user)}), 201
    except Exception:
        conn.close()
        return jsonify({"error": "Nome de usuário ou e-mail já existe"}), 409


@app.route("/admin/users/<int:user_id>", methods=["PUT"])
@require_admin
def update_user(user_id):
    data = request.get_json(force=True)
    conn = database.get_db()
    existing = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "Usuário não encontrado"}), 404

    name = data.get("name", existing["name"]).strip()
    email = data.get("email", existing["email"]).strip()
    role = data.get("role", existing["role"])
    active = data.get("active", existing["active"])

    if role not in ("admin", "editor"):
        conn.close()
        return jsonify({"error": "Papel inválido"}), 400

    conn.execute(
        "UPDATE users SET name=?, email=?, role=?, active=? WHERE id=?",
        (name, email, role, 1 if active else 0, user_id)
    )

    if data.get("password"):
        if len(data["password"]) < 6:
            conn.close()
            return jsonify({"error": "Senha deve ter ao menos 6 caracteres"}), 400
        conn.execute(
            "UPDATE users SET password_hash=? WHERE id=?",
            (generate_password_hash(data["password"]), user_id)
        )

    conn.commit()
    user = conn.execute(
        "SELECT id, username, email, name, role, active FROM users WHERE id=?", (user_id,)
    ).fetchone()
    conn.close()
    return jsonify({"message": "Usuário atualizado", "user": dict(user)})


@app.route("/admin/users/<int:user_id>", methods=["DELETE"])
@require_admin
def deactivate_user(user_id):
    if user_id == request.current_user["user_id"]:
        return jsonify({"error": "Você não pode desativar sua própria conta"}), 400

    conn = database.get_db()
    conn.execute("UPDATE users SET active=0 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Usuário desativado"})


# ──────────────────────────────────────────────
# Rota de Text-to-Speech
# ──────────────────────────────────────────────

@app.route("/text/tts", methods=["POST"])
def text_tts():
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "Texto vazio"}), 400

        VOICE = "pt-BR-AntonioNeural"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_filename = fp.name

        async def generate_audio():
            communicate = edge_tts.Communicate(text, VOICE)
            await communicate.save(temp_filename)

        # Cria um loop isolado para evitar conflito com o event loop do Flask/debug
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(generate_audio())
        finally:
            loop.close()

        return send_file(temp_filename, mimetype="audio/mpeg")

    except Exception as e:
        print(f"[ERRO] TTS: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/text/config", methods=["GET"])
def get_text_config():
    # Retorna apenas o modelo — a chave NUNCA é enviada ao cliente
    dynamic_instruction = database.build_dynamic_system_instruction(BASE_SYSTEM_INSTRUCTION)
    return jsonify({"model": "gemini-2.5-flash", "systemInstruction": dynamic_instruction})


# ──────────────────────────────────────────────
# Rota de Chat Inteligente
# ──────────────────────────────────────────────

@app.route("/text/chat", methods=["POST"])
def text_chat():
    try:
        data = request.get_json(force=True)
        prompt = data.get("prompt")
        history = data.get("history", [])
        mode = data.get("mode", "normal")

        if not prompt:
            return jsonify({"error": "Campo 'prompt' é obrigatório"}), 400

        model = "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"

        messages = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            messages.append({"role": role, "parts": [{"text": msg["content"]}]})

        messages.append({"role": "user", "parts": [{"text": prompt}]})

        current_system_instruction = database.build_dynamic_system_instruction(BASE_SYSTEM_INSTRUCTION)
        temperature_setting = 0.4

        if mode == "surdez":
            temperature_setting = 0.1
            is_start = len(history) == 0
            accessibility_rules = """
            [MODO ACESSIBILIDADE/SURDEZ ATIVO]
            PERFIL: O usuário necessita de objetividade máxima, clareza visual e português simplificado.

            REGRAS DE FORMATAÇÃO E ESTILO:
            1. Use frases curtas (Sujeito + Verbo + Predicado).
            2. Prefira listas (bullet points) ao invés de parágrafos longos.
            3. Evite conectivos complexos (portanto, contudo, todavia).
            4. Seja direto: Dê a informação imediatamente.
            """
            if is_start:
                accessibility_rules += """
                REGRA DE INÍCIO:
                - Você PODE dizer "Olá. Modo acessibilidade ativado." uma única vez.
                - Em seguida, responda a pergunta se houver, ou aguarde o comando.
                """
            else:
                accessibility_rules += """
                REGRA CRÍTICA - ZERO REPETIÇÃO:
                - É ESTRITAMENTE PROIBIDO usar saudações como: "Olá", "Oi", "Tudo bem", "Sou o FMPConnect".
                - Comece a resposta DIRETAMENTE com o dado solicitado.
                Exemplo Correto: "O curso de ADS dura 2,5 anos."
                """
            current_system_instruction += accessibility_rules

        body = {
            "contents": messages,
            "systemInstruction": {"parts": [{"text": current_system_instruction}]},
            "generationConfig": {"temperature": temperature_setting, "maxOutputTokens": 800}
        }

        print(f"[CHAT] {model} | Modo: {mode} | Histórico: {len(history)} msgs")

        jsondata = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=jsondata, method="POST")
        req.add_header("Content-Type", "application/json; charset=utf-8")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                answer = None
                try:
                    candidates = resp_json.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            answer = parts[0]["text"]
                except Exception:
                    pass

                if answer:
                    return jsonify({"answer": answer})
                return jsonify({"error": "Resposta vazia ou bloqueada pelo modelo", "raw": resp_json}), 502

        except urllib.error.HTTPError as e:
            error_content = e.read().decode("utf-8", errors="replace")
            safe_content = error_content.encode("ascii", errors="replace").decode("ascii")
            print(f"[ERRO] HTTP {e.code}: {safe_content[:200]}")
            return jsonify({"answer": "Erro técnico na IA.", "error": str(e)}), 500

    except Exception as e:
        safe_e = str(e).encode("ascii", errors="replace").decode("ascii")
        print(f"[ERRO] Critico no chat: {safe_e}")
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────
# Rotas RPA
# ──────────────────────────────────────────────

@app.route("/admin/rpa/scrape", methods=["POST"])
@require_auth
def rpa_scrape():
    """Raspa o site da FMP e importa itens novos para a base de conhecimento."""
    try:
        itens = rpa.scrape_site_fmp()
        user_id = request.current_user.get("user_id", 1)
        resultado = rpa.importar_para_base(itens, user_id=user_id)
        return jsonify({
            "message": f"{resultado['inseridos']} item(ns) importado(s), {resultado['ignorados']} ignorado(s).",
            **resultado,
            "total_encontrados": len(itens)
        })
    except Exception as e:
        print(f"[ERRO] RPA scrape: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/admin/rpa/emails", methods=["POST"])
@require_auth
def rpa_emails():
    """
    Lê e-mails de feedback via IMAP e importa como itens de conhecimento.
    Body esperado: { imap_host, imap_port, email, senha, pasta (opcional) }
    """
    try:
        data = request.get_json(force=True)
        imap_host = data.get("imap_host", "")
        imap_port = int(data.get("imap_port", 993))
        email_addr = data.get("email", "")
        senha = data.get("senha", "")
        pasta = data.get("pasta", "INBOX")

        if not imap_host or not email_addr or not senha:
            return jsonify({"error": "Campos obrigatórios: imap_host, email, senha"}), 400

        emails = rpa.ler_emails_feedback(imap_host, imap_port, email_addr, senha, pasta)
        itens = rpa.emails_para_itens_conhecimento(emails)
        user_id = request.current_user.get("user_id", 1)
        resultado = rpa.importar_para_base(itens, user_id=user_id)

        return jsonify({
            "message": f"{len(emails)} e-mail(s) lido(s). {resultado['inseridos']} item(ns) importado(s).",
            "emails_lidos": len(emails),
            **resultado
        })
    except Exception as e:
        print(f"[ERRO] RPA emails: {e}")
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────
# Rotas Estáticas
# ──────────────────────────────────────────────

@app.route("/", methods=["GET"])
def home():
    from flask import redirect
    return redirect("/public/paginainicial.html")


@app.route("/public/<path:filename>")
def serve_public(filename):
    return send_from_directory("public", filename)


# ──────────────────────────────────────────────
# Inicialização
# ──────────────────────────────────────────────

if __name__ == "__main__":
    database.init_db()

    print("\n" + "=" * 50)
    print("FMPConnect Backend - Com Sistema de Admin")
    print("  Admin: http://localhost:5000/public/admin/login.html")
    print("=" * 50 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=True)
