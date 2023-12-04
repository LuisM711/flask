from flask import Flask, render_template, request, url_for, redirect, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import requests
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'claveSuperSecretaImposibleDeAdivinar    '
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
    is_active = db.Column(db.Boolean, default=True) 

    def is_authenticated(self):
        return True 

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200))
    precio = db.Column(db.Integer)
    descripcion = db.Column(db.String(200))
class Divisa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), unique=True)
    pais = db.Column(db.String(200))
class Cripto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), unique=True)
    descripcion = db.Column(db.String(200))
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
            login_user(usuarioBd) 
            return redirect(url_for('principal'))
        else:
            raise Exception("Usuario o contraseña incorrectos")
    except Exception as e:
        return render_template('index.html', error=e)

@app.route('/principal')
@login_required
def principal():
    return render_template('principal.html')
# @app.route("/prueba", methods=['GET'])
# def prueba():
#     try:
#         nuevo_usuario = Usuario(usuario='luis', contraseña='1234')
#         db.session.add(nuevo_usuario)
#         db.session.commit()
#     except Exception as e:
#         return jsonify({"message": "Error al agregar usuario", "error": str(e)})
#     return jsonify({"message": "Usuario agregado correctamente"})
@app.route('/usuarios', methods=['GET', 'POST'])
@login_required
def usuarios():
    if request.method == 'POST':
        if 'usuario_id' in request.form:
            usuario_id = request.form['usuario_id']
            usuario = Usuario.query.get(usuario_id)
            usuario.usuario = request.form['usuario']
            usuario.contraseña = request.form['contraseña']
            db.session.commit()
            return jsonify({"message": "Usuario actualizado correctamente"})
        else:
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
##### divisas
@app.route('/divisas', methods=['GET'])
@login_required
def divisas():
    divisas = Divisa.query.all()
    return render_template('divisas.html', divisas=divisas)

@app.route('/divisas', methods=['POST'])
@login_required
def divisas_post():
    nueva_divisa = Divisa(
        nombre=request.form['nombre'],
        pais=request.form['pais'],
    )
    db.session.add(nueva_divisa)
    db.session.commit()
    return jsonify({"message": "Divisa agregada correctamente"})

@app.route('/divisas/<int:divisa_id>', methods=['PUT'])
@login_required
def divisas_put(divisa_id):
    divisa = Divisa.query.get(divisa_id)
    divisa.nombre = request.form['nombre']
    divisa.pais = request.form['pais']
    db.session.commit()
    return jsonify({"message": "Divisa actualizada correctamente"})

@app.route('/divisas/<int:divisa_id>', methods=['DELETE'])
@login_required
def divisas_delete(divisa_id):
    divisa = Divisa.query.get(divisa_id)
    db.session.delete(divisa)
    db.session.commit()
    return jsonify({"message": "divisa eliminada correctamente"})

##### criptos


@app.route('/criptos', methods=['GET'])
@login_required
def criptos():
    criptos = Cripto.query.all()
    print("inicio de criptos")
    print (criptos)
    print("fin de criptos")

    return render_template('criptos.html', criptos=criptos)
@app.route('/criptos', methods=['POST'])
@login_required
def criptos_post():
    nuevo_cripto = Cripto(
        nombre=request.form['nombre'],
        descripcion = request.form['descripcion']
    )
    try:
        db.session.add(nuevo_cripto)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": "Error al agregar cripto", "error": str(e)})
    return jsonify({"message": "cripto agregado correctamente"})


@app.route('/criptos/<int:cripto_id>', methods=['PUT'])
@login_required
def criptos_put(cripto_id):
    cripto = Cripto.query.get(cripto_id)
    cripto.nombre = request.form['nombre']
    cripto.descripcion = request.form['descripcion']
    db.session.commit()
    return jsonify({"message": "cripto actualizado correctamente"})

@app.route('/criptos/<int:cripto_id>', methods=['DELETE'])
@login_required
def criptos_delete(cripto_id):
    cripto = Cripto.query.get(cripto_id)
    db.session.delete(cripto)
    db.session.commit()
    return jsonify({"message": "cripto eliminado correctamente"})

@app.route('/nyse', methods=['GET'])
@login_required
def nyse():
    api_key = 'WMXT15076A2TQCU8'
    api_key = 'demo'
    api_url = f'https://www.alphavantage.co/query?function=MARKET_STATUS&apikey={api_key}'
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        return render_template('nyse.html', markets=data)
    else:
        return jsonify({"message": "Error al obtener datos de la Bolsa de Nueva York"})
@app.route('/nasa', methods=['GET'])
@login_required
def nasa():
    api_key = '0kV2072caK8oTfVFNXfNKUfcJhShz7TkwbmPx4ck'
    api_url = f'https://api.nasa.gov/planetary/apod?api_key={api_key}'
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        return render_template('nasa.html', data=data)
    else:
        return jsonify({"message": "Error al obtener datos de la NASA"})



@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user() 
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
