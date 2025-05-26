#Obtengo el GINI de Arg para pasarselo a c y que se me devuelva el valor con un 1 sumado en assembler
import requests
import subprocess

def obtener_gini_argentina():
    url = "https://api.worldbank.org/v2/en/country/AR/indicator/SI.POV.GINI"
    params = {
        "format": "json",
        "date": "2020",
        "per_page": "1"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data and len(data) > 1 and data[1]:
        gini = data[1][0]["value"]
        print(f"GINI obtenido para Argentina: {gini}")
        if gini is not None:
            subprocess.run(["./gini", str(gini)])
        else:
            print("No hay datos disponibles para el año seleccionado.")
    else:
        print("No se pudo obtener información del Banco Mundial.")

if __name__ == "__main__":
    obtener_gini_argentina()