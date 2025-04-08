from flask import Flask, render_template, request, send_file, redirect, url_for
import openai
import markdown
import os
from xhtml2pdf import pisa
from io import BytesIO

app = Flask(__name__)

openai.api_key = "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"


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

            # Guardamos datos para pasarlos al template
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

@app.route("/descargar_pdf", methods=["POST"])
def descargar_pdf():
    resultado_html = request.form["resultado_html"]
    html = render_template("pdf_template.html", contenido=resultado_html)

    pdf_stream = BytesIO()
    pisa.CreatePDF(src=html, dest=pdf_stream)
    pdf_stream.seek(0)
    return send_file(pdf_stream, as_attachment=True, download_name="recomendacion.pdf", mimetype="application/pdf")

@app.route("/nueva_recomendacion", methods=["POST"])
def nueva_recomendacion():
    # Aquí podrías reutilizar el mismo prompt o hacerlo más complejo
    return redirect(url_for("index"))

@app.route("/ir_a_jdoodle")
def ir_a_jdoodle():
    return redirect("https://www.jdoodle.com/")

if __name__ == "__main__":
    app.run(debug=True)
