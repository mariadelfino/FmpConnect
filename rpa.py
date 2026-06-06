"""
FMPConnect — Módulo RPA (Robotic Process Automation)

Funções:
  1. scrape_site_fmp()  — Raspa notícias/avisos do site oficial da FMP e retorna lista de itens
  2. ler_emails_feedback(config) — Lê e-mails de uma caixa de feedback via IMAP
  3. importar_para_base(itens, user_id) — Insere itens novos na base de conhecimento do banco
"""

import re
import imaplib
import email
from email.header import decode_header
from datetime import datetime

import requests
from bs4 import BeautifulSoup

import database

# ──────────────────────────────────────────────────────────────────────────────
# 1. Scraping do site da FMP
# ──────────────────────────────────────────────────────────────────────────────

FMP_BASE = "https://fmpsc.edu.br"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _fetch(url: str, timeout: int = 15) -> BeautifulSoup | None:
    """Faz GET e devolve BeautifulSoup ou None em caso de erro."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=timeout)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as exc:
        print(f"[RPA] Erro ao acessar {url}: {exc}")
        return None


def scrape_site_fmp() -> list[dict]:
    """
    Raspa o site da FMP procurando notícias, avisos e editais.
    Retorna lista de dicts: {category, title, content, url}
    """
    resultados = []

    soup = _fetch(FMP_BASE)
    if not soup:
        return resultados

    # --- Notícias / posts na página inicial ---
    artigos = soup.select("article, .post, .entry, .news-item, .card")
    for art in artigos:
        titulo_el = art.select_one("h1, h2, h3, .title, .entry-title, .post-title")
        if not titulo_el:
            continue
        titulo = titulo_el.get_text(strip=True)
        if len(titulo) < 8:
            continue

        # Conteúdo: resumo ou parágrafo
        resumo_el = art.select_one("p, .excerpt, .summary, .entry-summary")
        conteudo = resumo_el.get_text(" ", strip=True) if resumo_el else titulo

        # Link para a notícia completa
        link_el = art.select_one("a[href]")
        url_noticia = ""
        if link_el:
            href = link_el["href"]
            url_noticia = href if href.startswith("http") else FMP_BASE + href

        # Detecta categoria pelo conteúdo/título
        categoria = _detectar_categoria(titulo + " " + conteudo)

        resultados.append({
            "category": categoria,
            "title": titulo[:120],
            "content": _limpar_texto(conteudo)[:800],
            "url": url_noticia,
        })

    # --- Tenta também a página de editais/processos seletivos ---
    for path in ["/editais", "/processo-seletivo", "/noticias", "/avisos"]:
        sub = _fetch(FMP_BASE + path)
        if not sub:
            continue
        for item in sub.select("article, .post, li.edital, .item-edital"):
            t_el = item.select_one("h1,h2,h3,a")
            if not t_el:
                continue
            titulo = t_el.get_text(strip=True)
            if len(titulo) < 8:
                continue
            conteudo = titulo
            p_el = item.select_one("p")
            if p_el:
                conteudo = p_el.get_text(" ", strip=True)
            categoria = _detectar_categoria(titulo)
            resultados.append({
                "category": categoria,
                "title": titulo[:120],
                "content": _limpar_texto(conteudo)[:800],
                "url": FMP_BASE + path,
            })

    # Remove duplicatas pelo título
    vistos = set()
    unicos = []
    for r in resultados:
        chave = r["title"].lower().strip()
        if chave not in vistos:
            vistos.add(chave)
            unicos.append(r)

    print(f"[RPA] {len(unicos)} itens encontrados no site da FMP.")
    return unicos


def _detectar_categoria(texto: str) -> str:
    texto_lower = texto.lower()
    if any(w in texto_lower for w in ["edital", "processo seletivo", "vestibular", "inscrição", "vaga"]):
        return "Vestibular"
    if any(w in texto_lower for w in ["calendário", "semestre", "recesso", "feriado", "prova"]):
        return "Calendário Acadêmico"
    if any(w in texto_lower for w in ["matrícula", "trancamento", "reopção"]):
        return "Matrícula"
    if any(w in texto_lower for w in ["biblioteca", "livro", "empréstimo"]):
        return "Biblioteca"
    if any(w in texto_lower for w in ["estágio", "tcb", "tcc", "trabalho de conclusão"]):
        return "Estágio"
    if any(w in texto_lower for w in ["bolsa", "auxílio", "financeiro", "gratuito"]):
        return "Financeiro"
    if any(w in texto_lower for w in ["evento", "palestra", "workshop", "semana"]):
        return "Eventos"
    return "Avisos"


def _limpar_texto(texto: str) -> str:
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


# ──────────────────────────────────────────────────────────────────────────────
# 2. Leitura de e-mails de feedback via IMAP
# ──────────────────────────────────────────────────────────────────────────────

def ler_emails_feedback(
    imap_host: str,
    imap_port: int,
    email_addr: str,
    senha: str,
    pasta: str = "INBOX",
    max_emails: int = 20,
    apenas_nao_lidos: bool = True,
) -> list[dict]:
    """
    Conecta via IMAP e lê e-mails de feedback.
    Retorna lista de dicts: {assunto, remetente, data, corpo}
    """
    emails_lidos = []

    try:
        conn = imaplib.IMAP4_SSL(imap_host, imap_port)
        conn.login(email_addr, senha)
        conn.select(pasta)

        criterio = "UNSEEN" if apenas_nao_lidos else "ALL"
        status, ids = conn.search(None, criterio)
        if status != "OK":
            print("[RPA] Nenhum e-mail encontrado.")
            conn.logout()
            return []

        ids_lista = ids[0].split()
        # Pega os mais recentes
        ids_recentes = ids_lista[-max_emails:]

        for eid in reversed(ids_recentes):
            _, data = conn.fetch(eid, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])

            # Decodifica assunto
            assunto_raw = msg.get("Subject", "")
            assunto_parts = decode_header(assunto_raw)
            assunto = ""
            for part, enc in assunto_parts:
                if isinstance(part, bytes):
                    assunto += part.decode(enc or "utf-8", errors="replace")
                else:
                    assunto += str(part)

            remetente = msg.get("From", "")
            data_msg = msg.get("Date", "")

            # Extrai corpo (texto plano)
            corpo = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or "utf-8"
                            corpo += payload.decode(charset, errors="replace")
                        break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or "utf-8"
                    corpo = payload.decode(charset, errors="replace")

            emails_lidos.append({
                "assunto": assunto.strip(),
                "remetente": remetente,
                "data": data_msg,
                "corpo": corpo.strip()[:2000],
            })

        conn.logout()
        print(f"[RPA] {len(emails_lidos)} e-mail(s) de feedback lido(s).")
    except Exception as exc:
        print(f"[RPA] Erro ao ler e-mails: {exc}")

    return emails_lidos


def emails_para_itens_conhecimento(emails: list[dict]) -> list[dict]:
    """
    Converte e-mails de feedback em itens de conhecimento.
    Cada e-mail vira um item na categoria 'Feedbacks'.
    """
    itens = []
    for e in emails:
        assunto = e.get("assunto") or "Feedback recebido"
        corpo = e.get("corpo", "").strip()
        if not corpo:
            continue
        titulo = assunto[:120]
        conteudo = f"Feedback de {e.get('remetente','')}: {corpo}"[:800]
        itens.append({
            "category": "Feedbacks",
            "title": titulo,
            "content": conteudo,
        })
    return itens


# ──────────────────────────────────────────────────────────────────────────────
# 3. Importação para a base de conhecimento
# ──────────────────────────────────────────────────────────────────────────────

def importar_para_base(itens: list[dict], user_id: int = 1) -> dict:
    """
    Recebe lista de {category, title, content} e insere no banco,
    ignorando títulos que já existem (evita duplicatas).
    Retorna {'inseridos': N, 'ignorados': M}
    """
    if not itens:
        return {"inseridos": 0, "ignorados": 0}

    conn = database.get_db()
    inseridos = 0
    ignorados = 0

    for item in itens:
        categoria = (item.get("category") or "Geral").strip()
        titulo = (item.get("title") or "").strip()
        conteudo = (item.get("content") or "").strip()

        if not titulo or not conteudo:
            ignorados += 1
            continue

        existe = conn.execute(
            "SELECT id FROM knowledge_items WHERE title=?", (titulo,)
        ).fetchone()

        if existe:
            ignorados += 1
            continue

        conn.execute(
            "INSERT INTO knowledge_items (category, title, content, created_by) VALUES (?, ?, ?, ?)",
            (categoria, titulo, conteudo, user_id),
        )
        inseridos += 1

    conn.commit()
    conn.close()
    print(f"[RPA] Importados: {inseridos} | Ignorados (duplicatas): {ignorados}")
    return {"inseridos": inseridos, "ignorados": ignorados}


# ──────────────────────────────────────────────────────────────────────────────
# Execução direta (teste manual)
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== RPA FMPConnect ===")
    print("\n[1] Raspando site da FMP...")
    itens = scrape_site_fmp()
    if itens:
        resultado = importar_para_base(itens, user_id=1)
        print(f"    Resultado: {resultado}")
    else:
        print("    Nenhum item encontrado no site.")
