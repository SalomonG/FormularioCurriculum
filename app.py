from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import bcrypt

# Configuración
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'tu-clave-secreta-super-segura-aqui'  # Cambiar en producción!

# MongoDB
client = MongoClient("mongodb+srv://heimdall:Nn77Tw0WPM8Az1W1@cluster0.3vudx.mongodb.net/candidatos")
db = client["candidatos"]

# Autenticación
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.role = user_data['role']

@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({'_id': ObjectId(user_id)})
    return User(user_data) if user_data else None

def create_admin():
    if not db.users.find_one({'username': 'admin'}):
        hashed_pw = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        db.users.insert_one({
            'username': 'admin',
            'password': hashed_pw,
            'role': 'admin'
        })

# Rutas públicas
@app.route('/', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        datos = {
            "cedula": request.form['cedula'],
            "rif": request.form['rif'],
            "nombres": request.form['nombres'],
            "apellidos": request.form['apellidos'],
            "telefono": request.form['telefono'],
            "correo": request.form['correo'],
            "curriculum_filename": None
        }

        if 'curriculum' in request.files:
            file = request.files['curriculum']
            if file.filename != '':
                filename = f"{datos['cedula']}_{file.filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                datos["curriculum_filename"] = filename

        db.candidatos.insert_one(datos)
        flash('¡Registro exitoso!', 'success')
        return redirect(url_for('formulario'))
    
    return render_template('formulario.html')

# Rutas de autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        user_data = db.users.find_one({'username': request.form['username']})
        
        if user_data and bcrypt.checkpw(request.form['password'].encode('utf-8'), user_data['password']):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Rutas protegidas
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        abort(403)
    
    candidatos = list(db.candidatos.find())
    stats = {
        "total": db.candidatos.count_documents({}),
        "cvs": db.candidatos.count_documents({"curriculum_filename": {"$ne": None}}),
        "ultimo": db.candidatos.find_one(sort=[("_id", -1)])
    }
    return render_template('dashboard.html', candidatos=candidatos, **stats)

@app.route('/eliminar/<id>')
@login_required
def eliminar_candidato(id):
    if current_user.role != 'admin':
        abort(403)
    
    db.candidatos.delete_one({"_id": ObjectId(id)})
    flash('Candidato eliminado', 'info')
    return redirect(url_for('dashboard'))

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        create_admin()  # Solo en primera ejecución
    app.run(debug=True)