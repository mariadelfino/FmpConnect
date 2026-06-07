# FMPConnect

Assistente virtual oficial da **Faculdade Municipal de Palhoça (FMP)**, desenvolvido por alunos do curso de Análise e Desenvolvimento de Sistemas (ADS) no iLAB.

O sistema permite que alunos obtenham informações sobre cursos, serviços, biblioteca, calendário acadêmico e muito mais — por texto ou por voz — diretamente no navegador.

---

## Funcionalidades

| Módulo | Descrição |
|--------|-----------|
| **Chat por texto** | Conversa com IA (Gemini 2.5 Flash) com histórico de sessão |
| **Chat por voz** | Fala com o assistente e escuta a resposta em áudio (TTS pt-BR) |
| **Modo acessibilidade** | Alto contraste, filtros para daltonismo, fonte para dislexia, redução de animações e ajuste de tamanho de texto |
| **Modo surdez** | Respostas com linguagem simplificada e visual |
| **Painel Admin** | Dashboard completo para professores, secretaria e administradores gerenciarem o conteúdo do chatbot |
| **Base de conhecimento** | Informações cadastradas no painel são usadas em tempo real pelo bot |
| **RPA** | Robô que raspa o site da FMP e lê e-mails de feedback automaticamente |

---

## Tecnologias

**Backend**
- Python 3.12 + Flask
- Google Gemini 2.5 Flash (IA)
- Edge TTS (síntese de voz pt-BR)
- SQLite (banco de dados)
- JWT (autenticação do painel admin)

**Frontend**
- HTML5, CSS3, JavaScript puro
- Web Speech API (reconhecimento de voz)

---

## Estrutura do projeto

```
FmpConnect/
├── app.py                  # Backend Flask — rotas da API
├── database.py             # Banco de dados SQLite e base de conhecimento
├── rpa.py                  # Módulo RPA (scraping e e-mails)
├── testes_sistema.py       # Suite de testes automatizados
├── .env.example            # Modelo de variáveis de ambiente
├── public/
│   ├── boasvindas.html
│   ├── paginainicial.html
│   ├── chat.html           # Chat por texto
│   ├── chat-voz.html       # Chat por voz
│   ├── feedback.html
│   ├── sobre.html
│   ├── admin/
│   │   ├── login.html      # Login do painel admin
│   │   ├── painel.html     # Painel admin completo
│   │   └── admin.css
│   └── assets/
│       ├── css/
│       ├── js/
│       └── images/
└── run.bat                 # Atalho para iniciar o servidor no Windows
```

---

## Como rodar localmente

### 1. Pré-requisitos

- Python 3.10+
- pip

### 2. Clone o repositório

```bash
git clone https://github.com/mariadelfino/FmpConnect.git
cd FmpConnect
```

### 3. Instale as dependências

```bash
pip install flask flask-cors python-dotenv pyjwt werkzeug edge-tts requests beautifulsoup4
```

### 4. Configure as variáveis de ambiente

Copie o arquivo de exemplo e preencha com suas chaves:

```bash
cp .env.example .env
```

Edite o `.env`:

```
GOOGLE_API_KEY=sua_chave_do_gemini_aqui
JWT_SECRET=uma_string_secreta_forte
```

> Obtenha sua chave Gemini em: https://aistudio.google.com/app/apikey

### 5. Inicie o servidor

```bash
python app.py
```

Ou no Windows, clique duas vezes em `run.bat`.

Acesse: **http://localhost:5000**

---

## Painel Admin

| URL | Descrição |
|-----|-----------|
| `/public/admin/login.html` | Login do painel |
| `/public/admin/painel.html` | Dashboard completo |

**Credencial padrão:**
- Usuário: `admin`
- Senha: `fmp@2024`

> ⚠️ Troque a senha após o primeiro acesso em **Minha Conta → Alterar Senha**.

**Papéis de usuário:**
- `admin` — acesso total (usuários, base de conhecimento, RPA)
- `editor` — acesso à base de conhecimento (professores e secretaria)

---

## RPA — Automação

O módulo RPA pode ser executado via painel admin ou linha de comando:

```bash
# Raspar informações do site da FMP
python rpa.py scrape

# Ler e-mails de feedback (requer configuração no .env)
python rpa.py email

# Executar tudo
python rpa.py tudo
```

Para leitura de e-mails, adicione ao `.env`:

```
FEEDBACK_IMAP_HOST=imap.gmail.com
FEEDBACK_EMAIL=seu_email@fmpsc.edu.br
FEEDBACK_PASSWORD=sua_senha_de_app
```

---

## Testes

Execute a suite completa de testes (53 testes cobrindo auth, segurança, páginas, chat, TTS, base de conhecimento, acessibilidade, RPA e painel admin):

```bash
python testes_sistema.py
```

---

## Segurança

- Chaves de API armazenadas apenas no `.env` (nunca commitado)
- Autenticação JWT em todas as rotas do painel admin
- Rota `/text/token` removida — a chave Gemini nunca é enviada ao browser
- Senhas armazenadas com hash (werkzeug scrypt)

---

## Equipe

Desenvolvido por alunos do iLAB — FMP ADS

| Nome | Papel |
|------|-------|
| Maria Fernanda Delfino | Back-end |
| Isabela | Front-end |

---

## Instituição

**Faculdade Municipal de Palhoça (FMP)**  
Rua João Pereira dos Santos, 99 — Ponte do Imaruim — Palhoça/SC  
(48) 3220-0376 | contato@fmpsc.edu.br | https://fmpsc.edu.br
