from flask import Flask, render_template, request, redirect, url_for, flash
import os
from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://heimdall:Nn77Tw0WPM8Az1W1@cluster0.3vudx.mongodb.net/candidatos"
)
db = client["candidatos"]

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'supersecretkey'  # Necesario para usar mensajes flash

# Asegúrate de que la carpeta de subidas exista
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        # Recuperar datos del formulario
        cedula = request.form['cedula']
        rif = request.form['rif']
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        telefono = request.form['telefono']
        correo = request.form['correo']
        curriculum = request.files['curriculum']

        # Guardar el archivo
        filename = None
        if curriculum:
            filename = curriculum.filename
            curriculum.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Guardar los datos en la base de datos
        db.candidatos.insert_one({
            "cedula": cedula,
            "rif": rif,
            "nombres": nombres,
            "apellidos": apellidos,
            "telefono": telefono,
            "correo": correo,
            "curriculum_filename": filename
        })

        # Mensaje de confirmación
        flash('¡Gracias! Hemos recibido tu currículum correctamente.', 'success')

        return redirect(url_for('formulario'))
    return render_template('formulario.html')

if __name__ == '__main__':
    app.run(debug=True)