import base64
import re
from flask import Flask, flash, redirect, request, session, url_for, g
from flask import render_template
from flaskext.mysql import MySQL
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os

# Cargar variables de entorno desde el archivo .env
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data.env')
load_dotenv(dotenv_path=env_path)

#definimos la ruta absoluta del proyecto
template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

#unimos las rutas de las carpetas src y templates a la ruta del proyecto de la línea anterior
template_dir = os.path.join(template_dir, 'src', 'templates')

#indicamos que se busque el archivo index.html (en carpeta templates) al lanzar la aplicación
app = Flask(__name__, static_folder='static', template_folder = template_dir)

app.secret_key = os.urandom(24)
            
mysql = MySQL(app)
app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_DATABASE_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_DATABASE_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE_DB')
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = '@d9876'
# app.config['MYSQL_DATABASE_DB'] = 'automotores_srl'

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads', 'catalogo', 'grandes')
app.config['DEFAULT_IMAGE'] = os.path.join(app.root_path, 'static', 'assets', 'catalogo', 'grandes', 'NoFoto.png')

mysql.init_app(app)

soy_admin = True

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

#Admin
@app.context_processor
def inject_user():
    return dict(is_admin=session.get('is_admin', False))

def get_db():
    if 'db' not in g:
        g.db = mysql.connect()
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

#Funciones extra
def initialize_mysql(app):
    pass
    #     mysql.init_app(app)
    # else:
    #     mysql.connect()

def is_valid_email(email):
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(regex, email)

def is_alphanumeric(s):
    return s.isalnum()

def is_alphanumeric_extended(valor):
    # Acepta letras, números, espacios, tildes, y los caracteres " . : , ;'
    return re.match(r'^[\w\sáéíóúÁÉÍÓÚñÑ\.\:\,\;\']+$', valor) is not None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def validar_campos(modelo, descripcion):
    if not (modelo and descripcion):
        flash('Error: Todos los campos son requeridos')
        return False
    if not is_alphanumeric_extended(modelo):
        flash('Error: El modelo solo debe contener caracteres alfabéticos y números')
        return False
    if not is_alphanumeric_extended(descripcion):
        flash('Error: La descripción solo debe contener caracteres alfabéticos y números')
        return False
    
    return True


def guardar_datos_formulario(modelo, descripcion, foto):
    session['modelo'] = modelo
    session['descripcion'] = descripcion
    session['foto'] = foto
    
def limpiar_datos_formulario():
    session['modelo'] = ""
    session['descripcion'] = ""
    session['foto'] = ""
    
#Fin funciones extra

#Routes
@app.route('/')
def index():
    session['is_admin'] = True  # Establecer el estado de administrador
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, modelo, descripcion, foto FROM catalogo")
    catalogo = cursor.fetchall()
    #Convertir los datos a diccionario
    insertarObjectos = [] 
    nombreDeColumnas = [columna[0] for columna in cursor.description]
    
    for unRegistro in catalogo:
        registro_dict = dict(zip(nombreDeColumnas, unRegistro))
        # Convertir el blob en base64
        if registro_dict['foto']:  # Asegúrate de que el campo 'foto' no sea None
            registro_dict['foto'] = base64.b64encode(registro_dict['foto']).decode('utf-8')
        insertarObjectos.append(registro_dict)
    
    # Cierra el cursor para liberar recursos de memoria.    
    cursor.close()

    return render_template('index.html', data=insertarObjectos)

@app.route('/productos')
def productos():
    
    #abro la conexion
    db = get_db()

    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM catalogo")
    miResultado = cursor.fetchall()
    
    #Convertir los datos a diccionario
    insertarObjectos = [] 
    nombreDeColumnas = [columna[0] for columna in cursor.description]
    
    for unRegistro in miResultado:
        registro_dict = dict(zip(nombreDeColumnas, unRegistro))
        # Convertir el blob en base64
        if registro_dict['foto']:  # Asegúrate de que el campo 'foto' no sea None
            registro_dict['foto'] = base64.b64encode(registro_dict['foto']).decode('utf-8')
        insertarObjectos.append(registro_dict)
    
    # Cierra el cursor para liberar recursos de memoria.    
    cursor.close()

    return render_template('productos.html', data=insertarObjectos)

@app.route('/consultas')
def consultas():
    return render_template('consultas.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/adminAutomotores')
