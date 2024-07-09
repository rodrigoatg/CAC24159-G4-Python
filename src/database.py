import mysql.connector

database = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='@d9876',
    database='automotores_srl'
)

if database.is_connected():
    print("Conexión exitosa")
else:
    print("Conexión fallida")