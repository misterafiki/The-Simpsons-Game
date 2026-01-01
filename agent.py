import requests
import ollama
from flask import Flask, jsonify, request

app = Flask(__name__)

# URL de la API que proporcionaste
API_URL = "https://thesimpsonsapi.com/api/characters"

# Variable global temporal para guardar el personaje actual (en un juego real usarías sesiones)
contexto_juego = {
    "personaje_actual": None,
    "historial_chat": []
}

@app.route('/nuevo-juego', methods=['GET'])
def nuevo_juego():
    # 1. Obtener datos de la API
    response = requests.get(API_URL).json()
    # Elegimos el primero de la lista (puedes randomizar esto)
    personaje = response['results'][0] 
    
    contexto_juego["personaje_actual"] = personaje
    # Limpiamos el historial para un nuevo juego
    contexto_juego["historial_chat"] = [
        {"role": "user", "content": f"Aquí tienes el JSON del personaje: {personaje}"}
    ]

    # 2. Llamar a Ollama con tu modelo personalizado
    res = ollama.chat(model='simpsons-host:latest', messages=contexto_juego["historial_chat"])
    
    respuesta_ia = res['message']['content']
    contexto_juego["historial_chat"].append(res['message'])

    return jsonify({
        "presentacion": respuesta_ia,
        "imagen": f"https://thesimpsonsapi.com{personaje['portrait_path']}" # Construir URL imagen
    })

@app.route('/adivinar', methods=['POST'])
def adivinar():
    user_input = request.json.get('intento')
    
    # Añadimos el intento al historial
    contexto_juego["historial_chat"].append({"role": "user", "content": user_input})
    
    # Consultamos a la IA (ella sabe si acertó o no por las reglas del Modelfile)
    res = ollama.chat(model='simpsons-host', messages=contexto_juego["historial_chat"])
    
    respuesta_ia = res['message']['content']
    contexto_juego["historial_chat"].append(res['message'])

    return jsonify({"respuesta": respuesta_ia})

if __name__ == '__main__':
    app.run(port=5000)