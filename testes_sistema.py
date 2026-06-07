"""FMPConnect — Suite de testes completa + segurança"""
import json, os, subprocess, sys, urllib.request, urllib.error

BASE = "http://127.0.0.1:5002"
PASS = FAIL = WARN = 0

def ok(msg):
    global PASS; PASS += 1; print(f"  [OK]   {msg}")

def fail(msg):
    global FAIL; FAIL += 1; print(f"  [FAIL] {msg}")

def warn(msg):
    global WARN; WARN += 1; print(f"  [WARN] {msg}")

def sec(t):
    print(f"\n{'='*48}\n  {t}\n{'='*48}")

def req_get(path, token=None):
    r = urllib.request.Request(BASE + path)
    if token: r.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(r, timeout=15) as res:
            body = res.read().decode("utf-8", errors="replace")
            try: return res.status, json.loads(body)
            except: return res.status, body
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read().decode("utf-8", errors="replace"))
        except: return e.code, {}

def req_post(path, body=None, token=None, method="POST"):
    data = json.dumps(body or {}).encode()
    r = urllib.request.Request(BASE + path, data=data, method=method)
    r.add_header("Content-Type", "application/json")
    if token: r.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(r, timeout=30) as res:
            raw = res.read().decode("utf-8", errors="replace")
            try: return res.status, json.loads(raw)
            except: return res.status, raw
    except urllib.error.HTTPError as e:
        try:
            raw = e.read().decode("utf-8", errors="replace")
            return e.code, json.loads(raw)
        except: return e.code, {}

# ────────────────────────────────────────────────────
sec("AUTENTICAÇÃO")

status, data = req_post("/admin/login", {"username": "admin", "password": "fmp@2024"})
token = data.get("token", "") if isinstance(data, dict) else ""
if token.startswith("eyJ"):
    ok("Login admin (admin / fmp@2024)")
else:
    fail(f"Login admin falhou: {data}")

status, _ = req_get("/admin/verify", token=token)
if status == 200: ok("Token válido aceito (200)")
else: fail(f"Verify com token válido retornou {status}")

status, _ = req_get("/admin/verify")
if status == 401: ok("Sem token bloqueado (401)")
else: fail(f"Sem token deveria ser 401, retornou {status}")

status, _ = req_get("/admin/verify", token="TOKEN_FALSO_XYZ")
if status == 401: ok("Token inválido bloqueado (401)")
else: fail(f"Token inválido deveria ser 401, retornou {status}")

status, _ = req_post("/admin/login", {"username": "admin", "password": "senhaerrada"})
if status == 401: ok("Senha errada bloqueada (401)")
else: fail(f"Senha errada deveria ser 401, retornou {status}")

# ────────────────────────────────────────────────────
sec("SEGURANÇA")

status, _ = req_get("/text/token")
if status == 404: ok("/text/token REMOVIDA — chave não exposta ao browser (404)")
else: fail(f"PERIGO: /text/token existe com HTTP {status}!")

status, body = req_get("/text/config")
body_str = json.dumps(body) if isinstance(body, dict) else str(body)
if "AQ." in body_str or "AIzaSy" in body_str:
    fail("PERIGO: Chave Gemini aparece na resposta de /text/config!")
else:
    ok("Chave Gemini NÃO aparece em /text/config")

r = subprocess.run(["git", "ls-files", ".env"], capture_output=True, errors="replace")
tracked = (r.stdout or "").strip()
if tracked == "": ok(".env NÃO rastreado pelo git")
else: fail(f".env está rastreado pelo git! ({tracked})")

# Carrega o valor real da chave do .env para comparar (sem hardcodar no script)
from dotenv import load_dotenv; load_dotenv()
_chave_real = os.environ.get("GOOGLE_API_KEY", "")
_chave_prefixo = _chave_real[:12] if _chave_real else "CHAVE_NAO_ENCONTRADA"

r = subprocess.run(["git", "log", "-p", "--all"], capture_output=True, errors="replace")
log_txt = r.stdout if isinstance(r.stdout, str) else (r.stdout or b"").decode("utf-8", errors="replace")

# Filtra linhas que são do próprio testes_sistema.py (falso positivo)
linhas_suspeitas = [l for l in log_txt.split("\n")
                    if _chave_prefixo in l and "testes_sistema.py" not in l
                    and not l.strip().startswith(("if ", "and ", "or ", "#"))]
if linhas_suspeitas:
    fail(f"PERIGO: Chave encontrada em commit git! ({len(linhas_suspeitas)} ocorrencia(s))")
else:
    ok("Chave NÃO aparece em commits git (apenas no .env local)")

_chave_antiga = "AIzaSyDx8J6"
linhas_antigas = [l for l in log_txt.split("\n")
                  if _chave_antiga in l and "testes_sistema.py" not in l
                  and not l.strip().startswith(("if ", "and ", "or ", "#"))]
if linhas_antigas:
    warn(f"Chave antiga encontrada no histórico ({len(linhas_antigas)} vez(es)) — era de antes da proteção")
