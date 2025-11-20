import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

try:
    API_KEY = os.environ["GOOGLE_API_KEY"]
except KeyError:
    print("❌ ERRO: GOOGLE_API_KEY não encontrada no .env")
    print("📝 Crie um arquivo .env com: GOOGLE_API_KEY=sua_chave_aqui")
    exit(1)


GEMINI_CONFIG = {
    # Modelo de texto mais recente
    "model": "gemini-2.5-flash-preview-09-2025", 
    
    # Mantendo a mesma instrução de sistema
    "systemInstruction": """Você é o SenaChat, um assistente virtual amigável e prestativo do SENAC - JOVEM PROGRAMADOR. 
    
Seu papel é:
- Ajudar estudantes com dúvidas sobre cursos e tecnologia
- Responder de forma clara e objetiva
- Ser educado, profissional e motivador
- Quando não souber algo, ser honesto e sugerir onde encontrar a informação

Responda sempre de forma conversacional e natural.""",
    
}


app = Flask(__name__)
CORS(app, resources={
    r"/*": {"origins": "*"}  # Permite qualquer origem (dev)
})


@app.route('/token', methods=['GET'])
def get_token():
    """
    Retorna a API Key para o frontend.
    """
    try:
        print("✅ [Texto] API Key enviada para o frontend")
        return jsonify({"token": API_KEY})
    
    except Exception as e:
        print(f"❌ [Texto] Erro: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/config', methods=['GET'])
def get_config():
    """
    Retorna as configurações do Gemini (de texto) para o frontend.
    """
    try:
        print("📋 [Texto] Configurações enviadas para o frontend")
        return jsonify(GEMINI_CONFIG)
    
    except Exception as e:
        print(f"❌ [Texto] Erro: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])
def home():
    """Status do servidor."""
    return jsonify({
        "status": "online",
        "service": "SenaChat Backend (Texto)",
        "endpoints": {
            "/token": "Retorna API key",
            "/config": "Retorna configurações do Gemini para texto"
        }
    })


@app.route('/public/<path:filename>')
def serve_public(filename):
    """Serve arquivos estáticos da pasta `public/` (mesma rota que em `app.py`)."""
    return send_from_directory('public', filename)


if __name__ == '__main__':
    PORTA_TEXTO = 5001 
    
    print("\n" + "="*50)
    print("🚀 SenaChat Backend (Texto)")
    print("="*50)
    print(f"📡 Servidor: http://localhost:{PORTA_TEXTO}")
    print("🔑 Endpoints:")
    print(f"   - GET /token  → API Key")
    print(f"   - GET /config → Configurações do Gemini (Texto)")
    print("="*50)
    
    print("\n🔍 Rotas registradas no Flask (Texto):")
    for rule in app.url_map.iter_rules():
        print(f"   {rule.methods} {rule.rule}")
    print("="*50)
    
    print(f"💡 Deixe este terminal aberto! (Rodando na porta {PORTA_TEXTO})")
    print(f"💡 Lembre-se que o backend de VOZ (app.py) deve rodar em outro terminal na porta 5000.\n")
    
    app.run(
        host='0.0.0.0',
        port=PORTA_TEXTO, 
        debug=True
    )