from flask import Flask, render_template, request, url_for, redirect, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'claveeeee'  # Reemplaza con una clave secreta segura
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'home'




@app.route('/<path:filename>', methods=['GET']	)
def static_files(filename):
    return send_from_directory('static', filename)

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario = db.Column(db.String(200), unique=True)
    contraseña = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)  # Agregar este atributo

    def is_authenticated(self):
        return True  # Cambiar según la lógica de autenticación

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200))
    precio = db.Column(db.Integer)
    descripcion = db.Column(db.String(200))
class Mascota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), unique=True)
    edad = db.Column(db.Integer)
    raza = db.Column(db.String(200))
    descripcion = db.Column(db.String(200))
class Carro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(200), unique=True)
    modelo = db.Column(db.Integer)
    año = db.Column(db.Integer)
# Configurar Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/auth', methods=['POST'])
def autenticar():
    try:
        usuarioForm = request.form['usuario']
        contraseñaForm = request.form['contraseña']
        usuarioBd = Usuario.query.filter_by(usuario=usuarioForm, contraseña=contraseñaForm).first()
        if usuarioBd is not None:
            login_user(usuarioBd)  # Iniciar sesión del usuario
            return redirect(url_for('principal'))
        else:
            raise Exception("Usuario o contraseña incorrectos")
    except Exception as e:
        return render_template('index.html', error=e)

@app.route('/principal')
@login_required
def principal():
    return render_template('principal.html')

@app.route('/usuarios', methods=['GET', 'POST'])
@login_required
def usuarios():
    if request.method == 'POST':
        if 'usuario_id' in request.form:
            # Editar usuario existente
            usuario_id = request.form['usuario_id']
            usuario = Usuario.query.get(usuario_id)
            usuario.usuario = request.form['usuario']
            usuario.contraseña = request.form['contraseña']
            db.session.commit()
            return jsonify({"message": "Usuario actualizado correctamente"})
        else:
            # Crear nuevo usuario
            try:
                nuevo_usuario = Usuario(usuario=request.form['usuario'], contraseña=request.form['contraseña'])
                db.session.add(nuevo_usuario)
                db.session.commit()
            except Exception as e:
                return jsonify({"message": "Error al agregar usuario", "error": str(e)})
            return jsonify({"message": "Usuario agregado correctamente"})

    usuarios = Usuario.query.all()
    usuario_editar = None
    if 'editar_id' in request.args:
        # Mostrar formulario de edición si se proporciona un ID
        usuario_editar = Usuario.query.get(request.args['editar_id'])

    return render_template('usuarios.html', usuarios=usuarios, usuario_editar=usuario_editar)
@app.route('/usuarios/<int:usuario_id>', methods=['PUT'])
@login_required
def editar_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404

    usuario.usuario = request.form['usuario']
    usuario.contraseña = request.form['contraseña']
    db.session.commit()
    
    return jsonify({"message": "Usuario actualizado correctamente"})
@app.route('/usuarios/<int:usuario_id>', methods=['DELETE'])
@login_required
def borrar_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({"message": "Usuario eliminado correctamente"})
##### mascotas
@app.route('/mascotas', methods=['GET'])
@login_required
def mascotas():
    mascotas = Mascota.query.all()
    return render_template('mascotas.html', mascotas=mascotas)

@app.route('/mascotas', methods=['POST'])
@login_required
def mascotas_post():
    nueva_mascota = Mascota(
        nombre=request.form['nombre'],
        edad=request.form['edad'],
        raza=request.form['raza'],
        descripcion=request.form['descripcion']
    )
    db.session.add(nueva_mascota)
    db.session.commit()
    return jsonify({"message": "Mascota agregada correctamente"})

@app.route('/mascotas/<int:mascota_id>', methods=['PUT'])
@login_required
def mascotas_put(mascota_id):
    mascota = Mascota.query.get(mascota_id)
    mascota.nombre = request.form['nombre']
    mascota.edad = request.form['edad']
    mascota.raza = request.form['raza']
    mascota.descripcion = request.form['descripcion']
    db.session.commit()
    return jsonify({"message": "Mascota actualizada correctamente"})

@app.route('/mascotas/<int:mascota_id>', methods=['DELETE'])
@login_required
def mascotas_delete(mascota_id):
    mascota = Mascota.query.get(mascota_id)
    db.session.delete(mascota)
    db.session.commit()
    return jsonify({"message": "Mascota eliminada correctamente"})

##### Carros


@app.route('/carros', methods=['GET'])
def carros():
    carros = Carro.query.all()
    return render_template('carros.html', carros=carros)

@app.route('/carros', methods=['POST'])
def carros_post():
    nuevo_carro = Carro(
        marca=request.form['marca'],
        modelo=request.form['modelo'],
        año=request.form['año']
    )
    try:
        db.session.add(nuevo_carro)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": "Error al agregar carro", "error": str(e)})
    return jsonify({"message": "Carro agregado correctamente"})


@app.route('/carros/<int:carro_id>', methods=['PUT'])
def carros_put(carro_id):
    carro = Carro.query.get(carro_id)
    carro.marca = request.form['marca']
    carro.modelo = request.form['modelo']
    carro.año = request.form['año']
    db.session.commit()
    return jsonify({"message": "Carro actualizado correctamente"})

@app.route('/carros/<int:carro_id>', methods=['DELETE'])
def carros_delete(carro_id):
    carro = Carro.query.get(carro_id)
    db.session.delete(carro)
    db.session.commit()
    return jsonify({"message": "Carro eliminado correctamente"})






@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()  # Cierra la sesión del usuario
    return redirect(url_for('home'))




if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)