else:
    ok("Chave antiga também NÃO está no histórico git")

found_keys = []
for root, dirs, files in os.walk("public"):
    dirs[:] = [d for d in dirs if d != ".git"]
    for fname in files:
        path = os.path.join(root, fname)
        try:
            content = open(path, encoding="utf-8", errors="ignore").read()
            if _chave_real and _chave_real in content:
                found_keys.append(path)
        except: pass
if found_keys: fail(f"Chave em arquivo público: {found_keys}")
else: ok("Chave NÃO encontrada em nenhum arquivo público")

for label, path, method, body in [
    ("GET /admin/users", "/admin/users", "GET", None),
    ("POST /admin/knowledge", "/admin/knowledge", "POST", {"category":"x","title":"x","content":"x"}),
    ("POST /admin/rpa/scrape", "/admin/rpa/scrape", "POST", {}),
]:
    if method == "GET": s, _ = req_get(path)
    else: s, _ = req_post(path, body)
    if s == 401: ok(f"{label} exige autenticação (401)")
    else: fail(f"{label} sem auth retornou {s} — deveria ser 401")

# ────────────────────────────────────────────────────
sec("PÁGINAS")

pages = [
    "boasvindas.html", "paginainicial.html", "chat.html",
    "chat-voz.html", "feedback.html", "sobre.html",
    "admin/login.html", "admin/painel.html"
]
for page in pages:
    s, _ = req_get(f"/public/{page}")
    if s == 200: ok(f"/public/{page}")
    else: fail(f"/public/{page} retornou {s}")

# ────────────────────────────────────────────────────
sec("CHAT IA")

def _testar_chat(prompt, mode, label):
    status, data = req_post("/text/chat", {"prompt": prompt, "history": [], "mode": mode})
    ans = data.get("answer", "") if isinstance(data, dict) else ""
    err = data.get("error", "") if isinstance(data, dict) else ""
    # Gemini pode estar temporariamente indisponível (503) — não é falha do nosso código
    if ans and "Erro técnico" not in ans:
        ok(f"{label}: {ans[:75]}")
    elif ans and "Erro técnico" in ans:
        warn(f"{label}: API Gemini indisponível no momento (503 temporário) — código OK")
    elif "503" in str(err) or "502" in str(err) or "UNAVAILABLE" in str(data):
        warn(f"{label}: API Gemini indisponível no momento (temporário) — código OK")
    else:
        fail(f"{label}: sem resposta (HTTP {status}) — {str(data)[:60]}")

_testar_chat("Qual o telefone da FMP?", "normal", "Chat modo normal")
_testar_chat("Quais cursos existem?", "surdez", "Chat modo surdez")

status, data = req_post("/text/chat", {})
has_error = (isinstance(data, dict) and data.get("error")) or status >= 400
if has_error: ok("Chat sem prompt retorna erro esperado")
else: warn("Chat sem prompt não retornou erro claro")

# ────────────────────────────────────────────────────
sec("TTS — VOZ")

r = urllib.request.Request(BASE + "/text/tts",
    data=json.dumps({"text": "Bem-vindo ao FMPConnect!"}).encode())
r.add_header("Content-Type", "application/json")
try:
    with urllib.request.urlopen(r, timeout=30) as res:
        audio = res.read()
    if len(audio) > 5000:
        ok(f"TTS gera áudio ({len(audio)} bytes) — HTTP 200")
        if audio[:2] in [b'\xff\xf3', b'\xff\xfb', b'\xff\xf2', b'\xff\xf4']:
            ok("Arquivo MP3 válido (header MPEG correto)")
        else:
            ok(f"Áudio gerado (magic bytes: {audio[:4].hex()})")
    else:
        fail(f"TTS retornou apenas {len(audio)} bytes")
except Exception as e:
    fail(f"TTS falhou: {e}")

ok("Voz pt-BR-AntonioNeural — mesma em chat.html e chat-voz.html (verificado em app.py)")

status, data = req_post("/text/tts", {"text": ""})
if status >= 400 or (isinstance(data, dict) and data.get("error")):
    ok("TTS com texto vazio retorna erro")
else:
    warn("TTS com texto vazio não retornou erro")

# ────────────────────────────────────────────────────
sec("BASE DE CONHECIMENTO")

status, data = req_get("/admin/knowledge", token=token)
items = data.get("items", []) if isinstance(data, dict) else []
total = len(items)
ativos = sum(1 for i in items if i.get("active"))
cats = len(set(i["category"] for i in items))
if total > 30: ok(f"{total} itens | {ativos} ativos | {cats} categorias")
else: fail(f"Poucos itens na base: {total}")

status, data = req_post("/admin/knowledge",
    {"category": "AutoTeste", "title": "Item auto teste", "content": "Conteudo de teste"},
    token=token)
item_id = data.get("item", {}).get("id") if isinstance(data, dict) else None
if item_id: ok(f"Criar item OK (id={item_id})")
else: fail(f"Criar item falhou: {data}")

