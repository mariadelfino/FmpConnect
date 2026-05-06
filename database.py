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