def adminAutomotores():
    #abro la conexion
    db = get_db()

    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM catalogo")
    miResultado = cursor.fetchall()
    
    #Convertir los datos a diccionario
    insertarObjectos = [] 
    nombreDeColumnas = [columna[0] for columna in cursor.description]
    
    for unRegistro in miResultado:
        registro_dict = dict(zip(nombreDeColumnas, unRegistro))
        # Convertir el blob en base64
        if registro_dict['foto']:  # Asegúrate de que el campo 'foto' no sea None
            registro_dict['foto'] = base64.b64encode(registro_dict['foto']).decode('utf-8')
        insertarObjectos.append(registro_dict)
    
    # Cierra el cursor para liberar recursos de memoria.    
    cursor.close()
    
    return render_template('adminAutomotores.html', data=insertarObjectos)

#Ruta para guardar en la bdd
@app.route('/save-automotor', methods=['POST'])
def addAuto():
    modelo = request.form['modelo']
    descripcion = request.form['descripcion']
    foto = request.files['foto']

    #Validaciones
    if not validar_campos(modelo, descripcion):
        guardar_datos_formulario(modelo, descripcion, foto)
        return redirect(url_for('adminAutomotores'))
    #Fin validaciones

     # Verifica si se ha subido un archivo de foto
    if 'foto' in request.files:
        file = request.files['foto']
        if file.filename != '':
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                # Crear carpeta de subida si no existe
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                file.save(filepath)
                # Leer la imagen como binario
                with open(filepath, 'rb') as file:
                    fotoblob = file.read()
            else:
                flash('Error: El tipo de archivo subido no es válido')
                return redirect(url_for('adminAutomotores'))
        else:
            # Leer la imagen predeterminada como binario
            default_image_path = app.config['DEFAULT_IMAGE']
            with open(default_image_path, 'rb') as file:
                fotoblob = file.read()
    else:
        # Leer la imagen predeterminada como binario
        default_image_path = app.config['DEFAULT_IMAGE']
        with open(default_image_path, 'rb') as file:
            fotoblob = file.read()
     
     #abro la conexion
    db = get_db()
    cursor = db.cursor()
    sql = "INSERT INTO catalogo (modelo, descripcion, foto) VALUES (%s, %s, %s)"
    data = (modelo, descripcion, fotoblob)
    cursor.execute(sql, data)
    db.commit()
    flash('Automotor añadido correctamente')
    limpiar_datos_formulario()
    return redirect(url_for('adminAutomotores'))

#Ruta para eliminar en la bdd
@app.route('/eliminar/<string:id>')
def eliminar(id):
     #abro la conexion
    db = get_db()
    cursor = db.cursor()
    sql = "DELETE FROM catalogo WHERE id = %s"
    data = (id,)
    cursor.execute(sql, data)
    db.commit()
    flash('Automotor eliminado correctamente')
    return redirect(url_for('adminAutomotores'))

#Ruta para editar en la bdd
@app.route('/editar/<string:id>', methods=['POST'])
def edit(id):
    modelo = request.form['modelo']
    descripcion = request.form['descripcion']

    #Validaciones
    if not validar_campos(modelo, descripcion):
        guardar_datos_formulario(modelo, descripcion, foto)
        return redirect(url_for('adminAutomotores'))

     # Verifica si se ha subido un archivo de foto
    if 'foto' in request.files:
        file = request.files['foto']
        if file.filename != '':
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                # Crear carpeta de subida si no existe
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                file.save(filepath)
                # Leer la imagen como binario
                with open(filepath, 'rb') as file:
                    fotoblob = file.read()
            else:
                flash('Error: El tipo de archivo subido no es válido')
                return redirect(url_for('adminAutomotores'))
        else:
            # Leer la imagen predeterminada como binario
            default_image_path = app.config['DEFAULT_IMAGE']
            with open(default_image_path, 'rb') as file:
                fotoblob = file.read()
    else:
        # Leer la imagen predeterminada como binario
        default_image_path = app.config['DEFAULT_IMAGE']
        with open(default_image_path, 'rb') as file:
            fotoblob = file.read()
    
     #abro la conexion
    db = get_db()
    cursor = db.cursor()

    if fotoblob:
        sql = "UPDATE catalogo SET modelo = %s, descripcion = %s, foto = %s WHERE id = %s"
        data = (modelo, descripcion, fotoblob, id)
    else:
        sql = "UPDATE catalogo SET modelo = %s, descripcion = %s WHERE id = %s"
        data = (modelo, descripcion, id)
    
    cursor.execute(sql, data)
    db.commit()
    flash('Automotor editado correctamente')
    limpiar_datos_formulario()
    return redirect(url_for('adminAutomotores'))

#ejecucion directa de este archivo en modo de desarrollador en el puerto 4000 del localhost o servidor local creado por flask.
if __name__ == '__main__':
    ##app.run(debug=True, port=4000)
    app.run(debug=True)