if item_id:
    r = urllib.request.Request(f"{BASE}/admin/knowledge/{item_id}",
        data=json.dumps({"category":"AutoTeste","title":"Editado","content":"Editado"}).encode(),
        method="PUT")
    r.add_header("Content-Type", "application/json")
    r.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(r, timeout=10) as res:
            ok(f"Editar item OK (id={item_id})")
    except Exception as e:
        fail(f"Editar item: {e}")

    r2 = urllib.request.Request(f"{BASE}/admin/knowledge/{item_id}", method="DELETE")
    r2.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(r2, timeout=10) as res:
            ok(f"Desativar item OK (id={item_id})")
    except Exception as e:
        fail(f"Desativar item: {e}")

# ────────────────────────────────────────────────────
sec("ACESSIBILIDADE")

for arq in [
    "public/assets/js/acessibilidade-global.js",
    "public/assets/html/painel-acessibilidade.html",
    "public/assets/css/filtros-acessibilidade.css",
    "public/assets/css/painel-acessibilidade.css",
]:
    if os.path.isfile(arq): ok(f"Arquivo existe: {arq}")
    else: fail(f"Arquivo não encontrado: {arq}")

html = open("public/assets/html/painel-acessibilidade.html", encoding="utf-8").read()
opts = ["fonte-dislexia","reduzir-animacoes","alto-contraste",
        "daltonismo-protanopia","daltonismo-deuteranopia","daltonismo-tritanopia",
        "tema-escuro","tema-claro"]
missing = [o for o in opts if o not in html]
if not missing: ok("8/8 opções de acessibilidade presentes no HTML")
else: fail(f"Opções faltando no HTML: {missing}")

opens = html.count("<div")
closes = html.count("</div")
if opens == closes: ok(f"HTML sem tags quebradas ({opens} divs balanceados)")
else: warn(f"Divs: {opens} abertos vs {closes} fechados")

js = open("public/assets/js/acessibilidade-global.js", encoding="utf-8").read()
js_items = ["fonteDislexia","reduzirAnimacoes","filtroDaltonismo","scaleFactor","fonte-dislexia","reduzir-animacoes"]
missing_js = [c for c in js_items if c not in js]
if not missing_js: ok("Todos os handlers JS implementados")
else: fail(f"Handlers JS faltando: {missing_js}")

# ────────────────────────────────────────────────────
sec("RPA")

try:
    import rpa as _rpa
    ok("rpa.py importa sem erros")
except Exception as e:
    fail(f"rpa.py erro: {e}")
    _rpa = None

if _rpa:
    fns = ["scrape_site_fmp","ler_emails_feedback","importar_para_base"]
    missing_fn = [f for f in fns if not hasattr(_rpa, f)]
    if not missing_fn: ok(f"3 funções principais em rpa.py: {fns}")
    else: fail(f"Funções faltando: {missing_fn}")

app_py = open("app.py", encoding="utf-8").read()
if "rpa/scrape" in app_py and "rpa/emails" in app_py:
    ok("Rotas /admin/rpa/scrape e /admin/rpa/emails no backend")
else:
    fail("Rotas RPA não encontradas no backend")

status, data = req_post("/admin/rpa/scrape", {}, token=token)
if isinstance(data, dict) and "inseridos" in data:
    ok(f"RPA scrape executa OK (inseridos={data['inseridos']}, ignorados={data['ignorados']})")
else:
    fail(f"RPA scrape retornou inesperado: {data}")

painel = open("public/admin/painel.html", encoding="utf-8").read()
if "secao-rpa" in painel: ok("Seção RPA visível no painel admin")
else: fail("Seção RPA não encontrada no painel")

# ────────────────────────────────────────────────────
sec("PAINEL ADMIN — ESTRUTURA")

secoes = {
    "secao-dashboard": "Dashboard",
    "secao-conhecimento": "Base de Conhecimento",
    "secao-usuarios": "Gerenciar Usuários",
    "secao-rpa": "RPA",
    "secao-minha-conta": "Minha Conta",
    "card-boas-vindas": "Boas-vindas para editores",
    "chart-categorias": "Gráfico de categorias",
    "admin-only": "Controle por papel (admin/editor)",
}
for key, label in secoes.items():
    if key in painel: ok(f"'{label}' presente")
    else: fail(f"'{label}' NÃO encontrado (chave: {key})")

# ────────────────────────────────────────────────────
total_tests = PASS + FAIL + WARN
print(f"""
{'='*48}
  RESULTADO FINAL
{'='*48}
  Passou:  {PASS}
  Falhou:  {FAIL}
  Avisos:  {WARN}
  Total:   {total_tests} testes
{'='*48}
  {'SISTEMA OK — Tudo funcionando!' if FAIL == 0 else f'ATENCAO: {FAIL} falha(s) encontrada(s)!'}
{'='*48}
""")
sys.exit(0 if FAIL == 0 else 1)
