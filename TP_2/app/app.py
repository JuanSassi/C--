from flask import Flask, render_template, request, jsonify
import subprocess
import requests

app = Flask(__name__)

def obtener_gini(pais):
    url = f"https://api.worldbank.org/v2/en/country/{pais}/indicator/SI.POV.GINI"
    params = {
        "format": "json",
        "date": "2020",
        "per_page": "1"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data and len(data) > 1 and data[1]:
        gini = data[1][0]["value"]
        if gini is not None:
            try:
                resultado = subprocess.check_output(["./gini_exec/gini", str(gini)])
                return resultado.decode("utf-8")
            except Exception as e:
                return f"Error al ejecutar el programa C: {e}"
        else:
            return "No hay datos GINI disponibles para ese año."
    else:
        return "No se pudo obtener información del Banco Mundial."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/obtener_gini', methods=['POST'])
def obtener_gini_route():
    pais = request.json.get("pais")
    resultado = obtener_gini(pais)
    return jsonify({"resultado": resultado})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

