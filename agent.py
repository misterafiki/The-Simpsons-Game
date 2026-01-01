from flask import Flask, render_template, request, jsonify
import requests
import ollama
import random

app = Flask(__name__)

# Configuración
MODEL_NAME = "simpsons-host:latest" # El nombre que le diste en el Modelfile
SIMPSONS_API = "https://thesimpsonsapi.com/api/characters"

# Almacén temporal del juego (en memoria)
game_state = {
    "character": None,
    "history": []
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['GET'])
def start_game():
    try:
        # 1. Obtener personaje de la API
        resp = requests.get(SIMPSONS_API).json()
        
        character = random.choice(resp['results'])
        
        game_state["character"] = character
        game_state["history"] = [
            {"role": "user", "content": f"Aquí tienes el JSON del personaje: {character}"}
        ]

        # 2. Primera pista de la IA
        res = ollama.chat(model=MODEL_NAME, messages=game_state["history"])
        ia_message = res['message']['content']
        
        game_state["history"].append(res['message'])
        
        return jsonify({
            "pista": ia_message,
            "imagen": f"https://thesimpsonsapi.com{character['portrait_path']}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/guess', methods=['POST'])
def guess():
    user_guess = request.json.get('text')
    
    # Añadir el intento al historial
    game_state["history"].append({"role": "user", "content": user_guess})
    
    # Consultar a Ollama
    res = ollama.chat(model=MODEL_NAME, messages=game_state["history"])
    ia_response = res['message']['content']
    
    game_state["history"].append(res['message'])
    
    return jsonify({"respuesta": ia_response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)