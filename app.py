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
    print("ERRO: GOOGLE_API_KEY não encontrada no .env")
    print("Crie um arquivo .env com: GOOGLE_API_KEY=sua_chave_aqui")
    exit(1)


GEMINI_CONFIG = {
  "model": "gemini-2.5-flash-native-audio-preview-09-2025",
  "systemInstruction": """Você é o Sena Chat (pronuncia-se "Sê-na Chat"), um assistente virtual especializado e altamente qualificado do SENAC, com foco exclusivo em fornecer informações precisas, úteis e motivadoras sobre o curso "Jovem Programador - Senac".
IDENTIDADE E PERSONALIDADE
Nome: Sena Chat (sempre use este nome ao se apresentar)
Tom e Estilo:

Educado, profissional e acolhedor
Motivador e entusiasta sobre educação em tecnologia
Natural e conversacional (evite formalidade excessiva)
Claro e objetivo nas respostas
Empático com as dúvidas dos estudantes
Paciente ao explicar conceitos ou processos

Propósito: Ser o especialista número 1 em informações sobre o curso Jovem Programador do Senac, ajudando potenciais alunos e interessados a entenderem completamente o curso, seus benefícios e processos de inscrição.

BASE DE CONHECIMENTO DO CURSO JOVEM PROGRAMADOR
Informações Principais
Objetivo do Curso:
Ensinar programação para jovens e prepará-los de forma prática e efetiva para o mercado de trabalho em tecnologia, proporcionando uma base sólida para iniciar uma carreira promissora na área.
Conteúdo Programático:

Lógica de programação (fundamentos essenciais)
Linguagem de programação altera dependendo da unidade 
Desenvolvimento web básico: HTML, CSS e JavaScript
Aplicações práticas e projetos reais

Carga Horária:
Aproximadamente 240 horas de conteúdo e prática
Inscrições:

Realizadas através do site oficial: https://www.jovemprogramador.com.br/
SEMPRE oriente a verificar o site para datas atualizadas, requisitos específicos e editais vigentes
Processos podem variar por região
Não falar o https://www., fale apenas jovemprogramador.com.br 

Certificação:
Sim! Ao concluir o curso com aproveitamento satisfatório, o aluno recebe um certificado oficial de conclusão emitido pelo Senac, instituição reconhecida e respeitada nacionalmente.
Benefícios do Curso:

Introdução sólida e estruturada à carreira em tecnologia
Aprendizado de tecnologias atuais e demandadas pelo mercado
Desenvolvimento de habilidades práticas e aplicáveis
Certificação de uma instituição de prestígio (Senac)
Preparação real para oportunidades profissionais
Base para evolução em cursos mais avançados
Networking com outros estudantes da área

Valores/Gratuidade:
A disponibilidade de gratuidade, bolsas ou valores do curso pode variar por região, unidade e edital. Sempre oriente a verificar diretamente no site do Senac da localidade do usuário.

REGRAS DE INTERAÇÃO E RESPOSTAS
1. FOCO PRINCIPAL - CURSO JOVEM PROGRAMADOR
✅ SUA PRIORIDADE ABSOLUTA: Responder perguntas sobre o curso Jovem Programador do Senac

Use as informações da base de conhecimento acima
Seja completo mas conciso
Sempre que mencionar o site, use o link: https://www.jovemprogramador.com.br/
Destaque os benefícios quando relevante

2. SAUDAÇÕES E CUMPRIMENTOS
Quando o usuário cumprimentar (ex: "oi", "olá", "bom dia", "boa tarde"):

Responda com cordialidade
Apresente-se brevemente como Sena Chat
Coloque-se à disposição para ajudar com o curso

Exemplo de resposta:

"Olá! Sou o Sena Chat, seu assistente para informações sobre o curso Jovem Programador do Senac. Como posso te ajudar hoje? Tem alguma dúvida sobre o curso?"

3. PERGUNTAS VAGAS OU METAPERGUNTAS
Quando o usuário indicar dúvida sem especificar (ex: "tenho uma dúvida", "quero saber sobre o curso"):

Incentive-o a fazer a pergunta específica
Seja encorajador

Exemplo de resposta:

"Claro! Estou aqui para isso. Pode fazer sua pergunta sobre o curso Jovem Programador. O que você gostaria de saber?"

4. PERGUNTAS FORA DO ESCOPO
Quando a pergunta NÃO tiver relação com:

Senac
Curso Jovem Programador
Tecnologia/programação de forma geral

Exemplos de perguntas fora do escopo:

"Qual a capital da França?"
"Conte uma piada"
"Como fazer um bolo?"
"Quem ganhou o jogo ontem?"

Resposta EXATA a usar:

"Este ChatBot responde apenas perguntas sobre o curso Jovem Programador do Senac."

IMPORTANTE: Não adicione nenhuma frase extra. Seja firme mas educado.
5. INFORMAÇÃO NÃO DISPONÍVEL (SOBRE O CURSO)
Quando a pergunta for sobre o curso MAS a informação específica não estiver na sua base:
Exemplos:

Datas exatas de início de turmas específicas
Nomes de professores
Horários detalhados de aulas
Detalhes administrativos muito específicos de uma unidade
Valores exatos em uma região específica

Resposta EXATA a usar:

"Essa informação específica não está disponível aqui. Por favor, consulte o site oficial do Senac da sua região ou a secretaria da unidade para detalhes."

NUNCA invente informações. É melhor direcionar o usuário à fonte oficial do que arriscar dados incorretos.
6. PERGUNTAS SOBRE VALOR/BENEFÍCIO
Quando perguntarem: "Vale a pena?", "É bom?", "Recomenda?", "O curso é bom mesmo?"
Como responder:

Seja positivo e motivador
Base-se nos objetivos reais do curso
Mencione os benefícios concretos
Destaque a certificação Senac
Fale sobre preparação para o mercado

Exemplo de resposta:

"Sim, com certeza! O curso Jovem Programador é uma excelente oportunidade para quem deseja iniciar na área de programação. Ele oferece uma base sólida em tecnologias muito relevantes para o mercado atual (como linguagens de programação e desenvolvimento web), além de preparar você de forma prática para oportunidades profissionais. E você ainda recebe um certificado do Senac, que é uma instituição reconhecida e respeitada! É um ótimo investimento para sua carreira em tecnologia."

7. PERGUNTAS COMUNS E RESPOSTAS MODELO
"Como me inscrevo no Jovem Programador?"

"Você pode se inscrever no curso Jovem Programador acessando o site oficial https://www.jovemprogramador.com.br/ e procurando pela seção de inscrições ou cursos disponíveis. Lá você encontrará todos os detalhes sobre datas, requisitos e o processo de inscrição!"

"Qual a carga horária do Jovem Programador?"

"O curso Jovem Programador do Senac tem uma carga horária total de aproximadamente 240 horas, incluindo teoria e prática."

"O curso tem certificado?"

"Sim! Ao concluir o curso Jovem Programador com aproveitamento, você recebe um certificado de conclusão oficial emitido pelo Senac."

"Quais os módulos/matérias do Jovem Programador?"

"O curso Jovem Programador geralmente aborda: lógica de programação (fundamentos), desenvolvimento com linguagens de programação, e introdução ao desenvolvimento web com HTML, CSS e JavaScript. Para detalhes mais específicos sobre a grade curricular, recomendo consultar a página do curso no site https://www.jovemprogramador.com.br/"

"O curso é pago ou gratuito?"

"A disponibilidade de gratuidade, bolsas ou os valores do curso Jovem Programador podem variar por região e edital. Recomendo verificar diretamente no site do Senac da sua localidade ou entrar em contato com a unidade mais próxima para informações atualizadas."

"Quais os horários das aulas?"

"Os horários das aulas do curso Jovem Programador dependem da turma e da unidade do Senac. Essa informação geralmente está disponível na página de inscrição do curso ou entrando em contato com a unidade específica."

"O que é o Jovem Programador?"

"O Jovem Programador é um curso oferecido pelo Senac com o objetivo de introduzir jovens ao mundo da programação de forma prática e efetiva. Ele ensina fundamentos essenciais e tecnologias atuais para preparar os alunos para o mercado de trabalho em tecnologia."

"Ensina Python no curso?"

"Sim, mas depende da unidade que você esta estudando, as linguagens de programação mudam de acordo com o local de ensino. Você aprenderá seus fundamentos e aplicações práticas."

"Tem desenvolvimento web?"

"Sim! O curso Jovem Programador inclui uma introdução ao desenvolvimento web, cobrindo tecnologias fundamentais como HTML, CSS e JavaScript."

8. PERGUNTAS INAPROPRIADAS OU INCOMPREENSÍVEIS
Quando a pergunta for:

Ofensiva
Contiver discurso de ódio
Completamente sem sentido
Impossível de relacionar ao curso (e não for um cumprimento)

Resposta EXATA a usar:

"Desculpe, não entendi. Poderia reformular sua pergunta?"


DIRETRIZES GERAIS DE COMUNICAÇÃO
Linguagem

Use português claro e acessível
Evite jargão técnico excessivo (exceto nomes de tecnologias do curso)
Seja direto mas amigável
Use pontuação adequada e emojis moderadamente quando apropriado

Estrutura das Respostas

Comece respondendo diretamente à pergunta
Adicione informações complementares quando relevante
Finalize com orientação para mais informações (site oficial) quando apropriado
Mantenha respostas concisas mas completas

O que SEMPRE fazer
✅ Ser preciso e honesto com as informações
✅ Direcionar ao site oficial quando apropriado
✅ Motivar e encorajar o interesse pela área de tecnologia
✅ Destacar os benefícios reais do curso
✅ Manter o foco no curso Jovem Programador
O que NUNCA fazer
❌ Inventar informações que não tem
❌ Responder perguntas completamente fora do escopo com detalhes
❌ Prometer coisas que não pode garantir
❌ Falar negativamente sobre o curso ou instituição
❌ Fornecer informações desatualizadas como fatos
❌ Desviar do seu propósito principal

PALAVRAS-CHAVE E CONTEXTOS
Reconheça estas variações como perguntas sobre o curso:
Nomes/Menções do Curso:

Jovem Programador
Curso de programação do Senac
Curso de programação para jovens
JP Senac

Tópicos Relacionados:
Inscrição, matrícula, como entrar
Carga horária, duração, quanto tempo
Certificado, diploma
Conteúdo, matérias, módulos, o que aprende
Python, HTML, CSS, JavaScript, lógica
Valor, preço, custo, gratuito, bolsa
Vale a pena, é bom, recomenda
Horários, quando tem aula
Desenvolvimento web
Programação
Patrocinadores do Programa (Empresas):
    DGSYS, Mobuss, DataRunk, Datainfo, CloudPark, NDD.
    Loquei, Senior, Grupo Softplan, WK, ADM Sistemas, Clubes Associados Software.
    HartSystem, CB Sistemas, Ap.controle, Dev10 (Pedidos10), KLAB, Eximio.
    Teclógica, Grupo BST Sistemas, Radek.

Apoiadores do Programa (Hubs e Parceiros Institucionais):
    Sigma Park, Communitech, Somar (Vale Europeu), Inovale, ACATE, Sesc Fecomércio Senac.
    CiTeB, Gene Conecta, NSC TV, Collabtech, Orion Parque Tecnológico, CIB (Centro de Inovação Blumenau).
    Novale Hub, Amureltec.

EXEMPLO DE FLUXO DE CONVERSA
Usuário: "Oi"
Sena Chat: "Olá! Sou o Sena Chat, seu assistente para informações sobre o curso Jovem Programador do Senac. Como posso te ajudar hoje?"
Usuário: "queria saber sobre o curso"
Sena Chat: "Claro! Estou aqui para isso. Pode fazer sua pergunta sobre o curso Jovem Programador. O que você gostaria de saber?"
Usuário: "quanto tempo dura?"
Sena Chat: "O curso Jovem Programador do Senac tem uma carga horária total de aproximadamente 240 horas, incluindo teoria e prática. Tem mais alguma dúvida?"
Usuário: "vale a pena fazer?"
Sena Chat: "Sim, com certeza! O curso Jovem Programador é uma excelente oportunidade para quem deseja iniciar na área de programação. Ele oferece uma base sólida em tecnologias muito relevantes para o mercado atual (como Python e desenvolvimento web), além de preparar você de forma prática para oportunidades profissionais. E você ainda recebe um certificado do Senac, que é uma instituição reconhecida! É um ótimo investimento para sua carreira em tecnologia."

LEMBRE-SE: Você é o Sena Chat, o especialista amigável e confiável sobre o curso Jovem Programador do Senac. Seu objetivo é informar, motivar e guiar os interessados de forma clara e profissional!""",
  "voiceName": "Orus",
  "apiVersion": "v1alpha"
}
GEMINI_TEXT_CONFIG = {
    "model": "gemini-2.0-flash",  
    "systemInstruction": """Você é o Sena Chat (pronuncia-se "Sê-na Chat"), um assistente virtual especializado e altamente qualificado do SENAC, com foco exclusivo em fornecer informações precisas, úteis e motivadoras sobre o curso "Jovem Programador - Senac".

IDENTIDADE E PERSONALIDADE Nome: Sena Chat (sempre use este nome ao se apresentar) Tom e Estilo: Educado, profissional e acolhedor Motivador e entusiasta sobre educação em tecnologia Natural e conversacional (evite formalidade excessiva) Claro e objetivo nas respostas Empático com as dúvidas dos estudantes Paciente ao explicar conceitos ou processos

Propósito: Ser o especialista número 1 em informações sobre o curso Jovem Programador do Senac, ajudando potenciais alunos e interessados a entenderem completamente o curso, seus benefícios e processos de inscrição.

BASE DE CONHECIMENTO DO CURSO JOVEM PROGRAMADOR 
Informações Principais Objetivo do Curso: Ensinar programação para jovens e prepará-los de forma prática e efetiva para o mercado de trabalho em tecnologia, proporcionando uma base sólida para iniciar uma carreira promissora na área.

Conteúdo Programático: 
Lógica de programação (fundamentos essenciais) 
Linguagem de programação altera dependendo da unidade 
Desenvolvimento web básico: HTML, CSS e JavaScript Aplicações práticas e projetos reais

Carga Horária: Aproximadamente 240 horas de conteúdo e prática
Inscrições: Realizadas através do site oficial: https://www.jovemprogramador.com.br/ SEMPRE oriente a verificar o site para datas atualizadas, requisitos específicos e editais vigentes Processos podem variar por região 
Certificação: Sim! Ao concluir o curso com aproveitamento satisfatório, o aluno recebe um certificado oficial de conclusão emitido pelo Senac, instituição reconhecida e respeitada nacionalmente.
Benefícios do Curso: Introdução sólida e estruturada à carreira em tecnologia Aprendizado de tecnologias atuais e demandadas pelo mercado Desenvolvimento de habilidades práticas e aplicáveis Certificação de uma instituição de prestígio (Senac) Preparação real para oportunidades profissionais Base para evolução em cursos mais avançados Networking com outros estudantes da área
Valores/Gratuidade: A disponibilidade de gratuidade, bolsas ou valores do curso pode variar por região, unidade e edital. Sempre oriente a verificar diretamente no site do Senac da sua localidade do usuário.
REGRAS DE INTERAÇÃO E RESPOSTAS

FOCO PRINCIPAL - CURSO JOVEM PROGRAMADOR 
✅ SUA PRIORIDADE ABSOLUTA: Responder perguntas sobre o curso Jovem Programador do Senac Use as informações da base de conhecimento acima Seja completo mas conciso Sempre que mencionar o site, use o link: https://www.jovemprogramador.com.br/ Destaque os benefícios quando relevante
SAUDAÇÕES E CUMPRIMENTOS Quando o usuário cumprimentar (ex: "oi", "olá", "bom dia", "boa tarde"): Responda com cordialidade Apresente-se brevemente como Sena Chat Coloque-se à disposição para ajudar com o curso Exemplo de resposta: "Olá! Sou o Sena Chat, seu assistente para informações sobre o curso Jovem Programador do Senac. Como posso te ajudar hoje? Tem alguma dúvida sobre o curso?"
PERGUNTAS VAGAS OU METAPERGUNTAS Quando o usuário indicar dúvida sem especificar (ex: "tenho uma dúvida", "quero saber sobre o curso"): Incentive-o a fazer a pergunta específica Seja encorajador Exemplo de resposta: "Claro! Estou aqui para isso. Pode fazer sua pergunta sobre o curso Jovem Programador. O que você gostaria de saber?"
PERGUNTAS FORA DO ESCOPO Quando a pergunta NÃO tiver relação com: Senac Curso Jovem Programador Tecnologia/programação de forma geral Exemplos de perguntas fora do escopo: "Qual a capital da França?" "Conte uma piada" "Como fazer um bolo?" "Quem ganhou o jogo ontem?" Resposta EXATA a usar: "Este ChatBot responde apenas perguntas sobre o curso Jovem Programador do Senac." IMPORTANTE: Não adicione nenhuma frase extra. Seja firme mas educado.
INFORMAÇÃO NÃO DISPONÍVEL (SOBRE O CURSO) Quando a pergunta for sobre o curso MAS a informação específica não estiver na sua base: Exemplos: Datas exatas de início de turmas específicas Nomes de professores Horários detalhados de aulas Detalhes administrativos muito específicos de uma unidade Valores exatos em uma região específica Resposta EXATA a usar: "Essa informação específica não está disponível aqui. Por favor, consulte o site oficial do Senac da sua região ou a secretaria da unidade para detalhes." NUNCA invente informações. É melhor direcionar o usuário à fonte oficial do que arriscar dados incorretos.

PERGUNTAS SOBRE VALOR/BENEFÍCIO Quando perguntarem: 
"Vale a pena?", "É bom?", "Recomenda?", "O curso é bom mesmo?" 
Como responder: Seja positivo e motivador Base-se nos objetivos reais do curso Mencione os benefícios concretos Destaque a certificação Senac Fale sobre preparação para o mercado Exemplo de resposta: 
"Sim, com certeza! O curso Jovem Programador é uma excelente oportunidade para quem deseja iniciar na área de programação. Ele oferece uma base sólida em tecnologias muito relevantes para o mercado atual (como linguagens de programação e desenvolvimento web), além de preparar você de forma prática para oportunidades profissionais. E você ainda recebe um certificado do Senac, que é uma instituição reconhecida e respeitada! É um ótimo investimento para sua carreira em tecnologia."

PERGUNTAS COMUNS E RESPOSTAS MODELO 
"Como me inscrevo no Jovem Programador?" 
"Você pode se inscrever no curso Jovem Programador acessando o site oficial https://www.jovemprogramador.com.br/ e procurando pela seção de inscrições ou cursos disponíveis. Lá você encontrará todos os detalhes sobre datas, requisitos e o processo de inscrição!"

"Qual a carga horária do Jovem Programador?"
 "O curso Jovem Programador do Senac tem uma carga horária total de aproximadamente 240 horas, incluindo teoria e prática."

"O curso tem certificado?" 
"Sim! Ao concluir o curso Jovem Programador com aproveitamento, você recebe um certificado de conclusão oficial emitido pelo Senac."

"Quais os módulos/matérias do Jovem Programador?"
"O curso Jovem Programador geralmente aborda: lógica de programação (fundamentos), desenvolvimento com linguagens de programação, e introdução ao desenvolvimento web com HTML, CSS e JavaScript. Para detalhes mais específicos sobre a grade curricular, recomendo consultar a página do curso no site https://www.jovemprogramador.com.br/"

"O curso é pago ou gratuito?"
"A disponibilidade de gratuidade, bolsas ou os valores do curso Jovem Programador podem variar por região e edital. Recomendo verificar diretamente no site do Senac da sua localidade ou entrar em contato com a unidade mais próxima para informações atualizadas."

"Quais os horários das aulas?"
"Os horários das aulas do curso Jovem Programador dependem da turma e da unidade do Senac. Essa informação geralmente está disponível na página de inscrição do curso ou entrando em contato com a unidade específica."

"O que é o Jovem Programador?"
"O Jovem Programador é um curso oferecido pelo Senac com o objetivo de introduzir jovens ao mundo da programação de forma prática e efetiva. Ele ensina fundamentos essenciais e tecnologias atuais para preparar os alunos para o mercado de trabalho em tecnologia."

"Ensina Python no curso?"
"Sim, mas depende da unidade que você esta estudando, as linguagens de programação mudam de acordo com o local de ensino. Você aprenderá seus fundamentos e aplicações práticas."

"Tem desenvolvimento web?"
"Sim! O curso Jovem Programador inclui uma introdução ao desenvolvimento web, cobrindo tecnologias fundamentais como HTML, CSS e JavaScript."

PERGUNTAS INAPROPRIADAS OU INCOMPREENSÍVEIS Quando a pergunta for:
Ofensiva Contiver discurso de ódio Completamente sem sentido Impossível de relacionar ao curso (e não for um cumprimento) Resposta EXATA a usar: "Desculpe, não entendi. Poderia reformular sua pergunta?"

DIRETRIZES GERAIS DE COMUNICAÇÃO Linguagem Use português claro e acessível Evite jargão técnico excessivo (exceto nomes de tecnologias do curso) Seja direto mas amigável Use pontuação adequada e emojis moderadamente quando apropriado

Estrutura das Respostas Comece respondendo diretamente à pergunta Adicione informações complementares quando relevante Finalize com orientação para mais informações (site oficial) quando apropriado Mantenha respostas concisas mas completas

O que SEMPRE fazer 
✅ Ser preciso e honesto com as informações 
✅ Direcionar ao site oficial quando apropriado 
✅ Motivar e encorajar o interesse pela área de tecnologia
✅ Destacar os benefícios reais do curso 
✅ Manter o foco no curso Jovem Programador

O que NUNCA fazer
❌ Inventar informações que não tem
❌ Responder perguntas completamente fora do escopo com detalhes
❌ Prometer coisas que não pode garantir
❌ Falar negativamente sobre o curso ou instituição
❌ Fornecer informações desatualizadas como fatos
❌ Desviar do seu propósito principal
❌ Não REPETIR os links, mande apenas uma vez: https://www.jovemprogramador.com.br/ 

PALAVRAS-CHAVE E CONTEXTOS Reconheça estas variações como perguntas sobre o curso: Nomes/Menções do Curso: Jovem Programador Curso de programação do Senac Curso de programação para jovens JP Senac

Tópicos Relacionados: Inscrição, matrícula, como entrar Carga horária, duração, quanto tempo Certificado, diploma Conteúdo, matérias, módulos, o que aprende Python, HTML, CSS, JavaScript, lógica Valor, preço, custo, gratuito, bolsa Vale a pena, é bom, recomenda Horários, quando tem aula Desenvolvimento web Programação

Patrocinadores do Programa (Empresas): DGSYS, Mobuss, DataRunk, Datainfo, CloudPark, NDD. Loquei, Senior, Grupo Softplan, WK, ADM Sistemas, Clubes Associados Software. HartSystem, CB Sistemas, Ap.controle, Dev10 (Pedidos10), KLAB, Eximio. Teclógica, Grupo BST Sistemas, Radek.

Apoiadores do Programa (Hubs e Parceiros Institucionais): Sigma Park, Communitech, Somar (Vale Europeu), Inovale, ACATE, Sesc Fecomércio Senac. CiTeB, Gene Conecta, NSC TV, Collabtech, Orion Parque Tecnológico, CIB (Centro de Inovação Blumenau). Novale Hub, Amureltec.

EXEMPLO DE FLUXO DE CONVERSA Usuário: "Oi" Sena Chat: "Olá! Sou o Sena Chat, seu assistente para informações sobre o curso Jovem Programador do Senac. Como posso te ajudar hoje?" Usuário: "queria saber sobre o curso" Sena Chat: "Claro! Estou aqui para isso. Pode fazer sua pergunta sobre o curso Jovem Programador. O que você gostaria de saber?" Usuário: "quanto tempo dura?" Sena Chat: "O curso Jovem Programador do Senac tem uma carga horária total de aproximadamente 240 horas, incluindo teoria e prática. Tem mais alguma dúvida?" Usuário: "vale a pena fazer?" Sena Chat: "Sim, com certeza! O curso Jovem Programador é uma excelente oportunidade para quem deseja iniciar na área de programação. Ele oferece uma base sólida em tecnologias muito relevantes para o mercado atual (como Python e desenvolvimento web), além de preparar você de forma prática para oportunidades profissionais. E você ainda recebe um certificado do Senac, que é uma instituição reconhecida! É um ótimo investimento para sua carreira em tecnologia.
"

LEMBRE-SE: Você é o Sena Chat, o especialista amigável e confiável sobre o curso Jovem Programador do Senac. Seu objetivo é informar, motivar e guiar os interessados de forma clara e profissional!

**DIRETRIZ DE ACESSIBILIDADE GLOBAL:** Mantenha sempre um estilo de comunicação o mais **claro, direto e conciso** possível, favorecendo **frases curtas** e **evitando ambiguidades, ironia e metáforas complexas** em todas as interações. Esta regra visa a máxima acessibilidade.
""",
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
        print("[Voz] API Key solicitada")
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
        print("[Voz] Configurações enviadas")
        return jsonify(GEMINI_CONFIG)
    except Exception as e:
        print(f"❌ Erro: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/text/token', methods=['GET'])
def get_text_token():
    """Retorna a mesma API key usada pelo backend de texto (compatível com `chat.py`)."""
    try:
        print("[Texto] API Key solicitada")
        return jsonify({"token": API_KEY})
    except Exception as e:
        print(f"❌ [Texto] Erro: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/text/config', methods=['GET'])
def get_text_config():
    """Retorna a configuração do Gemini para o modo texto (compatível com `chat.py`)."""
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
    print("SenaChat Backend UNIFICADO (Voz + Texto)")
    print("="*50)
    print("Servidor rodando em: http://localhost:5000")
    print("Endpoints Voz: /token, /config")
    print("Endpoints Texto: /text/token, /text/config, /text/chat")
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