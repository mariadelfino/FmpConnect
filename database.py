import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'fmpconnect.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'editor',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        active INTEGER DEFAULT 1
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS knowledge_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_by INTEGER REFERENCES users(id),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        active INTEGER DEFAULT 1
    )''')

    existing = c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if existing == 0:
        c.execute(
            'INSERT INTO users (username, email, name, password_hash, role) VALUES (?, ?, ?, ?, ?)',
            ('admin', 'admin@fmpsc.edu.br', 'Administrador',
             generate_password_hash('fmp@2024'), 'admin')
        )
        print("=" * 50)
        print("ADMIN CRIADO! Login: admin | Senha: fmp@2024")
        print("TROQUE A SENHA APOS O PRIMEIRO ACESSO!")
        print("=" * 50)

    # Seed de conhecimento inicial — só insere se a tabela estiver vazia
    existentes = c.execute('SELECT COUNT(*) FROM knowledge_items').fetchone()[0]
    if existentes == 0:
        seed_items = [
            # ── Matrícula ──────────────────────────────────────────────
            ('Matrícula', 'Como fazer a matrícula',
             'A matrícula é feita presencialmente na secretaria acadêmica ou pelo Portal do Aluno (SGA) em http://sga.fmpsc.edu.br/portal. '
             'O prazo é divulgado no início de cada semestre pelo site oficial. '
             'Documentos necessários: RG, CPF, comprovante de residência e histórico escolar do ensino médio (para calouros).'),

            ('Matrícula', 'Trancamento de matrícula',
             'O trancamento pode ser solicitado na secretaria acadêmica dentro do prazo estabelecido no calendário semestral. '
             'O aluno deve preencher o requerimento disponível na secretaria. '
             'O trancamento é permitido por até 2 semestres consecutivos. Após esse período, o aluno é desligado.'),

            ('Matrícula', 'Reopção de curso (mudança de curso)',
             'A reopção de curso é permitida para alunos regularmente matriculados. '
             'O processo ocorre uma vez por ano, com edital publicado no site oficial. '
             'É necessário cumprir os requisitos de aproveitamento definidos no edital.'),

            # ── Financeiro ─────────────────────────────────────────────
            ('Financeiro', 'A FMP é gratuita?',
             'Sim. A FMP (Faculdade Municipal de Palhoça) é uma instituição pública municipal, '
             'portanto NÃO cobra mensalidade. O ensino é 100% gratuito para todos os alunos aprovados '
             'no processo seletivo. Há possibilidade de auxílio estudantil para alunos em situação de vulnerabilidade socioeconômica.'),

            ('Financeiro', 'Auxílio estudantil e bolsas',
             'A FMP oferece auxílios estudantis para alunos em situação de vulnerabilidade socioeconômica, '
             'como auxílio transporte e auxílio alimentação. '
             'Os editais são publicados periodicamente no site oficial. '
             'Informações: setor de assistência estudantil pelo e-mail contato@fmpsc.edu.br.'),

            # ── Estágio ────────────────────────────────────────────────
            ('Estágio', 'Como realizar estágio na FMP',
             'O estágio é coordenado pela Coordenação de Estágios de cada curso. '
             'O aluno deve apresentar o Termo de Compromisso de Estágio (TCE) antes de iniciar. '
             'Estágios podem ser obrigatórios (previstos na grade curricular) ou não obrigatórios. '
             'Documentação necessária: TCE preenchido pela empresa, plano de atividades e apólice de seguro. '
             'Procure a secretaria ou o coordenador do seu curso para mais informações.'),

            ('Estágio', 'Estágio obrigatório — prazos e documentos',
             'O estágio obrigatório deve ser realizado conforme previsto no PPC (Projeto Pedagógico do Curso). '
             'O aluno deve entregar relatório de estágio ao final. '
             'Contato para dúvidas: secretaria acadêmica ou coordenação do curso.'),

            # ── TCC ────────────────────────────────────────────────────
            ('TCC', 'Como funciona o TCC na FMP',
             'O TCC (Trabalho de Conclusão de Curso) é obrigatório para os cursos de Bacharelado e Licenciatura. '
             'Os cursos Tecnólogos possuem projeto integrador no lugar do TCC. '
             'O aluno deve escolher um orientador entre os professores do curso e seguir o cronograma semestral. '
             'As normas de formatação seguem a ABNT. Consulte o regulamento específico do seu curso na secretaria.'),

            ('TCC', 'Prazo e defesa do TCC',
             'O prazo de entrega e a data de defesa são divulgados no início de cada semestre pelo coordenador do curso. '
             'A banca é composta pelo orientador e dois avaliadores. '
             'Após aprovação, o aluno deve entregar a versão final encadernada e digital.'),

            # ── Coordenações ───────────────────────────────────────────
            ('Coordenações', 'Coordenação de Administração',
             'Curso: Administração (Bacharelado) — Turnos: Matutino e Noturno. '
             'Para dúvidas sobre grade curricular, aproveitamento de disciplinas e orientação acadêmica, '
             'procure a coordenação do curso na secretaria ou envie e-mail para contato@fmpsc.edu.br informando o curso.'),

            ('Coordenações', 'Coordenação de ADS (Análise e Desenvolvimento de Sistemas)',
             'Curso: Análise e Desenvolvimento de Sistemas (Tecnólogo) — Turno: Matutino. '
             'Responsável pelo iLAB: Profa. Daniela Amorim (iLAB@fmpsc.edu.br). '
             'Para dúvidas acadêmicas, procure a coordenação na secretaria.'),

            ('Coordenações', 'Coordenação de Pedagogia',
             'Curso: Pedagogia (Licenciatura) — Turnos: Matutino e Noturno. '
             'O curso conta com Laboratório de Práticas Pedagógicas / Brinquedoteca. '
             'Responsável: Profa. Juliane Di Paula Queiroz Odinino (juliane.odinino@fmpsc.edu.br).'),

            ('Coordenações', 'Coordenação de Processos Gerenciais',
             'Curso: Processos Gerenciais (Tecnólogo) — Turno: Matutino. '
             'Para dúvidas sobre grade curricular e orientação acadêmica, '
             'procure a coordenação do curso na secretaria.'),

            # ── Serviços ───────────────────────────────────────────────
            ('Serviços', 'Portal do Aluno (SGA) — notas e faltas',
             'O Portal do Aluno da FMP é o SGA, acessível em http://sga.fmpsc.edu.br/portal. '
             'Lá o aluno pode consultar notas, faltas, emitir declarações, solicitar documentos e acompanhar seu histórico acadêmico. '
             'Login com matrícula e senha fornecidos na secretaria no momento da matrícula.'),

            ('Serviços', 'Emissão de declaração e histórico',
             'Declarações de matrícula, histórico escolar e outros documentos acadêmicos podem ser solicitados: '
             '1) Diretamente no Portal do Aluno (SGA) em http://sga.fmpsc.edu.br/portal (para documentos digitais). '
             '2) Presencialmente na secretaria acadêmica. '
             'O prazo para emissão de documentos impressos é de até 5 dias úteis.'),

            ('Serviços', 'Xerox e impressão',
             'A FMP dispõe de serviço de xerox e impressão para alunos nas dependências da instituição. '
             'Consulte o valor e disponibilidade diretamente na secretaria ou cantina.'),

            # ── Ouvidoria ──────────────────────────────────────────────
            ('Ouvidoria', 'Como registrar reclamação ou sugestão',
             'A FMP possui Ouvidoria para recebimento de reclamações, sugestões e elogios. '
             'Contato: pelo site oficial https://fmpsc.edu.br/ na seção Ouvidoria, '
             'ou presencialmente na instituição. '
             'O prazo de resposta é de até 15 dias úteis.'),

            # ── Calendário Acadêmico ───────────────────────────────────
            ('Calendário Acadêmico', 'Onde encontrar o calendário acadêmico',
             'O calendário acadêmico semestral com todas as datas (início/fim de semestre, provas, recessos, feriados) '
             'é publicado no site oficial da FMP: https://fmpsc.edu.br/. '
             'Acesse a seção "Acadêmico" ou "Calendário". '
             'O calendário é divulgado antes do início de cada semestre letivo.'),

            ('Calendário Acadêmico', 'Período de provas e avaliações',
             'As datas das avaliações parciais e finais são definidas por cada professor e comunicadas no início do semestre. '
             'As provas finais geralmente ocorrem nas últimas semanas do semestre letivo, conforme o calendário acadêmico oficial. '
             'Consulte o site https://fmpsc.edu.br/ ou o SGA para informações atualizadas.'),

            # ── Vestibular / Ingresso ──────────────────────────────────
            ('Vestibular', 'Como se inscrever no vestibular da FMP',
             'As inscrições para o Processo Seletivo (Vestibular) da FMP são realizadas pelo site oficial https://fmpsc.edu.br/ '
             'na seção "Processo Seletivo" ou "Vestibular". '
             'As inscrições são gratuitas. '
             'O candidato deve estar atento aos editais publicados com as datas e regras de cada processo seletivo.'),

            ('Vestibular', 'Vagas remanescentes',
             'Além do Vestibular principal, a FMP abre editais de Vagas Remanescentes ao longo do ano. '
             'As vagas remanescentes são destinadas a candidatos que não participaram do processo seletivo principal '
             'ou cujas vagas não foram preenchidas. '
             'Fique atento ao site https://fmpsc.edu.br/ para os editais de vagas remanescentes.'),
        ]

        c.executemany(
            'INSERT INTO knowledge_items (category, title, content, created_by) VALUES (?, ?, ?, 1)',
            seed_items
        )
        print(f"✅ {len(seed_items)} itens de conhecimento iniciais inseridos.")

    conn.commit()
    conn.close()


def get_knowledge_items(active_only=True):
    conn = get_db()
    if active_only:
        rows = conn.execute(
            'SELECT * FROM knowledge_items WHERE active=1 ORDER BY category, title'
        ).fetchall()
    else:
        rows = conn.execute(
            '''SELECT ki.*, u.name as creator_name
               FROM knowledge_items ki
               LEFT JOIN users u ON ki.created_by = u.id
               ORDER BY ki.updated_at DESC'''
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def build_dynamic_system_instruction(base_instruction):
    items = get_knowledge_items(active_only=True)
    if not items:
        return base_instruction

    categories = {}
    for item in items:
        cat = item['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    extra = "\n\n📋 INFORMAÇÕES ADICIONAIS (Atualizadas pela Secretaria Acadêmica):\n"
    for cat, cat_items in categories.items():
        extra += f"\n[{cat.upper()}]\n"
        for item in cat_items:
            extra += f"- {item['title']}: {item['content']}\n"

    return base_instruction + extra
