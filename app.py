from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort, flash
from pymongo import MongoClient
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)



client = MongoClient("mongodb://localhost:27017/")
db = client["Polizas_ises"]
coleccion = db["Polizas"]

# Carpeta raíz donde guardaremos subcarpetas por póliza
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'Images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html", resultado=None, buscado=False)


@app.route("/buscar", methods=["POST"])
def buscar():
    try:
        poliza_num = int(request.form.get("poliza"))
        resultado = coleccion.find_one({"POLIZA": poliza_num})
        if not resultado:
            flash(f"No existe la póliza {poliza_num}", "error")
    except ValueError:
        flash("El número de póliza debe ser un entero.", "error")
        resultado = None
    return render_template("index.html", resultado=resultado, buscado=True)

@app.route("/cargar", methods=["POST"])
def cargar():
    # 1) Validar el número de póliza
    try:
        poliza_num = int(request.form.get("poliza"))
    except (TypeError, ValueError):
        flash("La póliza debe ser un número entero.", "error")
        return redirect(url_for('index'))

    # 2) Obtener múltiples archivos
    fotos = request.files.getlist("fotos")
    if not fotos or fotos == [None]:
        flash("Por favor selecciona al menos una imagen.", "error")
        return redirect(url_for('index'))

    # 3) Crear carpeta si no existe
    carpeta_poliza = os.path.join(app.config['UPLOAD_FOLDER'], str(poliza_num))
    os.makedirs(carpeta_poliza, exist_ok=True)

    # 4) Guardar imágenes y construir URLs
    urls_fotos = []
    for foto in fotos:
        if foto and foto.filename:
            filename = secure_filename(foto.filename)
            ruta_destino = os.path.join(carpeta_poliza, filename)
            try:
                foto.save(ruta_destino)
                url_foto = f"/imagen/{poliza_num}/{filename}"
                urls_fotos.append(url_foto)
            except Exception as e:
                flash(f"No se pudo guardar {filename}: {e}", "error")

    # 5) Actualizar MongoDB si hay imágenes válidas
    if urls_fotos:
        resultado = coleccion.update_one(
            {"POLIZA": poliza_num},
            {"$push": {"IMAGENES": {"$each": urls_fotos}}}
        )

        if resultado.matched_count:
            flash("Imágenes registradas correctamente en la póliza.", "success")
        else:
            flash("No se encontró la póliza en la base de datos. Las imágenes se guardaron en disco, pero no se registraron.", "error")
    else:
        flash("No se pudo guardar ninguna imagen válida.", "error")

    return redirect(url_for('index'))


@app.route("/imagen/<int:poliza>/<nombre_imagen>")
def servir_imagen(poliza, nombre_imagen):
    carpeta = os.path.join(app.config['UPLOAD_FOLDER'], str(poliza))
    try:
        return send_from_directory(carpeta, nombre_imagen)
    except FileNotFoundError:
        abort(404)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002,debug=True)
