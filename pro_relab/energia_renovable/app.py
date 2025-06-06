import psycopg2 # type: ignore
import hashlib
from flask import Flask, render_template, request, redirect, session, url_for, jsonify # type: ignore
from datetime import datetime, timedelta
import threading
import time
import requests # type: ignore elementos para datos davis
import pandas as pd # type: ignore Extrer los datos del archivo plano
#import tensorflow as tf
###############################################################################
#LIBRERIAS PARA EL MODELO DE PREDICCION
import pandas as pd # type: ignore
import numpy as np # type: ignore
from sklearn.preprocessing import MinMaxScaler # type: ignore
import tensorflow as tf # type: ignore

#########################################################################################################################
###### IR A hidrica.py ##### 
from hidrica import hidrica_bp, procesar_datos_hidrica  # Importa el Blueprint
#########################################################################################################################


# Crear una instancia de la aplicación Flask
app = Flask(__name__)
# Configurar la clave secreta de la aplicación, utilizada para gestionar sesiones y cookies seguras
app.config['SECRET_KEY'] = 'unicesmag'
# Establecer la duración de la sesión a 120 minutos
#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=120)
app.register_blueprint(hidrica_bp, url_prefix='/hidrica')
# Asegurar que las cookies solo se envíen por HTTPS y no accesibles por JavaScript
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365*10)
# Configurar los parámetros de la base de datos
app.config['DB_HOST'] = 'localhost'  # El host donde se encuentra la base de datos
app.config['DB_NAME'] = 'relab'  # El nombre de la base de datos
app.config['DB_USER'] = 'postgres'  # El usuario de la base de datos
app.config['DB_PASSWORD'] = 'unicesmag'  # La contraseña del usuario de la base de datos

voltaje_VCA_inversor_fotovoltaica = 0.0  # <-- ¡esto es lo que faltaba!
codigo_VCA_inversor_fotovoltaica = 0.0  # <-- ¡esto es lo que faltaba!
voltaje_VDC_hidrica = 0.0  # <-- ¡esto es lo que faltaba!
codigo_VDC_hidrica = 0.0  # <-- ¡esto es lo que faltaba!
caudal_hidrica = 0.0  # <-- ¡esto es lo que faltaba!
presion_hidrica = 0.0  # <-- ¡esto es lo que faltaba!
corriente_hidrica = 0.0  # <-- ¡esto es lo que faltaba!

lock = threading.Lock()

