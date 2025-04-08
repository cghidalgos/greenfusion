from flask import Flask, render_template, request, redirect, url_for
import openai
import markdown
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
api_key = os.getenv("API_KEY")

def generar_prompt(material, cantidad, precio, origen):
    return (
        f"Tengo un material llamado '{material}' que compro en '{origen}', "
        f"uso una cantidad de {cantidad} unidades y cada una cuesta {precio} pesos colombianos. "
        f"¿Qué material alternativo podría usar para reducir mis costos? "
        f"¿Cuánto bajaría el precio? ¿Qué ventajas tendría ese nuevo material sobre el actual?, hazlo en máximo 400 tokens"
    )

@app.route("/", methods=["GET", "POST"])
def index():
    resultado_html = None
    error = None
    datos = {}

    if request.method == "POST":
        try:
            material = request.form["material"]
            cantidad = float(request.form["cantidad"])
            precio = float(request.form["precio"])
            origen = request.form["origen"]

            if not (material and origen):
                raise ValueError("Todos los campos son obligatorios.")

            prompt = generar_prompt(material, cantidad, precio, origen)

            respuesta = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400
            )

            resultado_md = respuesta['choices'][0]['message']['content'].strip()
            resultado_html = markdown.markdown(resultado_md)

            datos = {
                "material": material,
                "cantidad": cantidad,
                "precio": precio,
                "origen": origen,
                "resultado_html": resultado_html,
            }

        except Exception as e:
            error = f"Ocurrió un error: {str(e)}"

    return render_template("index.html", resultado_html=resultado_html, error=error, datos=datos)

@app.route("/nueva_recomendacion", methods=["POST"])
def nueva_recomendacion():
    return redirect(url_for("index"))

@app.route("/ir_a_jdoodle")
def ir_a_jdoodle():
    return redirect("https://www.jdoodle.com/")

if __name__ == "__main__":
    app.run(debug=True)
