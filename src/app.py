#importamos el modulo de flask para que funcione el proyecto
import re
from flask import Flask, flash, redirect, request, session, url_for
from flask import render_template
from flaskext.mysql import MySQL
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

#importamos el modulo os para acceder mas facil a los directorios
import os

# importamos para la base de datos
import database as db

#definimos la ruta absoluta del proyecto
template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

#unimos las rutas de las carpetas src y templates a la ruta del proyecto de la línea anterior
template_dir = os.path.join(template_dir, 'src', 'templates')

#indicamos que se busque el archivo index.html (en carpeta templates) al lanzar la aplicación
app = Flask(__name__, template_folder = template_dir)
app.secret_key = os.urandom(24)
##app = Flask(__name__)
            
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_DATABASE_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_DATABASE_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE_DB')
mysql.init_app(app)

#Rutas de la aplicación
# @app.route('/') es un decorador que vincula una función con una URL específica del sitio web. En este caso, '/' representa la ruta raíz o homepage del sitio web.

# La función home() que sigue al decorador es la que se ejecutará cuando un usuario visite la página principal (homepage) del sitio. La declaración return render_template('index.html') dentro de esta función indica que Flask debe buscar y renderizar el archivo HTML llamado index.html, que generalmente contiene el contenido que se mostrará en la página principal del sitio web.

# IMPORTANTE: importar en la linea 2 del codigo el modulo render_template para lanzar la pagina index.html. Debe quedar asi:
# from flask import Flask, render_template


# cursor es un objeto que apunta a la base de datos y nos permitira interactuar con el. database es el nombre de la variable que se encuentra en el archivo database.py y que contiene toda la informacion de conexion a la base de datos.

#  cursor.execute("SELECT * FROM users") ejecuta la consulta sql a la base de datos

# el metodo fetchall toma todos los registros devueltos en la ejecucion de la consulta anterior y guarda el resultado en la variable miResultado.

# insertarObjectos = [] crea una lista vacia

# nombreDeColumnas = [columna[0] for columna in cursor.description]
# Los nombres de las columnas se obtienen de cursor.description y los guarda en la variable nombreDeColumnas.

# for unRegistro in miResultado:
#     insertarObjectos.append(dict(zip(nombreDeColumnas, unRegistro)))
# Recorre cada registro del resultado de ejecutar la consulta y lo convierten en un diccionario. Esto se hace mediante el uso de zip() para emparejar los nombres de las columnas con los valores de cada registro. 

#Funciones extra
def is_valid_email(email):
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(regex, email)

def is_alphanumeric(s):
    return s.isalnum()

def is_alphanumeric_extended(valor):
    # Acepta letras, números, espacios, tildes, y los caracteres " . : , ;'
    return re.match(r'^[\w\sáéíóúÁÉÍÓÚñÑ\.\:\,\;\']+$', valor) is not None


def validar_campos(nombre, apellido, email, documento, telefono):
    if not (nombre and apellido and email and documento and telefono):
        flash('Error: Todos los campos son requeridos')
        return False
    if not is_alphanumeric_extended(nombre):
        flash('Error: El nombre solo debe contener caracteres alfabéticos y números')
        return False
    if not is_alphanumeric_extended(apellido):
        flash('Error: El apellido solo debe contener caracteres alfabéticos y números')
        return False
    if not is_valid_email(email):
        flash('Error: El correo electrónico no es válido')
        return False
    if not (documento.isdigit() and telefono.isdigit()):
        flash('Error: El documento debe contener solo números')
        return False
    if not (documento.isdigit() and telefono.isdigit()):
        flash('Error: El teléfono debe contener solo números')
        return False
    return True

def guardar_datos_formulario(nombre, apellido, email, documento, telefono):
    session['nombre'] = nombre
    session['apellido'] = apellido
    session['email'] = email
    session['documento'] = documento
    session['telefono'] = telefono
def limpiar_datos_formulario():
    session['nombre'] = ""
    session['apellido'] = ""
    session['email'] = ""
    session['documento'] = ""
    session['telefono'] = ""
#Fin funciones extra

@app.route('/')
def home():
    cursor = db.database.cursor()
    
    cursor.execute("SELECT * FROM clientes")
    miResultado = cursor.fetchall()
    
    print(miResultado)
    #Convertir los datos a diccionario
    insertarObjectos = [] 
    nombreDeColumnas = [columna[0] for columna in cursor.description]
    
    for unRegistro in miResultado:
        insertarObjectos.append(dict(zip(nombreDeColumnas, unRegistro)))
    
    # Cierra el cursor para liberar recursos de memoria.    
    cursor.close()
    
    return render_template('index.html', data=insertarObjectos)

#Ruta para guardar clientes en la bdd
@app.route('/cliente', methods=['POST'])
def addUser():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    email = request.form['email']
    documento = request.form['documento']
    telefono = request.form['telefono']

    #Validaciones
    if not validar_campos(nombre,apellido,email,documento,telefono):
        guardar_datos_formulario(nombre, apellido, email, documento, telefono)
        return redirect(url_for('home'))
    #Fin validaciones

    cursor = db.database.cursor()
    sql = "INSERT INTO clientes (nombre, apellido, email, documento, telefono) VALUES (%s, %s, %s, %s, %s)"
    data = (nombre, apellido, email, documento, telefono)
    cursor.execute(sql, data)
    db.database.commit()
    flash('Cliente añadido correctamente')
    limpiar_datos_formulario()
    return redirect(url_for('home'))

@app.route('/eliminar/<string:id>')
def eliminar(id):
    cursor = db.database.cursor()
    sql = "DELETE FROM clientes WHERE id = %s"
    data = (id,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('home'))

@app.route('/editar/<string:id>', methods=['POST'])
def edit(id):
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    email = request.form['email']
    documento = request.form['documento']
    telefono = request.form['telefono']
    
    #Validaciones
    if not validar_campos(nombre,apellido,email,documento,telefono):
        return redirect(url_for('home'))
    #Fin validaciones
    
    cursor = db.database.cursor()
    sql = "UPDATE clientes SET nombre = %s, apellido = %s, email = %s, documento = %s, telefono = %s WHERE id = %s"
    data = (nombre, apellido, email, documento, telefono, id)
    cursor.execute(sql, data)
    db.database.commit()
    flash('Cliente editado correctamente')
    limpiar_datos_formulario()
    return redirect(url_for('home'))

#ejecucion directa de este archivo en modo de desarrollador en el puerto 4000 del localhost o servidor local creado por flask.
if __name__ == '__main__':
    ##app.run(debug=True, port=4000)
    app.run(debug=True)