# Definir una función para obtener la conexión a la base de datos
def get_db_connection():
    # Establecer una conexión a la base de datos utilizando los parámetros configurados en la aplicación
    conn = psycopg2.connect(
        host=app.config['DB_HOST'],
        database=app.config['DB_NAME'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD']
    )
    return conn  # Devolver la conexión a la base de datos
################################################################################################################################################
#--------------------------------------------------------AUTENTICACIONY LOGUEO------------------------------------------------------------------
################################################################################################################################################

# Ruta para la página de inicio de sesión
@app.route('/')
@app.route('/inicio_sesion')
def inicio_sesion():
    # Obtener el ID de usuario de la sesión actual
    user_id = session.get('user_id')    
    # Verificar si el usuario ha iniciado sesión
    if user_id is not None:
        # Si el usuario ha iniciado sesión, redirigir a la página principal
        return redirect(url_for('inicio_principal'))    
    # Si el usuario no ha iniciado sesión, renderizar la página de inicio de sesión
    return render_template('autenticacion_y_registro/index.html')

# Ruta para manejar el inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    print("Entro Login")    
    # Verificar si el método de la solicitud es POST
    if request.method == 'POST': 
        mail = request.form['cor_usu']  # Obtener el correo del usuario desde el formulario
        password = request.form['con_usu']  # Obtener la contraseña del usuario desde el formulario        
        # Encriptar la contraseña ingresada a MD5
        password_md5 = hashlib.md5(password.encode()).hexdigest()        
        # Buscar el usuario y la contraseña en la base de datos por su correo y contraseña
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT id_usu, per_usu FROM usuario WHERE cor_usu=%s AND con_usu=%s;', (mail, password_md5))
                user = cur.fetchone()  # Obtener el primer resultado de la consulta        
        # Verificar si se encontró un usuario con las credenciales proporcionadas
        if user is not None:
            session.permanent = True
            session['user_id'] = user[0]  # Guardar el ID del usuario en la sesión
            session['user_rol'] = user[1]  # Guardar el rol del usuario en la sesión
            return 'success'  # Devolver 'success' si el inicio de sesión es exitoso
        else:
            return 'error'  # Devolver 'error' si las credenciales son incorrectas

# Ruta para manejar el registro de una nueva cuenta (POST)
@app.route('/registro', methods=['GET', 'POST'])
def registro():    
    print("Entro Registrar")    
    if request.method == 'POST':        
        # Obtener los datos del formulario
        nombres = request.form['nom_usu']
        apellidos = request.form['ape_usu']
        correo = request.form['cor_usu']
        numero_documento = request.form['doc_usu']
        contra = request.form['con_usu']        
        # Codificar la contraseña en formato MD5
        password_md5 = hashlib.md5(contra.encode()).hexdigest()        
        # Buscar el usuario en la base de datos por su correo electrónico o número de documento
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT cor_usu, doc_usu FROM usuario WHERE cor_usu=%s OR doc_usu=%s;', (correo, numero_documento))
                user_exis = cur.fetchone()
                print(user_exis)                
                if user_exis is not None:
                    # Si el usuario ya existe, devolver 'exist'
                    print("El usuario ya existe en la base de datos")
                    return 'exist' 
                else:                     
                    # Si el usuario no existe, insertar el nuevo usuario en la base de datos
                    cur.execute("""
                        INSERT INTO usuario (nom_usu, ape_usu, cor_usu, doc_usu, con_usu)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (nombres, apellidos, correo, numero_documento, password_md5))
                    conn.commit()
                    print("Nuevo usuario agregado correctamente")
                    return 'success' 
    # Si el método no es POST, renderizar el formulario de registro
    return render_template('autenticacion_y_registro/registro.html')

# Página principal
@app.route('/inicio_principal')
def inicio_principal():
    user_id = session.get('user_id')    
    if user_id is None:
        # Si el usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
        return redirect(url_for('inicio_sesion'))    
    # Obtener más información del usuario a partir de su ID
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Ejecutar una consulta SQL para obtener el ID del usuario
            cur.execute(f'SELECT id_usu FROM usuario WHERE id_usu={user_id};')
            user = cur.fetchone()    
    # Renderizar la plantilla HTML de la página principal y pasar los datos del usuario
    return render_template('autenticacion_y_registro/pagina principal.html', user=user)

#Cerrar Sesion        
@app.route('/logout')
def logout():
    # Pausar la recolecta de datos
    user_id = session.get('user_id') 
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('UPDATE proyecto_fotovoltaica SET eje_pro = %s WHERE id_usu = %s;', (False,user_id))
            cur.execute('UPDATE proyecto_hidrica SET eje_pro = %s WHERE id_usu = %s;', (False,user_id))
            conn.commit()
    # Borrar la información de la sesión
    session.clear()
    # Redireccionar a la página de inicio o a donde prefieras
    return redirect(url_for('inicio_sesion'))  

################################################################################################################################################

# Ruta para editar el perfil del usuario
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile(): 
    if request.method == 'POST':
        print("entro")        
        # Obtener el ID del usuario de la sesión
        id_usu = session.get('user_id')        
        # Obtener los datos del formulario
        cor_usu = request.form['cor_usu']
        password = request.form['con_usu']         
        # Conectar a la base de datos
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Verificar si ya existe otro usuario con el mismo correo electrónico
                cur.execute("""
                    SELECT cor_usu FROM usuario WHERE cor_usu = %s AND id_usu != %s
                """, (cor_usu, id_usu))
                user_exis = cur.fetchone()                
                if user_exis is None:
                    # Obtener la información actual del usuario
                    cur.execute(f"""SELECT cor_usu, con_usu FROM usuario WHERE id_usu={id_usu};""")
                    user_data = cur.fetchone()                    
                    # Actualizar el correo electrónico del usuario
                    cur.execute('''
                        UPDATE usuario SET cor_usu = %s WHERE id_usu = %s
                    ''', (cor_usu, id_usu))                    
                    # Actualizar la contraseña si no es el valor por defecto
                    if password != "***************":
                        # Codificar la nueva contraseña en MD5
                        password_md5 = hashlib.md5(password.encode()).hexdigest()
                        cur.execute('''
                            UPDATE usuario SET con_usu = %s WHERE id_usu = %s
                        ''', (password_md5, id_usu))                    
                    # Redirigir con un mensaje de éxito
                    success = '1'
                    return redirect(url_for('edit_profile', success=success))
                else:
                    # Redirigir con un mensaje de error si el correo ya está en uso
                    error = '2'
                    return redirect(url_for('edit_profile', error=error))
    
    # Si el método no es POST
    success = request.args.get('success')
    error = request.args.get('error')    
    # Obtener el ID del usuario de la sesión
    user_id = session.get('user_id')    
    if user_id is None:
        # Si el usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
        return redirect(url_for('inicio_sesion'))    
    # Conectar a la base de datos
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Obtener la información del usuario
            cur.execute(f"""SELECT u.nom_usu, u.ape_usu, u.doc_usu, u.cor_usu, u.con_usu, r.tip_rol 
            FROM usuario u JOIN roles r ON u.id_rol = r.id_rol
            WHERE u.id_usu = {user_id};""")
            user_data = cur.fetchone()
            print(user_data)            
            # Si se encontró al usuario, asignar los datos
            if user_data:
                user = {
                    "nom_usu": user_data[0],
                    "ape_usu": user_data[1],
                    "doc_usu": user_data[2],
                    "cor_usu": user_data[3],
                    "con_usu": user_data[4],
                    "tip_rol": user_data[5],
                    "id_usu": user_id
                }            
            # Renderizar el template con los datos del usuario y los mensajes de éxito/error
            if success == "1" or error == "2":
                return render_template('autenticacion_y_registro/edit_profile.html', success=success, error=error, user=user)
            else:
                return render_template('autenticacion_y_registro/edit_profile.html', user=user)

# Ruta para editar el perfil de un usuario por parte del administrador
@app.route('/update_user', methods=['GET', 'POST'])
def update_user():
    if request.method == 'POST':  # Verifica si la solicitud es POST
        user_id = session.get('user_id')  # Obtiene el ID del usuario autenticado de la sesión
        id_usu = int(request.form['id_usu'])  # Obtiene el ID del usuario del formulario
        nom_usu = request.form['nom_usu']  # Obtiene el nombre del usuario del formulario
        ape_usu = request.form['ape_usu']  # Obtiene el apellido del usuario del formulario
        per_usu = request.form['per_usu']  # Obtiene el perfil del usuario del formulario
        doc_usu = request.form['doc_usu']  # Obtiene el documento del usuario del formulario
        id_rol = request.form['rol_usu']  # Obtiene el rol del usuario del formulario
                
        # Conectar a la base de datos y actualizar el usuario
        with get_db_connection() as conn:  # Abre una conexión a la base de datos
            with conn.cursor() as cur:  # Crea un cursor para ejecutar las consultas
                # Verificar si el usuario es diferente del usuario autenticado
                if id_usu != user_id:  # Si el ID del usuario del formulario no es el mismo que el ID del usuario autenticado
                    cur.execute('UPDATE usuario SET per_usu = %s WHERE id_usu = %s;', (per_usu, id_usu))  # Actualiza el perfil del usuario
                
                cur.execute('''
                    UPDATE usuario 
                    SET nom_usu = %s, ape_usu = %s, doc_usu = %s, id_rol = %s 
                    WHERE id_usu = %s;
                ''', (nom_usu, ape_usu, doc_usu, id_rol, id_usu))  # Actualiza los datos del usuario
                
                conn.commit()  # Guarda cambios en la base de datos
        
        success = '1'  # Establece un indicador de éxito
        return redirect(url_for('update_user', success=success))  # Redirige a la misma página con el indicador de éxito

    success = request.args.get('success')  # Obtiene el indicador de éxito de los parámetros de la URL
    error = request.args.get('error')  # Obtiene el indicador de error de los parámetros de la URL
    user_id = session.get('user_id')  # Obtiene el ID del usuario autenticado de la sesión
    if user_id is None:  # Si el usuario no ha iniciado sesión
        return redirect(url_for('inicio_sesion'))  # Redirige a la página de inicio de sesión   
    
    # Obtener más información del usuario a partir de su ID
    with get_db_connection() as conn:  # Abre una conexión a la base de datos
        with conn.cursor() as cur:  # Crea un cursor para ejecutar las consultas
            cur.execute('SELECT per_usu FROM usuario WHERE id_usu = %s;', (user_id,))  # Obtiene el perfil del usuario autenticado
            user = cur.fetchone()  # Obtiene el resultado de la consulta
                        
            if user[0] == 'Administrador':  # Si el usuario autenticado es un Administrador
                cur.execute('''
                    SELECT * FROM roles;
                ''')  # Obtiene todos los roles
                rol = cur.fetchall()  # Obtiene todos los resultados de la consulta
                cur.execute('''
                    SELECT * FROM usuario
                    JOIN roles ON usuario.id_rol = roles.id_rol;
                ''')  # Obtiene todos los usuarios y sus roles
                edit_usu = cur.fetchall()  # Obtiene todos los resultados de la consulta
                
                if success == "1" or error == "2":  # Si hay un indicador de éxito o error
                    return render_template('autenticacion_y_registro/edit_user.html', success=success, error=error, rol=rol, edit_usu=edit_usu)  # Renderiza la plantilla con los datos obtenidos
                else:
                    return render_template('autenticacion_y_registro/edit_user.html', rol=rol, edit_usu=edit_usu)  # Renderiza la plantilla con los datos obtenidos
            else:
                return redirect(url_for('inicio_principal'))  # Si el usuario no es Administrador, redirige a la página principal
            
################################################################################################################################################
#--------------------------------------------ESTACION DAVIS --------------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################


# Conexión de la estación meteorológica con el sistema de información
def davis():
    # Inicia una función llamada `davis` que se ejecutará indefinidamente.
    while True:
        print("Dato recibido")
        
        # Llaves de la API (se usan para autenticar y acceder a los datos).
        API_KEY = "jxhpskyfalmhlegx9mwqnwplcpmoltc0"
        STATION_ID = "181874"
        headers = {"X-Api-Secret": "sxchcxmtchcydblvcgbknst9mumap1cq"}

        # Obtiene el timestamp actual y define el rango de tiempo de 40 días hacia atrás.
        end_timestamp = int(time.time())
        start_timestamp = end_timestamp - (40 * 24 * 3600)

        # Duración máxima permitida para cada consulta (86400 segundos = 1 día).
        max_duration_seconds = 86400

        # Bucle para procesar datos en bloques de tiempo.
        while end_timestamp > start_timestamp:
            current_start = max(end_timestamp - max_duration_seconds, start_timestamp)
            url = f"https://api.weatherlink.com/v2/historic/{STATION_ID}?api-key={API_KEY}&start-timestamp={current_start}&end-timestamp={end_timestamp}"
            
            try:
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json().get('sensors', [])
                    db_data = []

                    for sensor in data:
                        for inner_data in sensor.get('data', []):
                            ts = inner_data.get('ts')
                            avg, hi, temp_avg = inner_data.get('solar_rad_avg'), inner_data.get('solar_rad_hi'),round((inner_data.get('temp_out') - 32) * 5.0 / 9.0, 1)
                            db_data.append(((avg, hi, temp_avg), datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')))

                    # Guardar los datos en la base de datos
                    with get_db_connection() as conn:
                        with conn.cursor() as cursor:
                            cursor.executemany("""
                                INSERT INTO dato_irradiancia (prom_irr, max_irr, temp_irr, created_at)
                                VALUES (%s, %s, %s,%s)
                                ON CONFLICT (created_at) DO NOTHING
                            """, [(prom, max_,temp, created_at) for (prom, max_, temp), created_at in db_data])
                            conn.commit()
                elif response.status_code == 400:
                    print("Error 400: Solicitud incorrecta", response.json())

            except requests.RequestException as e:
                print(f"Error en la API: {e}")

            end_timestamp = current_start - 1
        print("Datos guardados en la base de datos.")
        # Revisar y completar datos faltantes en los últimos 30 días
        revisar_completar_datos_faltantes() 
        ejecutar_proyecto()
        time.sleep(300)

# Función para revisar y completar datos faltantes en los últimos 30 días
def revisar_completar_datos_faltantes():
    # Definir el rango de 30 días
    end_date = datetime.now()
    start_date = end_date - timedelta(days=40)
    print(end_date)
    print(start_date)
    # Recuperar todos los datos de los últimos 30 días desde la base de datos
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT prom_irr, max_irr, created_at
                FROM dato_irradiancia
                WHERE created_at >= %s AND created_at <= %s
                ORDER BY created_at ASC
            """, (start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S')))
            records = cursor.fetchall()

    # Verificar intervalos de tiempo faltantes en los datos obtenidos
    interpolated_data = []
    last_timestamp = None

    for row in records:
        prom_irr, max_irr, created_at = row
        ts = int(created_at.timestamp())  # Utilizar directamente `created_at.timestamp()` en lugar de `strptime`

        if last_timestamp and ts - last_timestamp > 300:
            # Interpolación para intervalos de 5 minutos faltantes
            missing_intervals = (ts - last_timestamp) // 300
            for i in range(1, missing_intervals):
                missing_ts = last_timestamp + i * 300
                previous_year_data = get_previous_year_data(missing_ts)

                if previous_year_data and previous_year_data[0] is not None:
                    interpolated_entry = (previous_year_data[0], previous_year_data[1], datetime.fromtimestamp(missing_ts).strftime('%Y-%m-%d %H:%M:%S'))
                    print("Dato interpolado IF:", interpolated_entry)
                else:
                    interpolated_entry = (0, 0, datetime.fromtimestamp(missing_ts).strftime('%Y-%m-%d %H:%M:%S'))

                    print("Dato interpolado ELSE :", interpolated_entry)
                interpolated_data.append(interpolated_entry)

        last_timestamp = ts

    # Insertar los datos interpolados en la base de datos
    if interpolated_data:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.executemany("""
                    INSERT INTO dato_irradiancia (prom_irr, max_irr, created_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (created_at) DO NOTHING
                """, interpolated_data)
                conn.commit()

    ejecutar_proyecto()


# Función para obtener datos del año anterior para un timestamp específico
def get_previous_year_data(ts):
    query = "SELECT prom_irr, max_irr FROM dato_irradiancia WHERE created_at = %s"
    one_year_ago = (datetime.fromtimestamp(ts) - timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (one_year_ago,))
            result = cursor.fetchone()
            return result if result else (None, None)
        
# Crear un hilo para la función davis
data_fetch_thread = threading.Thread(target=davis)
data_fetch_thread.daemon = True  # Para asegurarse de que el hilo se detenga al cerrar la aplicación
data_fetch_thread.start()

#Ruta para ir a la seccion de datos de irradiancia
@app.route('/irradiance_display',methods=['GET', 'POST'])
def irradiance_display():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('inicio_sesion'))  
    
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        start_date = f"{start_date} 06:00:00"  # Agrega hora 06:00:00 a la fecha de inicio
        end_date = f"{end_date} 19:00:00"      # Agrega hora 19:00:00 a la fecha final

        # Redirige a la misma ruta con parámetros en la URL para evitar el reenvío del formulario
        return redirect(url_for('irradiance_display', start_date=start_date, end_date=end_date))

    # Procesa los datos de la base de datos
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if start_date and end_date:
                cur.execute('SELECT prom_irr, max_irr, created_at,temp_irr FROM dato_irradiancia WHERE (created_at >= %s and created_at <= %s) ORDER BY created_at;', (start_date, end_date))
            else:
                cur.execute('SELECT prom_irr, max_irr, created_at,temp_irr FROM dato_irradiancia WHERE created_at::date = CURRENT_DATE ORDER BY created_at;')
            db_irr = cur.fetchall()
            
    return render_template('informe_y_Estadistica/date_davis.html', db_irr=db_irr)

# Ruta para obtener los últimos datos de irradiación en formato JSON
@app.route('/get_latest_irradiance_data')
def get_latest_irradiance_data():
    # Suponiendo que tienes una función para obtener la conexión a la base de datos
    with get_db_connection() as conn:  
        with conn.cursor() as cur:  
            cur.execute('SELECT prom_irr, max_irr, created_at, temp_irr FROM dato_irradiancia ORDER BY created_at DESC LIMIT 1')  # Ordena por fecha de creación
            db_irr = cur.fetchall()  # Obtiene todos los resultados de la consulta
            
    # Estructura los datos en una lista de diccionarios
    data = [{'prom_irr': f"{float(row[0]):.1f}", 'max_irr': f"{float(row[1]):.1f}", 'created_at': row[2].strftime('%Y-%m-%d %H:%M:%S'), 'temp_out': f"{float(row[3]):.1f}"} for row in db_irr]
    
    return jsonify(data)  # Devuelve los datos en formato JSON

################################################################################################################################################
#---------------------------------------------------DATOS DE DEMANDA-------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################

def consultas_demanda(start_date, end_date):
    # Obtener más información de los datos tomados con el HIOKI
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if not start_date or not end_date:
                cur.execute("SELECT MAX(created_at) FROM dato_demanda")
                last_date = cur.fetchone()[0]  # Obtener la última fecha
                if last_date:
                    start_date = (last_date - timedelta(days=19)).strftime('%Y-%m-%d')
                    end_date = last_date.strftime('%Y-%m-%d')

            # Parámetros de fecha
            date_params = (start_date, end_date)

            # Consulta para db_dem
            cur.execute("""
                SELECT SUM(dat_dem) AS total_dem, to_char(created_at, 'YYYY-MM-DD HH24:00:00') AS datetime
                FROM dato_demanda WHERE created_at >= %s AND created_at < %s
                GROUP BY to_char(created_at, 'YYYY-MM-DD HH24:00:00')
                ORDER BY to_char(created_at, 'YYYY-MM-DD HH24:00:00') DESC;
            """, date_params)
            db_dem = cur.fetchall()

            # Consulta para db_ana_dem
            cur.execute("""
                SELECT fec_adem, exc_adem, con_adem, per_adem 
                FROM analisis_demanda WHERE fec_adem >= %s AND fec_adem < %s
                ORDER BY fec_adem ASC;
            """, date_params)
            db_ana_dem = cur.fetchall()
            # Consultas promedio
            consulta_promedio_sql = """
                SELECT %s AS nom_adem, round(CAST(AVG({column}) AS numeric), 2)
                FROM analisis_demanda WHERE fec_adem >= %s AND fec_adem < %s {extra_condition};
            """
            consulta_promedio = [
                ('Promedio consumo neto', 'exc_adem', 'AND per_adem < -2500 AND per_adem IS NOT NULL'),
                ('Promedio actual neto', 'con_adem', 'AND per_adem < -2500 AND per_adem IS NOT NULL'),
                ('Energía perdida', 'per_adem', 'AND per_adem < -2500 AND per_adem IS NOT NULL'),
                ('Pagaría a full', 'con_adem', 'AND per_adem IS NULL')
            ]

            consult_promedio = []
            for nom_adem, column, extra_condition in consulta_promedio:
                cur.execute(consulta_promedio_sql.format(column=column, extra_condition=extra_condition), (nom_adem, *date_params))
                result = cur.fetchone()
                consult_promedio.append((result[0], float(result[1]) if result and result[1] is not None else 0.0))


            # Consultas neto
            consulta_neto_sql = """
                SELECT %s AS nom_adem, round(CAST(SUM({column}) AS numeric), 2)*{factor}
                FROM analisis_demanda WHERE fec_adem >= %s AND fec_adem < %s {extra_condition};
            """
            consulta_neto = [
                ('Consumo neto', 'exc_adem', 1.5, ''),
                ('Consumo actual neto', 'con_adem', 1.5, ''),
                ('Energía perdida', 'per_adem', 1.5, ''),
                ('Pagaría a full', 'con_adem', 10, 'AND per_adem IS NULL')
            ]

            consult_neto = []
            for nom_adem, column, factor, extra_condition in consulta_neto:
                cur.execute(consulta_neto_sql.format(column=column, factor=factor, extra_condition=extra_condition), (nom_adem, *date_params))
                result = cur.fetchone()
                consult_neto.append((result[0], float(result[1]) if result and result[1] is not None else 0.0))



    return db_dem, db_ana_dem, consult_promedio, consult_neto


@app.route('/demand_display', methods=['GET', 'POST'])
def demand_display():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('inicio_sesion'))

    start_date = end_date = costo = None
    error_file = False

    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        try:
            costo = float(request.form.get('costo_energia', 0.0))  # Default value 0.0 if not provided
        except (ValueError, TypeError):
            costo = 0.0  # O cualquier valor predeterminado


        if not start_date or not end_date:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT MAX(created_at) FROM dato_demanda")
                    last_date = cursor.fetchone()[0]
            
            if last_date:
                start_date = (last_date - timedelta(days=10)).strftime('%Y-%m-%d')
                end_date = last_date.strftime('%Y-%m-%d')

        # Procesar archivo excel si existe
        file = request.files.get('file')
        if file and file.filename.endswith('.xlsx'):
            try:
                df_modelo = pd.read_excel(file, sheet_name='97intvl')
                required_columns = {'Date', 'Time', 'AvePsum'}
                if not required_columns.issubset(df_modelo.columns):
                    error_file = True
                else:
                    df_modelo['Datetime'] = pd.to_datetime(df_modelo['Date'].astype(str) + ' ' + df_modelo['Time'].astype(str))
                    data_to_insert = df_modelo[['Datetime', 'AvePsum']].values.tolist()
            except ValueError:
                error_file = True

            if not error_file:
                with get_db_connection() as conn:
                    with conn.cursor() as cursor:
                        duplicado = False
                        for date_time, ave_psum in data_to_insert:
                            cursor.execute("""
                                SELECT 1 FROM dato_demanda
                                WHERE dat_dem = %s AND created_at = %s AND id_usu = %s
                            """, (ave_psum, date_time, user_id))

                            if cursor.fetchone():
                                duplicado = True
                                break

                            cursor.execute("""
                                INSERT INTO dato_demanda (dat_dem, created_at, id_usu)
                                VALUES (%s, %s, %s)
                            """, (ave_psum, date_time, user_id))

                        conn.commit()

                        if not duplicado:
                            # Consultas de análisis
                            db_dem, db_ana_dem, consult_promedio, consult_neto = consultas_demanda(start_date, end_date)
                            return render_template(
                                'informe_y_Estadistica/date_hioki.html',
                                db_dem=db_dem, db_ana_dem=db_ana_dem,
                                consult_promedio=consult_promedio, consult_neto=consult_neto,
                                costo=costo
                            )

    # Consultas sin archivo cargado
    db_dem, db_ana_dem, consult_promedio, consult_neto = consultas_demanda(start_date, end_date)
    return render_template(
        'informe_y_Estadistica/date_hioki.html',
        db_dem=db_dem, db_ana_dem=db_ana_dem,
        consult_promedio=consult_promedio, consult_neto=consult_neto, costo=costo
    )


################################################################################################################################################

#PREDICCION DE IRRADIANCIA
@app.route('/irradiance_prediction')
def irradiance_prediction():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('inicio_sesion'))
    
    prediction_g = 1
    # Ruta donde se encuentra el modelo
    ruta = 'C:/PROYECTO/Relab/pro_relab/energia_renovable/modelo/'
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT prom_irr, created_at 
                FROM (
                    SELECT prom_irr, created_at 
                    FROM dato_irradiancia 
                    WHERE created_at::time >= '06:00:00' 
                    AND created_at::time <= '19:00:00' 
                    AND created_at::date < current_date
                    AND created_at::date BETWEEN current_date - INTERVAL '30 days' AND current_date - INTERVAL '1 day'
                    ORDER BY created_at DESC 
                ) as consulta
                ORDER BY created_at ASC;
            """)
            db = cur.fetchall()

    # Convertir los resultados a un DataFrame de pandas
    df = pd.DataFrame(db, columns=["prom_irr", "created_at"])

    # Establecer la columna 'created_at' como índice para el formato tabular (asignando el resultado)
    df_filtrado_nuevos_datos = df.set_index('created_at', inplace=False)
    print(df_filtrado_nuevos_datos)
    # Extraer los valores de irradiancia
    DATOS_NUEVOS = df_filtrado_nuevos_datos['prom_irr'].values


    # Escalar los nuevos datos entre -1 y 1
    scaler_nuevos = MinMaxScaler(feature_range=(-1, 1))
    datos_nuevos_escalados = scaler_nuevos.fit_transform(DATOS_NUEVOS.reshape(-1, 1))

    # Definir las secuencias para entrenamiento y predicción basados en el tamaño de las secuencias de entrada
    Dias_pasados = 7  # N
    LONG_SEC = 157 * Dias_pasados  # Tamaño de entrada
    Dias_futuros = 1  # Número de días a predecir
    N_STEPS = 157  # Tamaño de salida (para 1 día, 156 valores)

    print(f"Tamaño de los datos escalados nuevos: {len(datos_nuevos_escalados)}")

    # Generar secuencias solo si hay suficientes datos
    if len(datos_nuevos_escalados) > LONG_SEC + N_STEPS:
        X_train_nuevos, Y_train_nuevos = [], []
        for i in range(len(datos_nuevos_escalados) - LONG_SEC - N_STEPS):
            X_train_nuevos.append(datos_nuevos_escalados[i:i + LONG_SEC])
            Y_train_nuevos.append(datos_nuevos_escalados[i + LONG_SEC:i + LONG_SEC + N_STEPS])  # Ajuste para N_STEPS

        # Convertir a arrays de numpy
        X_train_nuevos = np.array(X_train_nuevos)
        Y_train_nuevos = np.array(Y_train_nuevos)

        # Verificar la forma de Y_train_nuevos para asegurarse de que sea [batch_size, N_STEPS]
        print(f"Forma de Y_train_nuevos: {Y_train_nuevos.shape}")  # Debe ser [batch_size, N_STEPS]

        # Imprimir el tamaño de las secuencias antes del reshape
        print(f"Forma de X_train_nuevos antes del reshape: {X_train_nuevos.shape}")

        # Reestructurar para que tenga la forma adecuada para el modelo (batch_size, time_steps, features)
        X_train_nuevos = np.reshape(X_train_nuevos, (X_train_nuevos.shape[0], X_train_nuevos.shape[1], 1))
        print(f"Forma de X_train_nuevos después del reshape: {X_train_nuevos.shape}")
    ################################################################################
        # Cargar el modelo ya entrenado para su reentrenamiento
        modelo = tf.keras.models.load_model(ruta + '20x2_17Model.keras')

        # Reentrenar el modelo con los nuevos datos
        EPOCHS = 10
        BATCH_SIZE = 64
        #historial = modelo.fit(X_train_nuevos, Y_train_nuevos, batch_size=BATCH_SIZE, epochs=EPOCHS, verbose=1)

        # Predicción multistep para días futuros
        # Usar el último segmento de datos escalados para predecir los días futuros
        ultimo_X = datos_nuevos_escalados[-LONG_SEC:].reshape(1, LONG_SEC, 1)

        predicciones_futuras = []
        num_predicciones = Dias_futuros * 157  # 156 valores por día

        for i in range(int(num_predicciones // N_STEPS)):
            # Hacer la predicción usando el último punto disponible
            pred_nueva = modelo.predict(ultimo_X)
            
            predicciones_futuras.extend(pred_nueva[0])  # Agrega todos los pasos predichos

            # Actualizar el último_X para incluir la nueva predicción
            ultimo_X = np.roll(ultimo_X, -N_STEPS, axis=1)
            ultimo_X[0, -N_STEPS:, 0] = pred_nueva[0].flatten()  # Aplanar el array antes de asignarlo

        # Transformar las predicciones de vuelta a la escala original        
        predicciones_futuras = np.array(predicciones_futuras).reshape(-1, 1)        
        predicciones_futuras_inv = scaler_nuevos.inverse_transform(predicciones_futuras)
        
        # Obtener la fecha y hora actuales
        fecha_hora_actual = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)

        # Sumar un día y establecer la hora a las 6:00
        print('Esta es la fecha del dia sguiente: ')
        fecha_actual = (fecha_hora_actual + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
        print(fecha_actual)

        eje_x_pred = []
        while len(eje_x_pred) < len(predicciones_futuras_inv):
            if 6 <= fecha_actual.hour <= 19:  # Solo horas de 6:00 a 19:00
                eje_x_pred.append(fecha_actual)
            fecha_actual += pd.Timedelta(minutes=5)
        
        # Crear DataFrame para las predicciones
        db_irr = pd.DataFrame({
            'fecha': eje_x_pred,
            'predicciones': predicciones_futuras_inv.flatten()
        })
        # Ajustar las predicciones para que no sean menores que 0
        db_irr['predicciones'] = db_irr['predicciones'].apply(lambda x: 0 if x < 1 else x)
        print('datosssss',db_irr)
    else:
        print("No hay suficientes datos para generar secuencias de entrenamiento")
    return render_template('informe_y_Estadistica/date_davis.html',prediction_g = prediction_g, db_irr=db_irr.to_dict(orient='records'))
    
################################################################################################################################################
#--------------------------------------------CREAR COMPONENTES Y EDITARLOS-------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################

#mostrar modal panel
@app.route('/ver_modal_panel')
def ver_modal_panel():
    # Conectar a la base de datos
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Ejecutar la consulta para obtener todas las tecnologías de panel
            cur.execute('SELECT * FROM tecnologia_panel;')
            tecno = cur.fetchall()  # Obtener todos los resultados de la consulta

    # Pasar los resultados a la plantilla
    return render_template('creacion_de_componentes/crea_panel.html', tecno=tecno)

#mostrar modal inversor
@app.route('/ver_modal_inversor')
def ver_modal_inversor():    
    return render_template('creacion_de_componentes/crea_inversor.html')

#mostrar modal bateria
@app.route('/ver_modal_bateria')
def ver_modal_bateria():
    return render_template('creacion_de_componentes/crea_bateria.html')

#mostrar modal regulador
@app.route('/ver_modal_regulador')
def ver_modal_regulador():
    return render_template('creacion_de_componentes/crea_regulador.html')

################################################################################################################################################

# Crear panel modal       
@app.route('/add_panel', methods=['POST'])
def add_panel():
    ref_pan = request.form['ref_pan']
    idu_pan = request.form['idu_pan']
    pmax_pan = float(request.form['pmax_pan'])  # Convierte los valores a números flotantes
    vmp_pan = float(request.form['vmp_pan'])
    imp_pan = float(request.form['imp_pan'])
    voc_pan = float(request.form['voc_pan'])
    isc_pan = float(request.form['isc_pan'])
    lar_pan = float(request.form['lar_pan'])
    anc_pan = float(request.form['anc_pan'])
    efi_pan = float(request.form['efi_pan'])
    are_pan = lar_pan * anc_pan
    nom_tec = request.form['tec_pan']
    den_pan = pmax_pan / are_pan
    user_id = session.get('user_id')
    pmax_cal_pan = vmp_pan * imp_pan

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Buscar tecnología en la base de datos
            cur.execute('SELECT * FROM tecnologia_panel WHERE nom_tec = %s;', (nom_tec,))
            tecno = cur.fetchone()

            # Si la tecnología no existe, insertarla
            if tecno is None:
                cur.execute('INSERT INTO tecnologia_panel (nom_tec) VALUES (%s) RETURNING id_tec;', (nom_tec,))
                id_tec = cur.fetchone()[0]
                conn.commit()  # Confirmar la inserción de la nueva tecnología
            else:
                id_tec = tecno[0]  # Suponiendo que el id_tec es la primera columna

            # Buscar el panel en la base de datos
            cur.execute('SELECT * FROM panel WHERE idu_pan = %s AND status = %s;', (idu_pan, True))
            panel = cur.fetchone()

            # Verificar si el panel ya existe
            if panel is not None:
                return 'exist'

            # Validar la potencia máxima calculada
            if pmax_cal_pan > pmax_pan - 0.6 and pmax_cal_pan < pmax_pan + 0.6:
                cur.execute('''
                    INSERT INTO panel (ref_pan, efi_pan, idu_pan, pmax_pan, vmp_pan, imp_pan, voc_pan, isc_pan, lar_pan, anc_pan, are_pan, id_tec, den_pan, id_usu)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                ''', (ref_pan, efi_pan, idu_pan, pmax_pan, vmp_pan, imp_pan, voc_pan, isc_pan, lar_pan, anc_pan, are_pan, id_tec, den_pan, user_id))
                conn.commit()  # Confirmar la inserción del nuevo panel

                return 'success'
            else:
                return 'error'

# Crear inversor modal
@app.route('/add_inversor', methods=['POST'])
def add_inversor():
    ref_inv = request.form['ref_inv']
    reg_inv = request.form['reg_inv']
    idu_inv = request.form['idu_inv']
    ent_inv = request.form['ent_inv']
    pmax_inv = float(request.form['pmax_inv'])  # Convierte los valores a números flotantes
    vme_inv = float(request.form['vme_inv'])
    ime_inv = float(request.form['ime_inv'])
    vsa_inv = float(request.form['vsa_inv'])
    ond_inv = request.form['ond_inv']
    efi_inv = float(request.form['efi_inv'])
    user_id = session.get('user_id')
    
    pmax_cal_inv = vme_inv * ime_inv  # Calcula la potencia máxima

    # Conectar a la base de datos y buscar si el inversor ya existe
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Buscar el inversor en la base de datos
            cur.execute('SELECT * FROM inversor WHERE idu_inv = %s AND status = %s;', (idu_inv, True))
            inversor = cur.fetchone()

            # Verificar si los datos ya existen en la base de datos
            if inversor is not None:
                return 'exist'

            # Verificar la potencia máxima calculada
            if pmax_cal_inv > pmax_inv - 0.6 and pmax_cal_inv < pmax_inv + 0.6:
                # Insertar el nuevo inversor
                cur.execute('''
                    INSERT INTO inversor (ref_inv, reg_inv, idu_inv, ent_inv, pmax_inv, vme_inv, ime_inv, vsa_inv, ond_inv, efi_inv, id_usu)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                ''', (ref_inv, reg_inv, idu_inv, ent_inv, pmax_inv, vme_inv, ime_inv, vsa_inv, ond_inv, efi_inv, user_id))

                conn.commit()  # Confirmar la inserción
                return 'success'
            else:
                return 'error'

# Crear bateria modal
@app.route('/add_bateria', methods=['POST'])
def add_bateria():
    ref_bat = request.form['ref_bat']
    vol_bat = float(request.form['vol_bat'])
    cap_bat = float(request.form['cap_bat'])
    ene_bat = vol_bat * cap_bat
    idu_bat = request.form['idu_bat']
    user_id = session.get('user_id')

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Buscar la batería en la base de datos
            cur.execute('SELECT * FROM bateria WHERE idu_bat = %s AND status = %s;', (idu_bat, True))
            bateria = cur.fetchone()

            # Verificar si la batería ya existe en la base de datos
            if bateria is not None:
                return 'exist'

            # Si la batería no existe, agregar una nueva
            cur.execute('''
                INSERT INTO bateria (ref_bat, idu_bat, vol_bat, cap_bat, ene_bat, id_usu)
                VALUES (%s, %s, %s, %s, %s, %s);
            ''', (ref_bat, idu_bat, vol_bat, cap_bat, ene_bat, user_id))
            conn.commit()  # Confirmar la inserción

            return 'success'

# Crear regulador modal
@app.route('/add_regulador', methods=['POST'])
def add_regulador():
    ref_reg = request.form['ref_reg']
    vol_reg = float(request.form['vol_reg'])
    cor_reg = float(request.form['cor_reg'])
    pot_reg = float(request.form['pot_reg'])  
    idu_reg = request.form['idu_reg']
    user_id = session.get('user_id')
    
    pot_cal_reg = vol_reg * cor_reg  # Calcula la potencia máxima

    # Conectar a la base de datos y buscar si el regulador ya existe
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Buscar el regulador en la base de datos
            cur.execute('SELECT * FROM regulador WHERE idu_reg = %s AND status = %s;', (idu_reg, True))
            regulador = cur.fetchone()

            # Verificar si los datos ya existen en la base de datos
            if regulador is not None:
                return 'exist'

            # Verificar la potencia máxima calculada
            if pot_cal_reg > pot_reg - 0.6 and pot_cal_reg < pot_reg + 0.6:
                # Insertar el nuevo regulador
                cur.execute('''
                INSERT INTO regulador (ref_reg, idu_reg, vol_reg, cor_reg, pot_reg, id_usu)
                VALUES (%s, %s, %s, %s, %s, %s);
                ''', (ref_reg, idu_reg, vol_reg, cor_reg, pot_reg, user_id))
                conn.commit()  # Confirmar la inserción
                return 'success'
            else:
                return 'error'

################################################################################################################################################

#Lista de componentes index
@app.route('/component_list')
def component_list():
    user_id = session.get('user_id')
    if user_id is None:
        # Si el usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
        return redirect(url_for('inicio_sesion'))
    return redirect(url_for('update_panel'))
    
#list  paneles
@app.route('/update_panel', methods=['GET', 'POST'])
def update_panel():
    if request.method == 'POST': 
        id_pan = request.form['id_pan']
        ref_pan = request.form['ref_pan']
        est_pan = request.form['est_pan']
        # Mapeo de cadenas a booleanos
        boolean_map = {'True': True, 'False': False}
        est_pan = boolean_map.get(est_pan, False) 
        pmax_pan = float(request.form['pmax_pan'])
        vmp_pan = float(request.form['vmp_pan'])
        imp_pan = float(request.form['imp_pan'])
        voc_pan = float(request.form['voc_pan'])
        isc_pan = float(request.form['isc_pan'])
        lar_pan = float(request.form['lar_pan'])
        anc_pan = float(request.form['anc_pan'])
        are_pan = lar_pan * anc_pan
        nom_tec = request.form['tec_pan']
        den_pan = pmax_pan / are_pan
        user_id = session.get('user_id')

        # Conectar a la base de datos
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Obtener información del panel a partir de su ID
                cur.execute('SELECT * FROM panel WHERE id_pan = %s;', (id_pan,))
                panel_data = cur.fetchone()
                if panel_data:
                    
                    if est_pan == False:
                        cur.execute('''UPDATE panel SET deleted_at = %s WHERE id_pan = %s; ''', (datetime.now() , id_pan))
                        conn.commit()
                    elif est_pan == True:
                        cur.execute('''UPDATE panel SET deleted_at = %s WHERE id_pan = %s; ''', (None , id_pan))
                        conn.commit()
                        
                    # Si el panel existe, se verifica la tecnología
                    cur.execute('SELECT id_tec FROM tecnologia_panel WHERE nom_tec = %s;', (nom_tec,))
                    tecno = cur.fetchone()
                    pmax_cal_pan = vmp_pan * imp_pan
                    # Si la tecnología no existe, crearla
                    if not tecno:
                        cur.execute('INSERT INTO tecnologia_panel (nom_tec) VALUES (%s) RETURNING id_tec;', (nom_tec,))
                        id_tec = cur.fetchone()[0]
                        conn.commit()
                    else:
                        id_tec = tecno[0]
                    # Verificar si el valor calculado de Pmax es válido
                    if pmax_cal_pan > pmax_pan - 0.5 and pmax_cal_pan < pmax_pan + 0.5:
                        
                        # Actualizar los datos del panel
                        cur.execute('''
                            UPDATE panel
                            SET ref_pan = %s, pmax_pan = %s, vmp_pan = %s, imp_pan = %s, voc_pan = %s, isc_pan = %s,
                                lar_pan = %s, anc_pan = %s, id_tec = %s, den_pan = %s, status = %s, id_usu = %s
                            WHERE id_pan = %s;
                        ''', (ref_pan, pmax_pan, vmp_pan, imp_pan, voc_pan, isc_pan, lar_pan, anc_pan, id_tec, den_pan, est_pan, user_id, id_pan))
                        conn.commit()

                        success = '1'
                        return redirect(url_for('update_panel', success=success))
                    else:
                        error = '2'
                        return redirect(url_for('update_panel', error=error))
    success = request.args.get('success')
    error = request.args.get('error')
    user_id = session.get('user_id')
    num_comp = 1
    if user_id is None:
        # Si el usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
        return redirect(url_for('inicio_sesion'))
    
    # Conectar a la base de datos para obtener información del usuario
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Obtener información del usuario desde la base de datos
            cur.execute('SELECT * FROM usuario WHERE id_usu = %s;', (user_id,))
            user = cur.fetchone()
            
            if user and user[4] == 'Administrador':
                # Obtener todas las tecnologías de los paneles
                cur.execute('SELECT * FROM tecnologia_panel;')
                tecno = cur.fetchall()
                
                # Obtener los paneles y las tecnologías asociadas
                cur.execute('''
                    SELECT *
                    FROM panel p 
                    JOIN tecnologia_panel t ON p.id_tec = t.id_tec;
                ''')

                pan_usu = cur.fetchall()
                # Renderizar el template dependiendo de los parámetros 'success' y 'error'
                if success == "1" or error == "2":
                    return render_template(
                        'creacion_de_componentes/index.html',success=success, error=error, tecno=tecno, user_comp=user, pan_usu=pan_usu, num_comp=num_comp)
                else:
                    return render_template('creacion_de_componentes/index.html',tecno=tecno, user_comp=user, pan_usu=pan_usu, num_comp=num_comp )
            else:
                return redirect(url_for('inicio_principal'))

#list  baterias
@app.route('/update_bateria', methods=['GET', 'POST'])
def update_bateria():
    if request.method == 'POST': 
        id_bat = request.form['id_bat']
        ref_bat = request.form['ref_bat']
        vol_bat = float(request.form['vol_bat'])
        cap_bat = float(request.form['cap_bat'])
        ene_bat = vol_bat * cap_bat
        est_bat = request.form['est_bat']
        # Mapeo de cadenas a booleanos
        boolean_map = {'True': True, 'False': False}
        est_bat = boolean_map.get(est_bat, False) 
        user_id = session.get('user_id')

        with get_db_connection() as conn:
            with conn.cursor() as cur:            
                # Si la batería existe, actualizar los datos
                cur.execute('SELECT * FROM bateria WHERE id_bat = %s;', (id_bat,))
                bateria = cur.fetchone()
                if bateria:
                    if est_bat == False:
                        cur.execute(''' UPDATE bateria SET deleted_at = %s WHERE id_bat = %s; ''', (datetime.now() , id_bat))
                        conn.commit()
                    elif est_bat == True:
                        cur.execute(''' UPDATE bateria SET deleted_at = %s WHERE id_bat = %s; ''', (None , id_bat))
                        conn.commit()
                        
                    cur.execute(''' UPDATE bateria
                        SET ref_bat = %s, vol_bat = %s, cap_bat = %s, ene_bat = %s, id_usu = %s,status = %s
                        WHERE id_bat = %s;
                    ''', (ref_bat, vol_bat, cap_bat, ene_bat, user_id,est_bat, id_bat))
                    
                    conn.commit()
                    success = '1'
                    return redirect(url_for('update_bateria', success=success))

        
    success = request.args.get('success')
    user_id = session.get('user_id')
    num_comp = 2
    if user_id is None:
        return redirect(url_for('inicio_sesion'))
    # Conectar a la base de datos
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Obtener más información del usuario
            cur.execute('SELECT * FROM usuario WHERE id_usu = %s;', (user_id,))
            user = cur.fetchone()
            if user and user[4] == 'Administrador':
                # Obtener todas las baterías
                cur.execute('SELECT * FROM bateria;')
                bat_usu = cur.fetchall()
                
                return render_template('creacion_de_componentes/index.html', success=success, user_comp=user, bat_usu=bat_usu, num_comp=num_comp)
            else:
                return redirect(url_for('inicio_principal'))
   
@app.route('/update_inversor', methods=['GET', 'POST'])
def update_inversor(): 
    if request.method == 'POST': 
        id_inv = request.form['id_inv']
        ref_inv = request.form['ref_inv']
        reg_inv = request.form['reg_inv']
        est_inv = request.form['est_inv']
        ent_inv = request.form['ent_inv']
        # Mapeo de cadenas a booleanos
        boolean_map = {'True': True, 'False': False}
        est_inv = boolean_map.get(est_inv, False) 
        pmax_inv = float(request.form['pmax_inv'])
        vme_inv = float(request.form['vme_inv'])
        ime_inv = float(request.form['ime_inv'])
        vsa_inv = float(request.form['vsa_inv'])
        ond_inv = request.form['ond_inv']
        efi_inv = float(request.form['efi_inv'])
        user_id = session.get('user_id')

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                
                # Si el inversor existe, actualizar los datos
                cur.execute('SELECT * FROM inversor WHERE id_inv = %s;', (id_inv,))
                inversor = cur.fetchone()

                if inversor:
                    
                    if est_inv == False:
                        cur.execute(''' UPDATE inversor SET deleted_at = %s WHERE id_inv = %s; ''', (datetime.now() , id_inv))
                        conn.commit()
                    if est_inv == True:
                        cur.execute(''' UPDATE inversor SET deleted_at = %s WHERE id_inv = %s; ''', (None, id_inv))
                        conn.commit()
                        
                    # Verificar la potencia máxima calculada
                    pmax_cal_inv = vme_inv * ime_inv
                    if pmax_cal_inv > pmax_inv - 0.6 and pmax_cal_inv < pmax_inv + 0.6:
                        cur.execute('''
                            UPDATE inversor
                            SET ref_inv = %s, ent_inv = %s, pmax_inv = %s, vme_inv = %s, ime_inv = %s,
                                vsa_inv = %s, ond_inv = %s, efi_inv = %s, id_usu = %s,reg_inv = %s,status=%s
                            WHERE id_inv = %s;
                        ''', (ref_inv, ent_inv, pmax_inv, vme_inv, ime_inv, vsa_inv, ond_inv, efi_inv, user_id,reg_inv,est_inv, id_inv))
                        
                        conn.commit()
                        success = '1'
                        return redirect(url_for('update_inversor', success=success))
                    else:
                        error = '2'
                        return redirect(url_for('update_inversor', error=error))

    success = request.args.get('success')
    error = request.args.get('error')
    user_id = session.get('user_id')
    num_comp=3
    if user_id is None:
        return redirect(url_for('inicio_sesion'))

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Obtener más información del usuario
            cur.execute('SELECT * FROM usuario WHERE id_usu = %s;', (user_id,))
            user = cur.fetchone()

            if user and user[4] == 'Administrador':
                # Obtener todos los inversores
                cur.execute('SELECT * FROM inversor;')
                inv_usu = cur.fetchall()
                
                return render_template('creacion_de_componentes/index.html', error=error, success=success, user_comp=user, inv_usu=inv_usu, num_comp=num_comp)
            else:
                return redirect(url_for('inicio_principal'))

@app.route('/update_regulador', methods=['GET', 'POST'])
def update_regulador():  
    if request.method == 'POST':
        id_reg = request.form['id_reg']
        ref_reg = request.form['ref_reg']
        est_reg = request.form['est_reg']
        # Mapeo de cadenas a booleanos
        boolean_map = {'True': True, 'False': False}
        est_reg = boolean_map.get(est_reg, False) 
        pot_reg = float(request.form['pot_reg'])
        vol_reg = float(request.form['vol_reg'])
        cor_reg = float(request.form['cor_reg'])
        user_id = session.get('user_id')

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                
                # Si el regulador existe, actualizar los datos
                cur.execute('SELECT * FROM regulador WHERE id_reg = %s;', (id_reg,))
                regulador = cur.fetchone()

                if regulador:
                    
                    if est_reg == False:
                        cur.execute(''' UPDATE regulador SET deleted_at = %s WHERE id_reg = %s; ''', (datetime.now() , id_reg))
                        conn.commit()
                    if est_reg == True:
                        cur.execute(''' UPDATE regulador SET deleted_at = %s WHERE id_reg = %s; ''', (None, id_reg))
                        conn.commit()
                        
                    # Verificar la potencia máxima calculada
                    pot_cal_reg = vol_reg * cor_reg
                    if pot_cal_reg > pot_reg - 0.6 and pot_cal_reg < pot_reg + 0.6:
                        cur.execute('''
                            UPDATE regulador
                            SET ref_reg = %s, pot_reg = %s, vol_reg = %s, cor_reg = %s,
                                id_usu = %s,status=%s
                            WHERE id_reg = %s;
                        ''', (ref_reg,  pot_reg, vol_reg, cor_reg,user_id,est_reg, id_reg))
                        
                        conn.commit()
                        success = '1'
                        return redirect(url_for('update_regulador', success=success))
                    else:
                        error = '2'
                        return redirect(url_for('update_regulador', error=error))
      
    success = request.args.get('success')
    error = request.args.get('error')
    user_id = session.get('user_id')
    num_comp=4
    if user_id is None:
        return redirect(url_for('inicio_sesion'))

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Obtener más información del usuario
            cur.execute('SELECT * FROM usuario WHERE id_usu = %s;', (user_id,))
            user = cur.fetchone()

            if user and user[4] == 'Administrador':
                # Obtener todos los reguladores
                cur.execute('SELECT * FROM regulador;')
                reg_usu = cur.fetchall()
                
                return render_template('creacion_de_componentes/index.html', error=error, success=success, user_comp=user, reg_usu=reg_usu, num_comp=num_comp)
            else:
                return redirect(url_for('inicio_principal'))

################################################################################################################################################
#--------------------------------------------CREAR PROYECTO FOTOVOLTAICO-------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################

#mostrar modal proyecto
@app.route('/ver_modal_proyecto')
def ver_modal_proyecto():   
    return render_template('creacion_de_proyecto/crea_proyecto.html')

#Crear Proyecto
@app.route('/add_proyecto', methods=['POST'])
def add_proyecto():
    nom_pro = request.form['nom_pro']
    cred_pro = request.form['cred_pro']
    user_id = session.get('user_id')

    # Conectar a la base de datos y buscar si el proyecto ya existe
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id_pro FROM proyecto_fotovoltaica WHERE nom_pro = %s AND id_usu = %s AND status = %s;', (nom_pro, user_id, True))
            proyecto = cur.fetchone()

            # Verificar si el proyecto ya existe
            if proyecto is not None:
                return 'exist'
            else:
                # Insertar el nuevo proyecto en la base de datos
                cur.execute('INSERT INTO proyecto_fotovoltaica (nom_pro, cred_pro,  id_usu) VALUES (%s, %s,  %s) RETURNING id_pro;', 
                            (nom_pro, cred_pro,  user_id))

                # Guardar los cambios y obtener el id_pro del nuevo proyecto
                id_pro = cur.fetchone()[0]
                conn.commit()

                return jsonify({'id_pro': id_pro})
            
#Cambiar el estado del proyecto cuando no existe algun componente
def estado_proyecto(proyecto_completo, cant_componentes):
    for proyecto in proyecto_completo:
        if (proyecto[20] != 0.0 and cant_componentes[4] != 0 and cant_componentes[5] != 0 and ((proyecto[32] == 'No' and proyecto[35] is not None) or proyecto[32] == 'Si') and proyecto[45] != 0.0 and proyecto[62] != 0.0 and proyecto[45] is not None and proyecto[62] is not None ):
            eje_pro=None
            break
        else:
            # Obtener detalles del proyecto
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Actualiza el estado de 'eje_pro' para el proyecto específico
                    cur.execute('''UPDATE proyecto_fotovoltaica 
                                    SET eje_pro = %s 
                                    WHERE id_pro = %s;''', (False, proyecto[0]))
                    
                    # Commit para guardar los cambios en la base de datos
                    conn.commit()
            eje_pro=False
    return eje_pro

#Iniciar Proyecto
@app.route('/inicio_proyecto_fotovoltaica', methods=['GET', 'POST'])
def inicio_proyecto_fotovoltaica(): 
    global codigo_VCA_inversor_fotovoltaica
    
    num_info = request.args.get('num_info') 
    eje_arg = request.args.get('eje') 

    if eje_arg == 'True':
        ejecutar = True
    elif eje_arg == 'False':
        ejecutar = False
    else:
        ejecutar = None

    id_pro = request.args.get('id_pro')
    user_id = session.get('user_id')
    if user_id is None:
        # Si el usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
        return redirect(url_for('inicio_sesion')) 
    
    # Obtener detalles del proyecto
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            result_proyect_ene=[]
            if num_info == '4':
                start_date = end_date = None

                if request.method == 'POST':                    
                    start_date = request.form.get('start_date')
                    end_date = request.form.get('end_date')
                    codigo = int(request.form.get('cod_sen'))
                    if start_date and end_date:
                        start_date = f"{start_date} 06:00:00"
                        end_date = f"{end_date} 19:00:00"
                # Solo actualizar si ejecutar no es None
                if ejecutar is False:
                    print("Entro")
                    cur.execute('''
                        UPDATE proyecto_fotovoltaica SET eje_pro = %s WHERE id_pro = %s;
                    ''', (ejecutar, id_pro))
                    conn.commit()
                    num_info = None
                
                elif ejecutar is True and codigo==codigo_VCA_inversor_fotovoltaica:
                    print(codigo,"==",codigo_VCA_inversor_fotovoltaica)
                    cur.execute('''
                        UPDATE proyecto_fotovoltaica SET eje_pro = %s WHERE id_pro = %s;
                    ''', (ejecutar, id_pro))
                    conn.commit()
                    
                if ejecutar is not None:
                    num_info = None
                elif ejecutar is None:
                    print("ENTRO none")
                    result_proyect_ene = mostrar_ejecucion_proyecto(id_pro, start_date, end_date)
                    
            
            # Hacemos una única consulta para obtener todos los datos relacionados
            cur.execute('''
                SELECT * FROM proyecto_fotovoltaica p
                LEFT JOIN inversor i ON i.id_inv = p.id_inv LEFT JOIN regulador r ON r.id_reg = p.id_reg LEFT JOIN arreglo_de_paneles ap ON ap.id_pro = p.id_pro
                LEFT JOIN banco_de_baterias bb ON bb.id_pro = p.id_pro WHERE p.id_pro = %s AND p.id_usu = %s AND p.status = true ORDER BY ap.id_arr, bb.id_ban;
            ''', (id_pro, user_id))
            proyecto_completo = cur.fetchall()

            # Evitamos duplicación en arreglos y bancos
            arreglo_visto = set()  # Conjunto para evitar duplicaciones de arreglos
            banco_visto = set()    # Conjunto para evitar duplicaciones de bancos

            arreglos_completos = []
            bancos_completos = []
            cargas_completas = []
            
            error_cap_inv = None
            error_inv_arr = None
            for arr in proyecto_completo:
                # Evitamos que los arreglos se dupliquen
                if arr[44] not in arreglo_visto:  # asumiendo que arr[44] es el ID del arreglo
                    print('id_arreglo', arr[44])
                    print('Arreglo Pot', arr[45])                    

                    cur.execute('SELECT * FROM paralelo_arreglo WHERE id_arr=%s ORDER BY id_parr DESC;', (arr[44],))
                    paralelo = cur.fetchall()

                    series_totales = []
                    for par in paralelo:
                        cur.execute('SELECT * FROM serie_arreglo WHERE id_parr=%s ORDER BY id_sarr DESC;', (par[0],))
                        serie = cur.fetchall()

                        paneles_totales = []
                        for ser in serie:
                            cur.execute('''
                                select p.*, ser.* from serie_arreglo ser LEFT JOIN panel p on ser.id_pan=p.id_pan
                                WHERE id_sarr=%s;
                            ''', (ser[0],))
                            panel = cur.fetchone()
                            paneles_totales.append(panel)

                        series_totales.append({
                            'paralelo': par,
                            'series': serie,
                            'paneles': paneles_totales
                        })

                    arreglos_completos.append({
                        'arreglo': arr,
                        'paralelos': paralelo,
                        'series_totales': series_totales
                    })
                    arreglo_visto.add(arr[44])  # Agregamos el arreglo al conjunto visto

                # Evitamos que los bancos se dupliquen
                if arr[59] not in banco_visto:  # asumiendo que arr[59] es el ID del banco
                    cur.execute('SELECT * FROM paralelo_banco WHERE id_ban=%s ORDER BY id_pban DESC;', (arr[59],))
                    paralelo = cur.fetchall()

                    series_totales = []
                    for par in paralelo:
                        cur.execute('SELECT * FROM serie_banco WHERE id_pban=%s ORDER BY id_sban DESC;', (par[0],))
                        serie = cur.fetchall()

                        baterias_totales = []
                        for ser in serie:
                            cur.execute('''
                                select b.*, ser.* from serie_banco ser LEFT JOIN bateria b on ser.id_bat=b.id_bat
                                WHERE id_sban=%s;
                            ''', (ser[0],))
                            bateria = cur.fetchone()
                            baterias_totales.append(bateria)

                        series_totales.append({
                            'paralelo': par,
                            'series': serie,
                            'baterias': baterias_totales
                        })

                    bancos_completos.append({
                        'banco': arr,
                        'paralelos': paralelo,
                        'series_totales': series_totales
                    })
                    banco_visto.add(arr[59])  # Agregamos el banco al conjunto visto
                    
                if arr[45] is not None and  arr[45] != 0.0:
                    ptot_arreglo = arr[45] * 1.2  # Multiplicamos por 1.2 para obtener el valor ajustado
                    if arr[20] is not None and ptot_arreglo > arr[20]:
                        error_cap_inv = f'Error: la capacidad del inversor no soporta algun arreglo que realizaste.'
                        error_inv_arr = f'{arr[45]} * 1.2 = {ptot_arreglo} Potencia del arreglo > {arr[20]} Potencia máxima por entrada del inversor' 
            
            # Evitamos que las cargas se dupliquen
            cur.execute('''select c.id_car,c.tip_car, pc.pot_pcar, pc.x_pcar, pc.y_pcar, pc.id_pcar from proyecto_fotovoltaica p 
                    left join proyecto_carga pc on p.id_pro=pc.id_pro
                    left join carga c on c.id_car= pc.id_car where p.id_pro=%s;''', (id_pro,))
            cargas_completas = cur.fetchall()
            
            # Obtenemos el proyecto principal
            cur.execute('SELECT * FROM proyecto_fotovoltaica WHERE id_pro = %s AND id_usu = %s AND status = true;', (id_pro, user_id))
            pro = cur.fetchone()

            cur.execute('''SELECT COUNT(id_inv) AS cant_inv, COUNT(id_reg) AS cant_reg,
                (SELECT COUNT(id_arr) FROM arreglo_de_paneles WHERE id_pro = %s) AS cant_arr,
                (SELECT COUNT(id_ban) FROM banco_de_baterias WHERE id_pro = %s) AS cant_ban,
				(SELECT COUNT(id_pcar) FROM proyecto_carga WHERE id_pro = %s) AS cant_car,
                (SELECT COUNT(id_pcar) FROM proyecto_carga WHERE pot_pcar!=0 and id_pro = %s) AS cant_pcar
                FROM proyecto_fotovoltaica 
                WHERE id_pro = %s;''', (id_pro,id_pro,id_pro,id_pro,id_pro,))
            cant_componentes = cur.fetchone()            
            # Verificamos si hay inversor
            if pro and  proyecto_completo[0][4] is not None :
                cant_arr_del = cant_componentes[2]  
                # Mientras haya arreglos por eliminar
                while cant_arr_del > proyecto_completo[0][19]:                    
                    # Si hay resultados, obtenemos el último registro
                    ultimo_registro = proyecto_completo[-1]  
                    if ultimo_registro[44] is not None:
                        print('entro ultimo arr')
                        # Ejecutamos la eliminación del arreglo de paneles
                        cur.execute('''
                        DELETE FROM serie_arreglo
                        WHERE id_parr IN (SELECT id_parr FROM paralelo_arreglo WHERE id_arr = %s);
                        DELETE FROM paralelo_arreglo
                        WHERE id_arr = %s;
                        DELETE FROM arreglo_de_paneles
                        WHERE id_arr = %s;
                        ''', (ultimo_registro[44],ultimo_registro[44],ultimo_registro[44],))
                        # Contamos la cantidad de arreglos de paneles restantes
                        cur.execute('SELECT COUNT(*) FROM arreglo_de_paneles WHERE id_pro = %s;', (id_pro,))
                        cant_arr = cur.fetchone()[0]

                        # Actualizamos la cantidad de arreglos que quedan por eliminar
                        cant_arr_del = cant_arr - proyecto_completo[0][19]  # Posición 18 del inversor 
                        # Redirigir después de la eliminación
                        return redirect(url_for('inicio_proyecto_fotovoltaica', id_pro=id_pro))       

                    else:
                        break                              
            eje_pro=estado_proyecto(proyecto_completo, cant_componentes)
            cur.execute('select eje_pro from proyecto_fotovoltaica where id_pro=%s',(id_pro,))
            eje_pro=cur.fetchone()[0]
            if pro:
                # Pasamos todo a la plantilla
                return render_template('creacion_de_proyecto/proyecto.html', num_info=num_info, pro=pro,cargas_completas=cargas_completas, bancos_completos=bancos_completos,  proyecto_completo=proyecto_completo, arreglos_completos=arreglos_completos, cant_componentes=cant_componentes,error_cap_inv=error_cap_inv,error_inv_arr=error_inv_arr,result_proyect_ene =result_proyect_ene,eje_pro=eje_pro,  zip=zip)
            else:
                return redirect(url_for('inicio_principal'))
################################################################################################################################################

#Modificar coordenadas de cada arreglo que muevo
@app.route('/update-coordinates', methods=['POST'])
def update_coordinates():
    data = request.get_json()
    # Recibir los datos del JSON
    id_arr = data.get('arr_id')  # ID del arreglo de paneles
    id_ban = data.get('ban_id')  # ID del banco de paneles
    id_pro = data.get('pro_id')  # ID del proyecto
    id_pcar = data.get('pcar_id')  # ID del proyecto
    x = data.get('x')            # Nueva coordenada X del arreglo de paneles
    y = data.get('y')            # Nueva coordenada Y del arreglo de paneles
    x_inv = data.get('x_inv')    # Nueva coordenada X del inversor
    y_inv = data.get('y_inv')    # Nueva coordenada Y del inversor
    x_reg = data.get('x_reg')    # Nueva coordenada X del regulador
    y_reg = data.get('y_reg')    # Nueva coordenada Y del regulador
    x_ban = data.get('x_ban')    # Nueva coordenada X del banco de baterias
    y_ban = data.get('y_ban')    # Nueva coordenada Y del banco de baterias
    x_pcar = data.get('x_pcar')    # Nueva coordenada X de la carga
    y_pcar = data.get('y_pcar')    # Nueva coordenada Y de la carga
    x_red = data.get('x_red')    # Nueva coordenada X de la red
    y_red = data.get('y_red')    # Nueva coordenada Y de la red
    print('regulador: ',x_reg,y_reg,'banco: ',id_ban,x_ban,y_ban,'carga: ',x_pcar,y_pcar,'red: ',x_red,y_red)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Validar que id_arr sea un valor válido antes de ejecutar la consulta
            if id_arr !='None':
                print('ENTRO1')
                cur.execute('''
                    UPDATE arreglo_de_paneles SET x_arr = %s, y_arr = %s WHERE id_arr = %s;
                ''', (x, y, id_arr))
                conn.commit()
            # Validar que id_pro sea un valor válido antes de ejecutar la consulta
            if id_pro !='None':
                print('ENTRO2')
                cur.execute('''
                    UPDATE proyecto_fotovoltaica SET xinv_pro = %s, yinv_pro = %s, xred_pro = %s, yred_pro = %s WHERE id_pro = %s;
                ''', (x_inv, y_inv,  x_red, y_red, id_pro))
                conn.commit()
                if x_reg is not None or y_reg is not None:
                    cur.execute('''
                        UPDATE proyecto_fotovoltaica SET xreg_pro = %s, yreg_pro = %s WHERE id_pro = %s;
                    ''', (x_reg, y_reg, id_pro))
                    conn.commit()
            # Validar que id_ban sea un valor válido antes de ejecutar la consulta
            if id_ban !='None':
                print('ENTRO3')
                cur.execute('''
                    UPDATE banco_de_baterias SET x_ban = %s, y_ban = %s WHERE id_ban = %s;
                ''', (x_ban, y_ban, id_ban))
                conn.commit()
            # Validar que id_car sea un valor válido antes de ejecutar la consulta
            if id_pcar !='None':
                print('ENTRO1')
                cur.execute('''
                    UPDATE proyecto_carga SET x_pcar = %s, y_pcar = %s WHERE id_pcar = %s;
                ''', (x_pcar, y_pcar, id_pcar))
                conn.commit()

    return jsonify(success=True)  # Respuesta de éxito

################################################################################################################################################

#mostrar modal para agregar el arreglo alproyecto
@app.route('/modal_arreglo_project')
def modal_arreglo_project(): 
    id_pro = request.args.get('id_pro')
    print(id_pro)
    # Obtener detalles del proyecto usando SQLAlchemy con la conexión abierta
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM proyecto_fotovoltaica WHERE id_pro = %s ;', (id_pro,))
            pro = cur.fetchone()  
    return render_template('creacion_de_proyecto/project_arreglo.html', pro = pro )

#agregar el arreglo alproyecto
@app.route('/add_arreglo_project', methods=['POST'])
def add_arreglo_project(): 
    id_pro = request.form['id_pro']
    num_ser = int(request.form['num_ser'])
    num_pan_ser = int(request.form['num_pan_ser']) 

    # Usando la conexión manual a la base de datos
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Insertar nuevo arreglo de paneles
            cur.execute('''
                INSERT INTO arreglo_de_paneles (id_pro, fil_arr, col_arr) 
                VALUES (%s, %s, %s) RETURNING id_arr;
            ''', (id_pro, num_ser, num_pan_ser))
            id_arr = cur.fetchone()[0]  # Obtener el ID del nuevo arreglo insertado
            
            paralelos_ids = []
            series_ids = []    
            
            # Insertar cada paralelo y serie
            for _ in range(num_ser):
                # Insertar en paralelo_arreglo
                cur.execute('''
                    INSERT INTO paralelo_arreglo (id_arr) 
                    VALUES (%s) RETURNING id_parr;
                ''', (id_arr,))
                id_parr = cur.fetchone()[0]  # Obtener el ID del paralelo recién insertado
                paralelos_ids.append(id_parr) 
                
                for _ in range(num_pan_ser):        
                    # Insertar en serie_arreglo
                    cur.execute('''
                        INSERT INTO serie_arreglo (id_parr) 
                        VALUES (%s) RETURNING id_sarr;
                    ''', (id_parr,))
                    id_sarr = cur.fetchone()[0]  # Obtener el ID de la serie recién insertada
                    series_ids.append(id_sarr) 
                    
            # Confirmar todas las transacciones
            conn.commit()

    return redirect(url_for('inicio_proyecto_fotovoltaica', id_pro=id_pro))

# Mostrar modal para llenar los series
@app.route('/modal_panel_serie')
def modal_panel_serie(): 
    id_sarr = request.args.get('id_sarr')
    print(id_sarr)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Obtener la información de la serie arreglo
            cur.execute('SELECT * FROM serie_arreglo WHERE id_sarr = %s;', (id_sarr,))
            sarr = cur.fetchone()
            # Obtener los paneles habilitados y su tecnología
            cur.execute('''
                SELECT p.*, tp.* FROM panel p JOIN tecnologia_panel tp ON p.id_tec = tp.id_tec
                WHERE p.status = %s;
            ''', (True,))
            pan = cur.fetchall()
            # Obtener información del panel actual en la serie
            cur.execute('''
                SELECT p.*, tp.*FROM serie_arreglo sa JOIN panel p ON sa.id_pan = p.id_pan JOIN tecnologia_panel tp ON p.id_tec = tp.id_tec
                WHERE sa.id_sarr = %s;''', (id_sarr,))
            info = cur.fetchone()

    # Renderizar la plantilla con los datos obtenidos
    return render_template('creacion_de_proyecto/serie_panel.html', sarr=sarr, pan=pan, info=info)

@app.route('/edit_panel', methods=['POST'])
def edit_panel():
    # Obtiene los valores enviados en el formulario POST
    id_sarr = request.form['id_sarr']
    print(id_sarr)
    id_pan = request.form['id_pan']

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Obtener la información de la serie arreglo
            cur.execute('SELECT id_parr FROM serie_arreglo WHERE id_sarr = %s;', (id_sarr,))
            id_parr = cur.fetchone()

            # Actualizar el valor de id_pan en el registro de SerieArreglo
            cur.execute('UPDATE serie_arreglo SET id_pan = %s WHERE id_sarr = %s;', (id_pan, id_sarr))
            conn.commit()

            # Realiza una consulta para obtener los resultados necesarios
            cur.execute('''
                SELECT 
                    SUM(p.vmp_pan) * MIN(p.imp_pan),
                    SUM(p.vmp_pan),
                    MIN(p.imp_pan),
                    SUM(p.are_pan),
                    AVG(p.efi_pan)
                FROM panel p
                JOIN serie_arreglo sa ON sa.id_pan = p.id_pan
                JOIN paralelo_arreglo pa ON pa.id_parr = sa.id_parr
                WHERE pa.id_parr = %s AND p.imp_pan != 0
                GROUP BY sa.id_parr, pa.id_arr;
            ''', (id_parr,))                      
            results = cur.fetchone()
            print(results)
            if results:
                pser, vser, iser, area, efis = results
                cur.execute('SELECT id_arr FROM paralelo_arreglo WHERE id_parr = %s;', (id_parr,))
                id_arr = cur.fetchone()  
                # Actualizar el registro de ParaleloArreglo
                cur.execute('''
                    UPDATE paralelo_arreglo 
                    SET pser_parr = %s, vser_parr = %s, iser_parr = %s, aser_parr = %s, efi_parr = %s 
                    WHERE id_parr = %s;
                ''', (pser, vser, iser, area, efis, id_parr))
                conn.commit()

                # Consultar el arreglo de paneles
                cur.execute('''
                    SELECT 
                        MIN(pa.vser_parr) * SUM(pa.iser_parr),
                        MIN(pa.vser_parr),
                        SUM(pa.iser_parr),
                        SUM(pa.aser_parr),
                        pa.id_arr,
                        AVG(pa.efi_parr)
                    FROM paralelo_arreglo pa
                    JOIN arreglo_de_paneles ap ON ap.id_arr = pa.id_arr
                    WHERE pa.id_arr = %s AND pa.vser_parr != 0
                    GROUP BY pa.id_arr;
                ''', (id_arr,))
                result_par = cur.fetchone()

                if result_par:
                    parr, vparr, iparr, area, id_arr, efip = result_par
                    
                    # Actualizar el registro de ArregloDePaneles
                    cur.execute('''
                        UPDATE arreglo_de_paneles 
                        SET ptot_arr = %s, vmax_arr = %s, imax_arr = %s, area_arr = %s, efi_arr = %s 
                        WHERE id_arr = %s;
                    ''', (parr, vparr, iparr, area, efip, id_arr))
                    conn.commit()
                return 'success'
    return 'success'

################################################################################################################################################

#mostrar modal para agregar el inversor alproyecto
@app.route('/modal_inversor_project')
def modal_inversor_project():    
    id_pro = request.args.get('id_pro')
    # Obtener detalles del proyecto usando SQLAlchemy con la conexión abierta
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select * from proyecto_fotovoltaica where id_pro= %s ;', (id_pro,))
            pro = cur.fetchone() 
            cur.execute('select * from arreglo_de_paneles where id_pro= %s ;', (id_pro,))
            arr = cur.fetchall() 
            cur.execute('select * from inversor where status= %s ;', (True,))
            inv = cur.fetchall() 
            cur.execute('select pro.*, inv.* from proyecto_fotovoltaica pro join inversor inv on pro.id_inv=inv.id_inv where pro.id_pro= %s ;', (id_pro,))
            info = cur.fetchone()          
            
    return render_template('creacion_de_proyecto/project_inversor.html', pro = pro, arr=arr , inv = inv, info=info)

#agregar el inversor alproyecto
@app.route('/add_inversor_project', methods=['POST'])
def add_inversor_project():     
    id_pro = request.form['id_pro']
    id_inv = request.form['id_inv']
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                    UPDATE proyecto_fotovoltaica 
                    SET id_inv = %s 
                    WHERE id_pro = %s;
                ''', (id_inv, id_pro))
            conn.commit()
            cur.execute('select inv.reg_inv from proyecto_fotovoltaica pro join inversor inv on pro.id_inv=inv.id_inv where pro.id_pro= %s ;', (id_pro,))
            reg_inv = cur.fetchone() 
            print(reg_inv[0])
            if reg_inv[0] == 'Si' :
                cur.execute('''
                    UPDATE proyecto_fotovoltaica 
                    SET id_reg = %s, id_inv = %s 
                    WHERE id_pro = %s;
                ''', (None, id_inv, id_pro))
                conn.commit()
            
    return redirect(url_for('inicio_proyecto_fotovoltaica', id_pro=id_pro))

################################################################################################################################################
#mostrar modal para agregar cargas alproyecto
@app.route('/modal_carga_project')
def modal_carga_project(): 
    id_pro = request.args.get('id_pro')
    cargas = []  # Inicializar lista vacía para almacenar los tipos de carga
    
    # Obtener detalles del proyecto y las cargas asociadas
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT c.tip_car FROM proyecto_fotovoltaica p JOIN proyecto_carga pc ON p.id_pro = pc.id_pro
                JOIN carga c ON c.id_car = pc.id_car WHERE p.id_pro = %s;
            ''', (id_pro,))
            
            # Iterar sobre los resultados y agregar los tipos de carga a la lista 'cargas'
            for row in cur.fetchall():
                cargas.append(row[0])  # row[0] contiene el valor de tipo_carga
                
    return render_template('creacion_de_proyecto/project_carga.html', cargas=cargas, id_pro=id_pro)

# Agregar la carga al proyecto
@app.route('/add_carga_project', methods=['POST'])
def add_carga_project():     
    id_pro = request.form['id_pro']
    cargas = {
        'Lineal': request.form.get('car_lineal'),
        'Inductiva': request.form.get('car_inductiva'),
        'No Lineal': request.form.get('car_no_lineal')
    }

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Obtener todos los tipos de carga disponibles y mapear a un diccionario
            cur.execute('SELECT id_car, tip_car FROM carga;')
            cargas_dict = {c[1]: c[0] for c in cur.fetchall()}

            # Iterar sobre cada tipo de carga (Lineal, Inductiva, No Lineal)
            for tipo, valor in cargas.items():
                id_car = cargas_dict.get(tipo)
                if valor:  # Si la carga está marcada
                    cur.execute('''
                        INSERT INTO proyecto_carga (id_car, id_pro)
                        SELECT %s, %s WHERE NOT EXISTS (
                            SELECT 1 FROM proyecto_carga WHERE id_car = %s AND id_pro = %s
                        );
                    ''', (id_car, id_pro, id_car, id_pro))
                else:  # Si la carga no está marcada, eliminar
                    cur.execute('DELETE FROM proyecto_carga WHERE id_car = %s AND id_pro = %s;', (id_car, id_pro))

            conn.commit()

    return redirect(url_for('inicio_proyecto_fotovoltaica', id_pro=id_pro))

################################################################################################################################################

#mostrar modal para agregar el regulador alproyecto
@app.route('/modal_regulador_project')
def modal_regulador_project():    
    id_pro = request.args.get('id_pro')
    # Obtener detalles del proyecto usando SQLAlchemy con la conexión abierta
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select * from proyecto_fotovoltaica where id_pro= %s ;', (id_pro,))
            pro = cur.fetchone() 
            cur.execute('select * from arreglo_de_paneles where id_pro= %s ;', (id_pro,))
            arr = cur.fetchall() 
            cur.execute('select * from regulador where status= %s ;', (True,))
            reg = cur.fetchall() 
            cur.execute('select pro.*, reg.* from proyecto_fotovoltaica pro join regulador reg on pro.id_reg=reg.id_reg where pro.id_pro= %s ;', (id_pro,))
            info = cur.fetchone() 
    return render_template('creacion_de_proyecto/project_regulador.html', pro = pro, arr=arr , reg = reg, info=info)

#agregar el regulador alproyecto
@app.route('/add_regulador_project', methods=['POST'])
def add_regulador_project():     
    id_pro = request.form['id_pro']
    id_reg = request.form['id_reg']
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                UPDATE proyecto_fotovoltaica 
                SET id_reg = %s 
                WHERE id_pro = %s;
            ''', (id_reg, id_pro))
            conn.commit()
    return redirect(url_for('inicio_proyecto_fotovoltaica', id_pro=id_pro))

################################################################################################################################################

#mostrar modal para agregar el banco alproyecto
@app.route('/modal_banco_project')
def modal_banco_project(): 
    id_pro = request.args.get('id_pro')
    print(id_pro)
    # Obtener detalles del proyecto usando SQLAlchemy con la conexión abierta
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM proyecto_fotovoltaica WHERE id_pro = %s ;', (id_pro,))
            pro = cur.fetchone()  
    return render_template('creacion_de_proyecto/project_banco.html', pro = pro )

#agregar el banco alproyecto
@app.route('/add_banco_project', methods=['POST'])
def add_banco_project(): 
    id_pro = request.form['id_pro']
    num_ser = int(request.form['num_ser'])
    num_bat_ser = int(request.form['num_bat_ser']) 

    # Usando la conexión manual a la base de datos
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Insertar nuevo banco de baterias
            cur.execute('''
                INSERT INTO banco_de_baterias (id_pro, fil_ban, col_ban) 
                VALUES (%s, %s, %s) RETURNING id_ban;
            ''', (id_pro, num_ser, num_bat_ser))
            id_ban = cur.fetchone()[0]  # Obtener el ID del nuevo banco insertado
            
            paralelos_ids = []
            series_ids = []    
            
            # Insertar cada paralelo y serie
            for _ in range(num_ser):
                # Insertar en paralelo_banco
                cur.execute('''
                    INSERT INTO paralelo_banco (id_ban) 
                    VALUES (%s) RETURNING id_pban;
                ''', (id_ban,))
                id_pban = cur.fetchone()[0]  # Obtener el ID del paralelo recién insertado
                paralelos_ids.append(id_pban) 
                
                for _ in range(num_bat_ser):        
                    # Insertar en serie_banco
                    cur.execute('''
                        INSERT INTO serie_banco (id_pban) 
                        VALUES (%s) RETURNING id_sban;
                    ''', (id_pban,))
                    id_sban = cur.fetchone()[0]  # Obtener el ID de la serie recién insertada
                    series_ids.append(id_sban) 
                    
            # Confirmar todas las transacciones
            conn.commit()

    return redirect(url_for('inicio_proyecto_fotovoltaica', id_pro=id_pro))

# Mostrar modal para llenar los series bancos
@app.route('/modal_bateria_serie')
def modal_bateria_serie(): 
    id_sban = request.args.get('id_sban')
    print(id_sban)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Obtener la información de la serie banco
            cur.execute('SELECT * FROM serie_banco WHERE id_sban = %s;', (id_sban,))
            sban = cur.fetchone()
            # Obtener los bateria habilitados y su tecnología
            cur.execute('''
                SELECT * FROM bateria WHERE status = %s;
            ''', (True,))
            bat = cur.fetchall()
            # Obtener información del bateria actual en la serie
            cur.execute('''
                SELECT b.* FROM serie_banco sb JOIN bateria b ON sb.id_bat = b.id_bat WHERE sb.id_sban = %s;''', (id_sban,))
            info = cur.fetchone()

    # Renderizar la plantilla con los datos obtenidos
    return render_template('creacion_de_proyecto/serie_bateria.html', sban=sban, bat=bat, info=info)

@app.route('/edit_bateria', methods=['POST'])
def edit_bateria():
    # Obtiene los valores enviados en el formulario POST
    id_sban = request.form['id_sban']
    id_bat = request.form['id_bat']
    
    # Usando la conexión explícita a la base de datos
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Actualiza el valor de id_bat en el registro de SerieBanco con el id_sban dado
            cur.execute('UPDATE serie_banco SET id_bat = %s WHERE id_sban = %s;', (id_bat, id_sban))
            
            # Obtener id_pban de la serie
            cur.execute('SELECT id_pban FROM serie_banco WHERE id_sban = %s;', (id_sban,))
            id_pban = cur.fetchone()[0]  # fetchone devuelve una tupla, obtenemos el primer valor
            
            # Obtener id_ban del paralelo
            cur.execute('SELECT id_ban FROM paralelo_banco WHERE id_pban = %s;', (id_pban,))
            id_ban = cur.fetchone()[0]
            
            # Consulta para el total de los paralelos
            cur.execute('''
                SELECT SUM(b.vol_bat), AVG(b.cap_bat), SUM(b.vol_bat) * AVG(b.cap_bat)
                FROM bateria b
                JOIN serie_banco s ON s.id_bat = b.id_bat
                JOIN paralelo_banco p ON p.id_pban = s.id_pban
                WHERE p.id_pban = %s AND b.cap_bat != 0
                GROUP BY s.id_pban, p.id_ban;
            ''', (id_pban,))
            results = cur.fetchone()

            if results:
                vser = results[0]  # Primer valor calculado
                cser = results[1]  # Segundo valor calculado
                eser = results[2]  # Tercer valor calculado
                
                # Actualizar los valores en paralelo_banco
                cur.execute('''
                    UPDATE paralelo_banco
                    SET vser_pban = %s, cser_pban = %s, eser_pban = %s
                    WHERE id_pban = %s;
                ''', (vser, cser, eser, id_pban))
                
                # Consulta para el total del banco
                cur.execute('''
                    SELECT MIN(p.vser_pban), SUM(p.cser_pban),
                           MIN(p.vser_pban) * SUM(p.cser_pban), p.id_ban
                    FROM paralelo_banco p
                    JOIN banco_de_baterias b ON b.id_ban = p.id_ban
                    WHERE p.id_ban = %s AND p.vser_pban != 0
                    GROUP BY p.id_ban;
                ''', (id_ban,))
                result_par = cur.fetchone()

                if result_par:
                    vpban = result_par[0]  # Tensión mínima
                    cpban = result_par[1]  # Capacidad total
                    epban = result_par[2]  # Energía total
                    id_ban = result_par[3]  # id del banco de baterías

                    # Actualizar los valores en banco_de_baterias
                    cur.execute('''
                        UPDATE banco_de_baterias
                        SET vol_ban = %s, cap_ban = %s, ene_ban = %s
                        WHERE id_ban = %s;
                    ''', (vpban, cpban, epban, id_ban))
                    
                    conn.commit()  # Confirmar todas las transacciones

                    return 'success'

    return 'success'

################################################################################################################################################
#--------------------------------------------EDITAR PROYECTO FOTOVOLTAICO-------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################

#Lista de proyectos fotovoltaicos creados
@app.route('/list_project')
def list_project():
    buscar = request.args.get('buscar')
    success = request.args.get('success')
    error = request.args.get('error')
    user_id = session.get('user_id')
    if user_id is None:
        # Si el usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
        return redirect(url_for('inicio_sesion')) 

    # Obtener información del usuario
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM usuario WHERE id_usu = %s;', (user_id,))
            user = cur.fetchone()

            # Consulta SQL base para proyectos
            sql_query = '''
                SELECT p.id_pro, p.nom_pro, p.id_inv, p.created_at, AVG(ap.ptot_arr) AS arr, AVG(bb.ene_ban) AS ban
                FROM proyecto_fotovoltaica p
                LEFT JOIN arreglo_de_paneles ap ON p.id_pro = ap.id_pro
                LEFT JOIN banco_de_baterias bb ON bb.id_pro = p.id_pro
                WHERE p.id_usu = %s AND p.status = true 
            '''
            params = [user_id]

            # Modificar consulta si hay búsqueda
            if buscar:
                sql_query += " AND p.nom_pro ILIKE %s"
                params.append(f"%{buscar}%")

            sql_query += '''
                GROUP BY p.id_pro
                ORDER BY p.created_at DESC;
            '''

            # Ejecutar la consulta con o sin filtro de búsqueda
            cur.execute(sql_query, tuple(params))
            pro_list = cur.fetchall()
            print(pro_list)
            
    # Renderizar la plantilla con los resultados y notificaciones si existen
    return render_template(
        'creacion_de_proyecto/list_project.html' if not buscar else 'creacion_de_proyecto/search_project.html',
        user=user, pro_list=pro_list, success=success, error=error
    )
    
#Eliminar un proyecto
@app.route('/delete_project')
def delete_project():
    id_pro = request.args.get('id_pro')
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Ejecutar la consulta para actualizar el estado del proyecto a "false"
            cur.execute('''
                UPDATE proyecto_fotovoltaica SET status = false WHERE id_pro = %s
            ''', (id_pro,))
            
            # Confirmar los cambios en la base de datos
            conn.commit()
    
    # Redirigir de vuelta a la lista de proyectos
    return redirect(url_for('list_project'))

#Eliminar arreglo
@app.route('/ver_modal_del_arr')
def ver_modal_del_arr():
    id_arr = request.args.get('id_arr')
    id_pro = request.args.get('id_pro')
    id_del_arr = request.args.get('id_arr_del')
    if id_del_arr is not None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:            
                # Ejecutamos la eliminación del arreglo de paneles
                cur.execute('''
                DELETE FROM serie_arreglo
                WHERE id_parr IN (SELECT id_parr FROM paralelo_arreglo WHERE id_arr = %s);
                DELETE FROM paralelo_arreglo
                WHERE id_arr = %s;
                DELETE FROM arreglo_de_paneles
                WHERE id_arr = %s;
                ''', (id_del_arr,id_del_arr,id_del_arr,))
                
                conn.commit()
        
        # Redirigir al inicio del proyecto
        return redirect(url_for('inicio_proyecto_fotovoltaica', id_pro=id_pro))
    
    else:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Obtener los detalles del arreglo
                cur.execute('SELECT * FROM arreglo_de_paneles WHERE id_arr = %s;', (id_arr,))
                arr = cur.fetchone()
        
        # Renderizar la plantilla para mostrar el modal de eliminación
        return render_template('creacion_de_proyecto/delete_arreglo_project.html', arr=arr)

#Eliminar banco
@app.route('/ver_modal_del_ban')
def ver_modal_del_ban():
    id_ban = request.args.get('id_ban')
    id_pro = request.args.get('id_pro')
    id_del_ban = request.args.get('id_ban_del')
    if id_del_ban is not None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:            
                # Ejecutamos la eliminación del banco de paneles
                cur.execute('''
                DELETE FROM serie_banco
                WHERE id_pban IN (SELECT id_pban FROM paralelo_banco WHERE id_ban = %s);
                DELETE FROM paralelo_banco
                WHERE id_ban = %s;
                DELETE FROM banco_de_baterias
                WHERE id_ban = %s;
                ''', (id_del_ban,id_del_ban,id_del_ban,))
                
                conn.commit()
        
        # Redirigir al inicio del proyecto
        return redirect(url_for('inicio_proyecto_fotovoltaica', id_pro=id_pro))
    
    else:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Obtener los detalles del banco
                cur.execute('SELECT * FROM banco_de_baterias WHERE id_ban = %s;', (id_ban,))
                ban = cur.fetchone()
        
        # Renderizar la plantilla para mostrar el modal de eliminación
        return render_template('creacion_de_proyecto/delete_banco_project.html', ban=ban)

#Eliminar inversor
@app.route('/ver_modal_del_inv')
def ver_modal_del_inv():
    from app import get_db_connection
    id_pro = request.args.get('id_pro')
    id_inv_del = request.args.get('id_inv_del')
    if id_inv_del is not None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:            
                # Ejecutamos la eliminación del inversor del proyecto
                cur.execute('''
                    UPDATE proyecto_fotovoltaica SET id_inv = %s, xinv_pro=%s, yinv_pro=%s, id_reg = %s, xreg_pro=%s, yreg_pro=%s  WHERE id_pro = %s;
                ''', (None, 319, 116, None, 494, 340, id_pro,))
                conn.commit()
        
        # Redirigir al inicio del proyecto
        return redirect(url_for('inicio_proyecto_fotovoltaica', id_pro=id_pro))
    
    else:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Obtener los detalles del inversor que se esta usando en el proyecto
                cur.execute('SELECT id_inv,id_pro FROM proyecto_fotovoltaica WHERE id_pro = %s;', (id_pro,))
                inv = cur.fetchone()
        
        # Renderizar la plantilla para mostrar el modal de eliminación
        return render_template('creacion_de_proyecto/delete_inversor_project.html', inv=inv)

#Modal para agregar potencia a la carga
@app.route('/modal_carga_pot', methods=['GET', 'POST'])
def modal_carga_pot():
    if request.method == 'POST':
        # Si es una solicitud POST, significa que se está enviando el formulario para actualizar la potencia
        id_pcar = request.form['id_pcar']
        pot_pcar = request.form['pot_pcar']
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Actualizar el valor de la potencia de la carga
                cur.execute('UPDATE proyecto_carga SET pot_pcar = %s WHERE id_pcar = %s;', (pot_pcar, id_pcar))
                # Obtener el id_pro relacionado con la carga
                cur.execute('SELECT id_pro FROM proyecto_carga WHERE id_pcar = %s;', (id_pcar,))
                id_pro = cur.fetchone()[0]  # Obtener el id_pro de la carga
        
        return redirect(url_for('inicio_proyecto_fotovoltaica', id_pro=id_pro))
    
    else:
        # Si es una solicitud GET, significa que se está mostrando el modal
        id_pcar = request.args.get('id_pcar')
        print(id_pcar)
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Obtener los detalles de la carga con el id_pcar dado
                cur.execute('SELECT pc.id_pcar, pc.pot_pcar, c.tip_car FROM proyecto_carga pc LEFT JOIN carga c ON pc.id_car = c.id_car WHERE id_pcar = %s;', (id_pcar,))
                pcar = cur.fetchone()  # Obtener el resultado de la consulta
        
        return render_template('creacion_de_proyecto/pot_car.html', pcar=pcar)
    
################################################################################################################################################
#--------------------------------------------EJECUTAR PROYECTO FOTOVOLTAICO-------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################

def ejecutar_proyecto():
    global voltaje_VCA_inversor_fotovoltaica 
    if voltaje_VCA_inversor_fotovoltaica == 0:
        voltaje_VCA_inversor_fotovoltaica=121.11
        
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''SELECT sum(a.ptot_arr) as tot_arr, avg(a.efi_arr) as tot_efi, a.id_pro, sum(a.area_arr) as tot_area  
                        FROM arreglo_de_paneles a 
                        JOIN proyecto_fotovoltaica p ON a.id_pro = p.id_pro 
                        WHERE p.eje_pro = %s
                        GROUP BY a.id_pro;''', (True,))
            w_tot_rows = cur.fetchall()  # Obtener todas las filas
            cur.execute('''SELECT id_irr, prom_irr, created_at FROM dato_irradiancia ORDER BY created_at desc limit 3;''')
            #cur.execute('SELECT id_irr, prom_irr, created_at FROM dato_irradiancia WHERE created_at::date = CURRENT_DATE ORDER BY created_at;')
            irr = cur.fetchall()
            
            for w_tot in w_tot_rows:
                # Acceder a los valores individuales dentro de la tupla w_tot
                tot_arr = w_tot[0]       
                id_pro = w_tot[2]
                Area_pro = w_tot[3]
                
                for row in irr:
                    prom_irr = row[1]
                    id_irr = row[0]
                    created_at = row[2]
                    resultadoW = tot_arr * (prom_irr / 1000)  # Potencia ajustada a la irradiancia real en Wh
                    resultadokwh = (resultadoW / 1000)  # Potencia ajustada a la irradiancia real en kwh
                    if prom_irr==0:
                        tot_efi=0                        
                    else:   
                        tot_efi =(resultadoW/(Area_pro*prom_irr))*100
                    
                    cur.executemany("""
                        INSERT INTO energia_arreglo (id_pro, parr_ene, id_irr, efi_ene, w_ene, kw_ene, created_at, vinv_ene)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id_pro, created_at) DO NOTHING
                    """, [(id_pro, tot_arr, id_irr, tot_efi, resultadoW, resultadokwh, created_at, voltaje_VCA_inversor_fotovoltaica)])
                    conn.commit() 

                    voltaje_VCA_inversor_fotovoltaica=round(voltaje_VCA_inversor_fotovoltaica-0.1,2)

#mostrar modal para establecer conexion sesores fotovoltaica
@app.route('/modal_conexion_sensor')
def modal_conexion_sensor():    
    from app import get_db_connection
    id_pro = request.args.get('id_pro')
    num_info = request.args.get('num_info')
    eje = request.args.get('eje')
    # Obtener detalles del proyecto usando SQLAlchemy con la conexión abierta
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select * from proyecto_fotovoltaica where id_pro= %s ;', (id_pro,))
            pro = cur.fetchone() 
    return render_template('creacion_de_proyecto/conexion_sensor_fotovoltaica.html', pro = pro, num_info=num_info,eje=eje)
            
#Mostrar datos de proyecto generacion de energia
def mostrar_ejecucion_proyecto(id_pro,start_date,end_date):
    print(start_date,'-',end_date)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if start_date is None and end_date is None:
                cur.execute('''SELECT e.id_pro, e.parr_ene, irr.prom_irr, e.efi_ene, e.w_ene, e.kw_ene, e.created_at, p.eje_pro, e.vinv_ene   FROM energia_arreglo e join dato_irradiancia irr on e.id_irr=irr.id_irr join proyecto_fotovoltaica p on e.id_pro=p.id_pro where e.id_pro=%s ORDER BY e.created_at desc limit 257;''', (id_pro,))
            else:
                cur.execute('SELECT e.id_pro, e.parr_ene, irr.prom_irr, e.efi_ene, e.w_ene, e.kw_ene, e.created_at, p.eje_pro, e.vinv_ene  FROM energia_arreglo e join dato_irradiancia irr on e.id_irr=irr.id_irr join proyecto_fotovoltaica p on e.id_pro=p.id_pro   WHERE (e.created_at >= %s and e.created_at <= %s) and e.id_pro=%s ORDER BY e.created_at desc;', (start_date, end_date, id_pro,))
            result_proyect_ene = cur.fetchall()# Obtener el id_pro de la carga

            return result_proyect_ene


# Ruta para obtener los últimos datos del proyecto en formato JSON
@app.route('/get_latest_proyecto_data/<int:id_pro>', methods=['GET'])
def get_latest_proyecto_data(id_pro):
    with get_db_connection() as conn:  
        with conn.cursor() as cur:  
            # Ejecuta la consulta usando id_pro como parámetro
            cur.execute('''
                SELECT e.id_pro, e.parr_ene, irr.prom_irr, e.efi_ene, e.w_ene, e.kw_ene, e.vinv_ene, e.created_at  
                FROM energia_arreglo e 
                JOIN dato_irradiancia irr ON e.id_irr = irr.id_irr 
                WHERE e.id_pro = %s 
                ORDER BY e.created_at DESC 
                LIMIT 1
            ''', (id_pro,))
            db_irr = cur.fetchall()  # Obtiene todos los resultados de la consulta

    # Estructura los datos en una lista de diccionarios con formato ajustado
    data = [{
        'parr_ene': f"{float(row[1]):.3f}",
        'prom_irr': f"{float(row[2]):.1f}",
        'efi_ene': f"{float(row[3]):.3f}",
        'w_ene': f"{float(row[4]):.3f}",
        'kw_ene': f"{float(row[5]):.3f}",
        'vinv_ene': f"{float(row[6]):.3f}",
        'created_at': row[7].strftime('%Y-%m-%d %H:%M:%S')
    } for row in db_irr]
    
    return jsonify(data)  # Devuelve los datos en formato JSON


###### CONEXION SENSORES ########
@app.route('/api/voltaje', methods=['POST'])
def recibir_voltaje():
    global voltaje_VCA_inversor_fotovoltaica, codigo_VCA_inversor_fotovoltaica

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibió JSON'}), 400

    dispositivo = data.get("dispositivo")

    if dispositivo == "fotovoltaica":
        if 'voltaje' in data and 'codigo' in data:
            with lock:
                voltaje_VCA_inversor_fotovoltaica = data['voltaje']
                codigo_VCA_inversor_fotovoltaica = data['codigo']
                print(f"⚡ Fotovoltaica -> V: {data['voltaje']} V | Código: {data['codigo']}")
                ejecutar_proyecto()

            return jsonify({'message': 'Datos recibidos correctamente'}), 200
        else:
            return jsonify({'error': 'Datos incompletos de fotovoltaica'}), 400

    elif dispositivo == "hidrica":
        print("ENTRA 1")
        success = procesar_datos_hidrica(data)
        if success:
            return jsonify({'message': 'Datos recibidos correctamente'}), 200
        else:
            return jsonify({'error': 'Datos incompletos de hidráulica'}), 400

    return jsonify({'error': 'Dispositivo desconocido'}), 400



    
# API para obtener voltaje actual
@app.route('/api/voltaje_actual', methods=['GET'])
def get_voltaje_actual():
    with lock:
        return jsonify({'voltaje': voltaje_VCA_inversor_fotovoltaica})
    
################################################################################################################################################
#---------------------------------------------------------INFORMES------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################
@app.route('/informes',methods=['GET', 'POST'])
def informes():
    user_id = session.get('user_id')
    user_rol = session.get('user_rol')
    
    if user_id is None:
        # Si el usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
        return redirect(url_for('inicio_sesion'))
    start_date,end_date=None,None     
    # Suponiendo que tienes una función para obtener la conexión a la base de datos
    if user_rol=='Administrador':
        with get_db_connection() as conn:  
            with conn.cursor() as cur:  
                # Ejecuta la consulta 
                cur.execute('''
                    select p.created_at, p.nom_pro, avg(e.w_ene)as w_ene, avg(e.efi_ene)as efi_ene, p.eje_pro
                    from energia_arreglo e join proyecto_fotovoltaica p
                    on e.id_pro=p.id_pro group by p.created_at, p.nom_pro, p.eje_pro order by p.created_at desc limit 30;
                ''')
                sist_optima = cur.fetchall()  # Obtiene todos los resultados de la consulta
                if request.method == 'POST':
                    start_date = request.form['start_date']
                    end_date = request.form['end_date'] 
                    start_date = f"{start_date} 00:00:00"  # Agrega hora 06:00:00 a la fecha de inicio
                    end_date = f"{end_date} 23:59:59"
                    print('DAMOS INFORMES',start_date,'-',end_date)
                    # Ejecuta la consulta 
                    cur.execute('''
                        SELECT p.id_pro, p.created_at,  p.nom_pro, 
                        (SELECT COUNT(id_inv) FROM inversor WHERE id_inv = p.id_inv) AS cant_inv,
                        (SELECT COUNT(id_reg) FROM regulador WHERE id_reg = p.id_reg) AS cant_reg,
                        (SELECT COUNT(id_arr) FROM arreglo_de_paneles WHERE id_pro = p.id_pro) AS cant_arr,
                        (SELECT COUNT(id_ban) FROM banco_de_baterias WHERE id_pro = p.id_pro) AS cant_ban,
                        (SELECT COUNT(id_pcar) FROM proyecto_carga WHERE id_pro = p.id_pro and pot_pcar!=0) AS cant_pcar,
                        avg(e.w_ene), p.status
                        FROM proyecto_fotovoltaica p LEFT JOIN energia_arreglo e on e.id_pro=p.id_pro
                        WHERE p.created_at >= %s AND p.created_at <= %s
                        GROUP BY p.id_pro, p.created_at, p.nom_pro order by created_at desc;
                    ''', (start_date, end_date,))
                else:
                    print('DAMOS INFORMES',start_date,'-',end_date)
                    # Ejecuta la consulta 
                    cur.execute('''
                        SELECT p.id_pro, p.created_at,  p.nom_pro, 
                        (SELECT COUNT(id_inv) FROM inversor WHERE id_inv = p.id_inv) AS cant_inv,
                        (SELECT COUNT(id_reg) FROM regulador WHERE id_reg = p.id_reg) AS cant_reg,
                        (SELECT COUNT(id_arr) FROM arreglo_de_paneles WHERE id_pro = p.id_pro) AS cant_arr,
                        (SELECT COUNT(id_ban) FROM banco_de_baterias WHERE id_pro = p.id_pro) AS cant_ban,
                        (SELECT COUNT(id_pcar) FROM proyecto_carga WHERE id_pro = p.id_pro and pot_pcar!=0) AS cant_pcar,
                        avg(e.w_ene), p.status
                        FROM proyecto_fotovoltaica p 
                        LEFT JOIN energia_arreglo e on e.id_pro=p.id_pro
                        GROUP BY p.id_pro, p.created_at, p.nom_pro order by created_at desc limit 30;
                    ''')
                estructuras = cur.fetchall()  # Obtiene todos los resultados de la consulta
        return render_template('informe_y_Estadistica/informes.html',sist_optima=sist_optima,estructuras=estructuras)
    else:
        return redirect(url_for('inicio_principal'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)