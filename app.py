import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# ========================================
# Configuração
# ========================================

load_dotenv()

try:
    API_KEY = os.environ["GOOGLE_API_KEY"]
except KeyError:
    print("❌ ERRO: GOOGLE_API_KEY não encontrada no .env")
    print("📝 Crie um arquivo .env com: GOOGLE_API_KEY=sua_chave_aqui")
    exit(1)

# ========================================
# Configurações do Gemini (Centralizadas aqui!)
# ========================================

GEMINI_CONFIG = {
    "model": "gemini-2.5-flash-native-audio-preview-09-2025",
    "systemInstruction": """Você é o SenaChat, um assistente virtual amigável e prestativo do SENAC - JOVEM PROGRAMADOR. 
    
Seu papel é:
- Ajudar estudantes com dúvidas sobre cursos e tecnologia
- Responder de forma clara e objetiva
- Ser educado, profissional e motivador
- Quando não souber algo, ser honesto e sugerir onde encontrar a informação

Responda sempre de forma conversacional e natural.""",
    
    "voiceName": "Orus",  # Voz masculina em português
    "apiVersion": "v1alpha"
}

# ========================================
# Flask App
# ========================================

app = Flask(__name__)
CORS(app, resources={
    r"/*": {"origins": "*"}  # Permite qualquer origem (dev)
})

# ========================================
# Rotas
# ========================================

@app.route('/token', methods=['GET'])
def get_token():
    """
    Retorna a API Key para o frontend.
    
    NOTA: Em produção, usar autenticação mais segura.
    Para projeto integrador está OK.
    """
    try:
        print("✅ API Key enviada para o frontend")
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
        print("📋 Configurações enviadas para o frontend")
        return jsonify(GEMINI_CONFIG)
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        return jsonify({"error": str(e)}), 500


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

# ========================================
# Inicialização
# ========================================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 SenaChat Backend")
    print("="*50)
    print("📡 Servidor: http://localhost:5000")
    print("🔑 Endpoints:")
    print("   - GET /token  → API Key")
    print("   - GET /config → Configurações do Gemini")
    print("="*50)
    
    # DEBUG: Lista todas as rotas registradas
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