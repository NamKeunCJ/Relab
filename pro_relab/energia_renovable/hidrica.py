import psycopg2
import hashlib
from datetime import datetime, timedelta
import threading
import time
import requests # elementos para datos davis
# hidrica.py
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
import math

# Crear un Blueprint para las rutas hídricas
hidrica_bp = Blueprint('hidrica', __name__, static_folder='static',template_folder='templates')

# Variables compartidas
voltaje_VDC_hidrica = 0.0
codigo_VDC_hidrica = 0.0
caudal_hidrica = 0.0
presion_hidrica = 0.0
corriente_hidrica = 0.0
fechahora_dato=0.0

# Lock para acceso concurrente
lock = threading.Lock()

################################################################################################################################################
#--------------------------------------------CREAR COMPONENTES Y EDITARLOS-------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################

@hidrica_bp.route('/update_motobomba', methods=['GET', 'POST'])
def update_motobomba():
    from app import get_db_connection
    if request.method == 'POST':
        id_mot = request.form['id_mot']
        ref_mot = request.form['ref_mot']
        est_mot = request.form['est_mot']
        # Mapeo de cadenas a booleanos
        boolean_map = {'True': True, 'False': False}
        est_mot = boolean_map.get(est_mot, False) 
        pot_mot = float(request.form['pot_mot'])
        vol_mot = float(request.form['vol_mot'])
        cau_mot = float(request.form['cau_mot'])
        fre_mot = float(request.form['fre_mot'])
        pre_mot = float(request.form['pre_mot'])
        dent_mot = float(request.form['dent_mot']) 
        dsal_mot = float(request.form['dsal_mot'])
        user_id = session.get('user_id')

        # Usar get_db_connection() para obtener la conexión
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM motobomba WHERE id_mot = %s;', (id_mot,))
                motobomba = cur.fetchone()

                if motobomba:
                    if est_mot == False:
                        cur.execute('UPDATE motobomba SET deleted_at = %s WHERE id_mot = %s;', (datetime.now(), id_mot))
                    else:
                        cur.execute('UPDATE motobomba SET deleted_at = %s WHERE id_mot = %s;', (None, id_mot))
                    
                    conn.commit()
                    
                    # Verificar potencia
                    cur.execute('''
                        UPDATE motobomba
                        SET ref_mot = %s, pot_mot = %s, vol_mot = %s, cau_mot = %s,
                            id_usu = %s, status = %s, fre_mot = %s, pre_mot = %s, dent_mot = %s, dsal_mot = %s
                        WHERE id_mot = %s;
                    ''', (ref_mot, pot_mot, vol_mot, cau_mot, user_id, est_mot, fre_mot, pre_mot, dent_mot, dsal_mot, id_mot))
                    conn.commit()
                    success = '1'
                    return redirect(url_for('hidrica.update_motobomba', success=success))  # Redirige con success
        
    success = request.args.get('success')
    error = request.args.get('error')
    user_id = session.get('user_id')
    user_rol = session.get('user_rol')
    num_comp = 5

    if user_id is None:
        return redirect(url_for('inicio_sesion'))

    if user_rol == 'Administrador':
        # Obtener todos los motobombas
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM motobomba;')
                mot_usu = cur.fetchall()
        
        return render_template('creacion_de_componentes/index.html', error=error, success=success, mot_usu=mot_usu, num_comp=num_comp)
    else:
        return redirect(url_for('inicio_principal'))

#mostrar modal motobomba
@hidrica_bp.route('/ver_modal_motobomba')
def ver_modal_motobomba():
    return render_template('creacion_de_componentes/crea_motobomba.html')

# Crear motobomba modal
@hidrica_bp.route('/add_motobomba', methods=['POST'])
def add_motobomba():
    from app import get_db_connection
    ref_mot = request.form['ref_mot']
    vol_mot = float(request.form['vol_mot'])
    cau_mot = float(request.form['cau_mot'])
    pot_mot = float(request.form['pot_mot'])  
    fre_mot = float(request.form['fre_mot'])
    pre_mot = float(request.form['pre_mot'])
    dent_mot = float(request.form['dent_mot']) 
    dsal_mot = float(request.form['dsal_mot'])
    idu_mot = request.form['idu_mot']
    user_id = session.get('user_id')
    
    # Conectar a la base de datos y buscar si el motobomba ya existe
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Buscar el motobomba en la base de datos
            cur.execute('SELECT * FROM motobomba WHERE idu_mot = %s AND status = %s;', (idu_mot, True))
            motobomba = cur.fetchone()

            # Verificar si los datos ya existen en la base de datos
            if motobomba is not None:
                return 'exist'
            
            # Insertar el nuevo motobomba
            cur.execute('''
            INSERT INTO motobomba (ref_mot, idu_mot, vol_mot, cau_mot, pot_mot, fre_mot, pre_mot, dent_mot, dsal_mot,id_usu)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            ''', (ref_mot, idu_mot, vol_mot, cau_mot, pot_mot, fre_mot, pre_mot, dent_mot, dsal_mot, user_id))
            conn.commit()  # Confirmar la inserción
            
            return 'success'


@hidrica_bp.route('/update_generador', methods=['GET', 'POST'])
def update_generador():
    from app import get_db_connection
    if request.method == 'POST':
        id_gen = request.form['id_gen']
        ref_gen = request.form['ref_gen']
        est_gen = request.form['est_gen']
        # Mapeo de cadenas a booleanos
        boolean_map = {'True': True, 'False': False}
        est_gen = boolean_map.get(est_gen, False) 
        pot_gen = float(request.form['pot_gen'])
        vol_gen = float(request.form['vol_gen'])
        vel_gen = float(request.form['vel_gen'])
        dia_gen = float(request.form['dia_gen'])
        user_id = session.get('user_id')

        # Usar get_db_connection() para obtener la conexión
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM generador WHERE id_gen = %s;', (id_gen,))
                generador = cur.fetchone()

                if generador:
                    if est_gen == False:
                        cur.execute('UPDATE generador SET deleted_at = %s WHERE id_gen = %s;', (datetime.now(), id_gen))
                    else:
                        cur.execute('UPDATE generador SET deleted_at = %s WHERE id_gen = %s;', (None, id_gen))
                    
                    conn.commit()
                    
                    # Verificar potencia
                    cur.execute('''
                        UPDATE generador
                        SET ref_gen = %s, pot_gen = %s, vol_gen = %s, vel_gen = %s,
                            id_usu = %s, status = %s, dia_gen = %s
                        WHERE id_gen = %s;
                    ''', (ref_gen, pot_gen, vol_gen, vel_gen, user_id, est_gen, dia_gen, id_gen))
                    conn.commit()
                    success = '1'
                    return redirect(url_for('hidrica.update_generador', success=success))  # Redirige con success
        
    success = request.args.get('success')
    error = request.args.get('error')
    user_id = session.get('user_id')
    user_rol = session.get('user_rol')
    num_comp = 6

    if user_id is None:
        return redirect(url_for('inicio_sesion'))

    if user_rol == 'Administrador':
        # Obtener todos los generadores
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM generador;')
                gen_usu = cur.fetchall()
        
        return render_template('creacion_de_componentes/index.html', error=error, success=success, gen_usu=gen_usu, num_comp=num_comp)
    else:
        return redirect(url_for('inicio_principal'))


#mostrar modal generador
@hidrica_bp.route('/ver_modal_generador')
def ver_modal_generador():
    return render_template('creacion_de_componentes/crea_generador.html')

# Crear generador modal
@hidrica_bp.route('/add_generador', methods=['POST'])
def add_generador():
    from app import get_db_connection
    ref_gen = request.form['ref_gen']
    vol_gen = float(request.form['vol_gen'])
    vel_gen = float(request.form['vel_gen'])
    pot_gen = float(request.form['pot_gen']) 
    dia_gen = float(request.form['dia_gen']) 
    idu_gen = request.form['idu_gen']
    user_id = session.get('user_id')
    
    # Conectar a la base de datos y buscar si el generador ya existe
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Buscar el generador en la base de datos
            cur.execute('SELECT * FROM generador WHERE idu_gen = %s AND status = %s;', (idu_gen, True))
            generador = cur.fetchone()

            # Verificar si los datos ya existen en la base de datos
            if generador is not None:
                return 'exist'
            
            # Insertar el nuevo generador
            cur.execute('''
            INSERT INTO generador (ref_gen, idu_gen, vol_gen, vel_gen, pot_gen, dia_gen, id_usu)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            ''', (ref_gen, idu_gen, vol_gen, vel_gen, pot_gen, dia_gen, user_id))
            conn.commit()  # Confirmar la inserción
            
            return 'success'

################################################################################################################################################
#--------------------------------------------CREAR PROYECTO HIDRICO-------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################

#mostrar modal proyecto
@hidrica_bp.route('/ver_modal_proyecto_h')
def ver_modal_proyecto_h():   
    return render_template('creacion_de_proyecto/crea_proyecto_hidrico.html')

#Crear Proyecto
@hidrica_bp.route('/add_proyecto_h', methods=['POST'])
def add_proyecto_h():
    from app import get_db_connection
    nom_pro = request.form['nom_pro_h']
    user_id = session.get('user_id')

    # Conectar a la base de datos y buscar si el proyecto ya existe
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id_pro FROM proyecto_hidrica WHERE nom_pro = %s AND id_usu = %s AND status = %s;', (nom_pro, user_id, True))
            proyecto = cur.fetchone()

            # Verificar si el proyecto ya existe
            if proyecto is not None:
                return 'exist'
            else:
                # Insertar el nuevo proyecto en la base de datos
                cur.execute('INSERT INTO proyecto_hidrica (nom_pro, id_usu) VALUES (%s, %s) RETURNING id_pro;', 
                            (nom_pro, user_id))

                # Guardar los cambios y obtener el id_pro del nuevo proyecto
                id_pro = cur.fetchone()[0]

                # Insertar el el tanque predeterminado para el proyecto en la base de datos
                cur.execute('INSERT INTO tanque (id_pro) VALUES (%s);', (id_pro,))
                # Insertar el el generador predeterminado para el proyecto en la base de datos
                cur.execute('INSERT INTO proyecto_generador (id_pro) VALUES (%s);', (id_pro,))
                # Insertar el el turbina predeterminado para el proyecto en la base de datos
                cur.execute('INSERT INTO proyecto_turbina (id_pro) VALUES (%s);', (id_pro,))
                # Insertar el el turbina predeterminado para el proyecto en la base de datos
                cur.execute('INSERT INTO trayectoria_tubo (id_pro) VALUES (%s);', (id_pro,))
                conn.commit()
                
                return jsonify({'id_pro': id_pro})

#Cambiar el estado del proyecto cuando no existe algun componente
def estado_proyecto_hidrica(proyecto,carga_completa):
    from app import get_db_connection
    if (proyecto[3] is not None and proyecto[32] is not None and proyecto[64] is not None and proyecto[72] != 0 and carga_completa[0][7] != 0 and len(list(filter(lambda x: x[8] != 0, carga_completa))) > 0 and proyecto[47] != 0):
        eje_pro=None
    else:
        # Obtener detalles del proyecto
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Actualiza el estado de 'eje_pro' para el proyecto específico
                cur.execute('''UPDATE proyecto_hidrica 
                                SET eje_pro = %s 
                                WHERE id_pro = %s;''', (False, proyecto[0]))
                
                # Commit para guardar los cambios en la base de datos
                conn.commit()
        eje_pro=False
    return eje_pro

#Iniciar Proyecto
@hidrica_bp.route('/inicio_proyecto_hidrica', methods=['GET', 'POST'])
def inicio_proyecto_hidrica(): 
    from app import get_db_connection
    global codigo_VDC_hidrica

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
            if num_info=='4':
                start_date,end_date=None,None
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
                        UPDATE proyecto_hidrica SET eje_pro = %s WHERE id_pro = %s;
                    ''', (ejecutar, id_pro))
                    conn.commit()
                    num_info = None
                
                elif ejecutar is True and codigo==codigo_VDC_hidrica:
                    print(codigo,"==",codigo_VDC_hidrica)
                    cur.execute('''
                        UPDATE proyecto_hidrica SET eje_pro = %s WHERE id_pro = %s;
                    ''', (ejecutar, id_pro))
                    conn.commit()
                    
                if ejecutar is not None:
                    num_info = None
                elif ejecutar is None:
                    print("ENTRO none")
                    result_proyect_ene = mostrar_ejecucion_proyecto_hidrica(id_pro, start_date, end_date)
                    
            # Obtenemos el proyecto principal
            cur.execute('''SELECT 
                pro.*, mot.*, gen_pro.*,gen.*, tan.*, tur_pro.*,tur.*,tra.alt_tra, COUNT(tub.id_tub) AS count_tubos
                FROM 
                    proyecto_hidrica pro
                LEFT JOIN motobomba mot on pro.id_mot=mot.id_mot 
                LEFT JOIN proyecto_generador gen_pro ON pro.id_pro = gen_pro.id_pro
                LEFT JOIN generador gen ON gen_pro.id_gen = gen.id_gen
                LEFT JOIN tanque tan ON pro.id_pro = tan.id_pro
                LEFT JOIN proyecto_turbina tur_pro ON pro.id_pro = tur_pro.id_pro
                LEFT JOIN turbina tur ON tur_pro.id_tur = tur.id_tur
				LEFT JOIN trayectoria_tubo tra ON tra.id_pro = pro.id_pro
                LEFT JOIN tubo tub ON tub.id_pro = pro.id_pro
                WHERE 
                pro.id_pro = %s
                GROUP BY 
                pro.id_pro, mot.id_mot, gen_pro.id_pgen, gen.id_gen,tan.id_tan, tur_pro.id_ptur, tur.id_tur, tra.alt_tra;
            ''', (id_pro,))  # La coma final es necesaria para formar una tupla
            pro_com = cur.fetchone()
            # Obtenemos el proyecto principal en cuestion de cargas
            cur.execute('''SELECT 
                pro_car.id_pcar, car.*,(SELECT COUNT(id_pcar) FROM proyecto_cargah WHERE id_pro = %s) AS cant_car, pro_car.pot_pcar AS cant_pcar, pro_car.x_pcar, pro_car.y_pcar  
                FROM 
                    proyecto_hidrica pro
                LEFT JOIN proyecto_cargah pro_car ON pro.id_pro = pro_car.id_pro
                LEFT JOIN carga car ON pro_car.id_car = car.id_car
                WHERE 
                pro.id_pro = %s ;
            ''', (id_pro,id_pro,))  # La coma final es necesaria para formar una tupla
            car_com = cur.fetchall()
            # Obtenemos el proyecto principal en cuestion de las tuberias
            cur.execute('''SELECT 
                    tub.lon_tub, tub.ori_tub, cod.ang_cod, tra.dia_tra, g.cau_ene,
                    count(*) OVER () AS total_tubos,
                    row_number() OVER (ORDER BY tub.created_at) AS fila
                FROM tubo tub
                JOIN codo cod ON cod.id_cod = tub.id_cod
                LEFT JOIN (SELECT id_pro, dia_tra FROM trayectoria_tubo WHERE id_pro = %s LIMIT 1) tra ON tub.id_pro = tra.id_pro
                LEFT JOIN (SELECT id_pro, cau_ene FROM energia_generada WHERE id_pro = %s ORDER BY created_at DESC LIMIT 1) g ON tub.id_pro = g.id_pro
                WHERE tub.id_pro = %s
                ORDER BY tub.created_at;
            ''', (id_pro,id_pro,id_pro,))  # La coma final es necesaria para formar una tupla
            tub_com = cur.fetchall()
            # Obtenemos el proyecto principal
            cur.execute('SELECT * FROM proyecto_hidrica WHERE id_pro = %s AND id_usu = %s AND status = true;', (id_pro, user_id))
            pro_h = cur.fetchone()
            eje_pro=estado_proyecto_hidrica(pro_com,car_com)
            cur.execute('select eje_pro from proyecto_hidrica where id_pro=%s;',(id_pro,))
            eje_pro=cur.fetchone()[0]
            if pro_h:
                # Pasamos todo a la plantilla
                return render_template('creacion_de_proyecto/proyecto_hidrico.html', result_proyect_ene=result_proyect_ene, pro_com=pro_com, car_com=car_com, tub_com=tub_com, num_info=num_info, pro_h=pro_h, eje_pro=eje_pro, cos=math.cos, sin=math.sin, pi=math.pi)
            else:
                return redirect(url_for('inicio_principal'))


################################################################################################################################################
#mostrar modal para agregar el motobomba alproyecto
@hidrica_bp.route('/modal_motobomba_project')
def modal_motobomba_project():    
    from app import get_db_connection
    id_pro = request.args.get('id_pro')
    # Obtener detalles del proyecto usando SQLAlchemy con la conexión abierta
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select * from proyecto_hidrica where id_pro= %s ;', (id_pro,))
            pro = cur.fetchone() 
            cur.execute('select * from motobomba where status= %s ;', (True,))
            mot = cur.fetchall() 
            cur.execute('select pro.*, mot.* from proyecto_hidrica pro join motobomba mot on pro.id_mot=mot.id_mot where pro.id_pro= %s ;', (id_pro,))
            info = cur.fetchone() 
    return render_template('creacion_de_proyecto/project_motobomba.html', pro = pro, mot = mot, info=info)

#agregar el motobomba alproyecto
@hidrica_bp.route('/add_motobomba_project', methods=['POST'])
def add_motobomba_project():     
    from app import get_db_connection
    id_pro = request.form['id_pro']
    id_mot = request.form['id_mot']
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                UPDATE proyecto_hidrica
                SET id_mot = %s 
                WHERE id_pro = %s;
            ''', (id_mot, id_pro))
            conn.commit()
    return redirect(url_for('hidrica.inicio_proyecto_hidrica', id_pro=id_pro))

################################################################################################################################################
#mostrar modal para agregar el tanque alproyecto
@hidrica_bp.route('/modal_tanque_project')
def modal_tanque_project():    
    from app import get_db_connection
    id_pro = request.args.get('id_pro')
    # Obtener detalles del proyecto usando SQLAlchemy con la conexión abierta
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select * from proyecto_hidrica where id_pro= %s ;', (id_pro,))
            pro = cur.fetchone() 
            cur.execute('select pro.id_pro, tan.cap_tan from proyecto_hidrica pro left join tanque tan on pro.id_pro=tan.id_pro where pro.id_pro= %s ;', (id_pro,))
            info = cur.fetchone() 
    return render_template('creacion_de_proyecto/project_tanque.html', pro = pro, info=info)

#agregar el tanque alproyecto
@hidrica_bp.route('/add_tanque_project', methods=['POST'])
def add_tanque_project():     
    from app import get_db_connection
    id_pro = request.form['id_pro']
    cap_tan = request.form['cap_tan']
    print(cap_tan)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                UPDATE tanque
                SET cap_tan = %s 
                WHERE id_pro = %s;
            ''', (cap_tan, id_pro))
            conn.commit()
    return redirect(url_for('hidrica.inicio_proyecto_hidrica', id_pro=id_pro))

################################################################################################################################################
#mostrar modal para agregar el generador alproyecto
@hidrica_bp.route('/modal_generador_project')
def modal_generador_project():    
    from app import get_db_connection
    id_pro = request.args.get('id_pro')
    # Obtener detalles del proyecto usando SQLAlchemy con la conexión abierta
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select * from proyecto_hidrica where id_pro= %s ;', (id_pro,))
            pro = cur.fetchone() 
            cur.execute('select * from generador where status= %s ;', (True,))
            gen = cur.fetchall() 
            cur.execute('''select pro.*, gen.*, pgen.* from proyecto_hidrica pro 
                join proyecto_generador pgen on pro.id_pro=pgen.id_pro 
                join generador gen on gen.id_gen=pgen.id_gen
                where pro.id_pro= %s ;''', (id_pro,))
            info = cur.fetchone() 
            print(info)
    return render_template('creacion_de_proyecto/project_generador.html', pro = pro, gen = gen, info=info)

#agregar el generador alproyecto
@hidrica_bp.route('/add_generador_project', methods=['POST'])
def add_generador_project():     
    from app import get_db_connection
    id_pro = request.form['id_pro']
    id_gen = request.form['id_gen']
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select vel_gen from generador where id_gen= %s ;', (id_gen,))
            vel_ptur = cur.fetchone() 
            cur.execute(''' UPDATE proyecto_turbina SET vel_ptur=%s WHERE id_pro = %s; ''', (vel_ptur, id_pro))
            conn.commit()
            cur.execute(''' UPDATE proyecto_generador SET id_gen = %s WHERE id_pro = %s; ''', (id_gen, id_pro))
            conn.commit()
    return redirect(url_for('hidrica.inicio_proyecto_hidrica', id_pro=id_pro))

################################################################################################################################################
#mostrar modal para agregar el turbina al proyecto
@hidrica_bp.route('/modal_turbina_project')
def modal_turbina_project():    
    from app import get_db_connection
    id_pro = request.args.get('id_pro')
    # Obtener detalles del proyecto usando SQLAlchemy con la conexión abierta
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select * from proyecto_hidrica where id_pro= %s ;', (id_pro,))
            pro = cur.fetchone() 
            cur.execute('select * from turbina where status= %s ;', (True,))
            tur = cur.fetchall() 
            cur.execute('''select pro.*, tur.*, ptur.* from proyecto_hidrica pro 
                join proyecto_turbina ptur on pro.id_pro=ptur.id_pro 
                join turbina tur on tur.id_tur=ptur.id_tur
                where pro.id_pro= %s ;''', (id_pro,))
            info = cur.fetchone() 
            print(info)
    return render_template('creacion_de_proyecto/project_turbina.html', pro = pro, tur = tur, info=info)

#agregar el turbina alproyecto
@hidrica_bp.route('/add_turbina_project', methods=['POST'])
def add_turbina_project():     
    from app import get_db_connection
    id_pro = request.form['id_pro']
    id_tur = request.form['id_tur']
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(''' UPDATE proyecto_turbina SET id_tur = %s WHERE id_pro = %s; ''', (id_tur, id_pro))
            conn.commit()
    return redirect(url_for('hidrica.inicio_proyecto_hidrica', id_pro=id_pro))

################################################################################################################################################
#mostrar modal para agregar el turbina_alabes alproyecto
@hidrica_bp.route('/modal_turbina_alabes_project')
def modal_turbina_alabes_project():    
    from app import get_db_connection
    id_pro = request.args.get('id_pro')
    # Obtener detalles del proyecto usando SQLAlchemy con la conexión abierta
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select * from proyecto_hidrica where id_pro= %s ;', (id_pro,))
            pro = cur.fetchone() 
            cur.execute('''select pro.id_pro, ptur.cant_ptur, ptur.vel_ptur,tur.tip_tur , tur.cuc_tur 
                        from proyecto_hidrica pro left 
                        join proyecto_turbina ptur on pro.id_pro=ptur.id_pro 
                        join turbina tur on tur.id_tur=ptur.id_tur where pro.id_pro= %s ;''', (id_pro,))
            info = cur.fetchone() 
    return render_template('creacion_de_proyecto/project_turbina_alabes.html', pro = pro, info=info)

#agregar el turbina_alabes alproyecto
@hidrica_bp.route('/add_turbina_alabes_project', methods=['POST'])
def add_turbina_alabes_project():     
    from app import get_db_connection
    id_pro = request.form['id_pro']
    cant_ptur = request.form['cant_ptur']
    vel_ptur = request.form['vel_ptur']
    print(cant_ptur)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                UPDATE proyecto_turbina
                SET cant_ptur = %s, vel_ptur = %s
                WHERE id_pro = %s;
            ''', (cant_ptur, vel_ptur, id_pro))
            conn.commit()
    return redirect(url_for('hidrica.inicio_proyecto_hidrica', id_pro=id_pro))

################################################################################################################################################
#mostrar modal para agregar el caudalimetro alproyecto
@hidrica_bp.route('/modal_caudalimetro_project')
def modal_caudalimetro_project():    
    from app import get_db_connection
    id_pro = request.args.get('id_pro')
    # Obtener detalles del proyecto usando SQLAlchemy con la conexión abierta
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select * from proyecto_hidrica where id_pro= %s ;', (id_pro,))
            pro = cur.fetchone() 
            cur.execute('select pro.id_pro, pgen.cau_pgen from proyecto_hidrica pro left join proyecto_generador pgen on pro.id_pro=pgen.id_pro where pro.id_pro= %s ;', (id_pro,))
            info = cur.fetchone() 
    return render_template('creacion_de_proyecto/project_caudalimetro.html', pro = pro, info=info)

################################################################################################################################################
#mostrar modal para agregar cargas alproyecto
@hidrica_bp.route('/modal_carga_project')
def modal_carga_project(): 
    from app import get_db_connection
    id_pro = request.args.get('id_pro')
    cargas = []  # Inicializar lista vacía para almacenar los tipos de carga
    
    # Obtener detalles del proyecto y las cargas asociadas
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT c.tip_car FROM proyecto_hidrica p JOIN proyecto_cargah pc ON p.id_pro = pc.id_pro
                JOIN carga c ON c.id_car = pc.id_car WHERE p.id_pro = %s;
            ''', (id_pro,))
            
            # Iterar sobre los resultados y agregar los tipos de carga a la lista 'cargas'
            for row in cur.fetchall():
                cargas.append(row[0])  # row[0] contiene el valor de tipo_carga
                
    return render_template('creacion_de_proyecto/project_carga_hidrico.html', cargas=cargas, id_pro=id_pro)

# Agregar la carga al proyecto
@hidrica_bp.route('/add_carga_project_hidrica', methods=['POST'])
def add_carga_project_hidrica():     
    from app import get_db_connection
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
                        INSERT INTO proyecto_cargah (id_car, id_pro)
                        SELECT %s, %s WHERE NOT EXISTS (
                            SELECT 1 FROM proyecto_cargah WHERE id_car = %s AND id_pro = %s
                        );
                    ''', (id_car, id_pro, id_car, id_pro))
                else:  # Si la carga no está marcada, eliminar
                    cur.execute('DELETE FROM proyecto_cargah WHERE id_car = %s AND id_pro = %s;', (id_car, id_pro))
                print(id_car, id_pro, id_car, id_pro)
            conn.commit()

    return redirect(url_for('hidrica.inicio_proyecto_hidrica', id_pro=id_pro))

#Modal para agregar potencia a la carga
@hidrica_bp.route('/modal_carga_pot_hidrica', methods=['GET', 'POST'])
def modal_carga_pot_hidrica():
    from app import get_db_connection
    if request.method == 'POST':
        # Si es una solicitud POST, significa que se está enviando el formulario para actualizar la potencia
        id_pcar = request.form['id_pcar_h']
        pot_pcar = request.form['pot_pcar_h']
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Actualizar el valor de la potencia de la carga
                cur.execute('UPDATE proyecto_cargah SET pot_pcar = %s WHERE id_pcar = %s;', (pot_pcar, id_pcar))
                # Obtener el id_pro relacionado con la carga
                cur.execute('SELECT id_pro FROM proyecto_cargah WHERE id_pcar = %s;', (id_pcar,))
                id_pro = cur.fetchone()[0]  # Obtener el id_pro de la carga
                
        return redirect(url_for('hidrica.inicio_proyecto_hidrica', id_pro=id_pro))
    
    else:
        # Si es una solicitud GET, significa que se está mostrando el modal
        id_pcar = request.args.get('id_pcar')
        print(id_pcar)
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Obtener los detalles de la carga con el id_pcar dado
                cur.execute('SELECT pc.id_pcar, pc.pot_pcar, c.tip_car FROM proyecto_cargah pc LEFT JOIN carga c ON pc.id_car = c.id_car WHERE id_pcar = %s;', (id_pcar,))
                pcar = cur.fetchone()  # Obtener el resultado de la consulta
        
        return render_template('creacion_de_proyecto/pot_car_hidrico.html', pcar=pcar)

################################################################################################################################################
#mostrar modal para agregar la tuberia al proyecto
@hidrica_bp.route('/modal_tuberia_project')
def modal_tuberia_project():    
    from app import get_db_connection
    id_pro = request.args.get('id_pro')
    # Obtener detalles del proyecto usando SQLAlchemy con la conexión abierta
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select pro.id_pro, tra.dia_tra from proyecto_hidrica pro join trayectoria_tubo tra on pro.id_pro=tra.id_pro where pro.id_pro= %s ; ', (id_pro,))
            pro = cur.fetchone() 
            cur.execute('select * from codo where status= %s ;', (True,))
            cod = cur.fetchall() 
    return render_template('creacion_de_proyecto/project_tuberia.html', pro = pro, cod = cod)

#agregar la tuberia alproyecto
@hidrica_bp.route('/add_tuberia_project', methods=['POST'])
def add_tuberia_project():     
    from app import get_db_connection
    import math
    
    id_pro = request.form['id_pro']
    dia_tra = request.form['dia_tra']
    lon_tub = request.form['lon_tub']
    id_cod = request.form['ang_cod']
    ori_tub = request.form.get('ori_tub', 'No Aplica')

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Insertar nueva tubería
            cur.execute('''
                INSERT INTO tubo (id_pro, lon_tub, id_cod, ori_tub)
                VALUES (%s, %s, %s, %s)
            ''', (id_pro, lon_tub, id_cod, ori_tub))
            conn.commit()

            # Obtener datos para el cálculo de la altura
            cur.execute('''
                SELECT tub.lon_tub, cod.ang_cod, tub.ori_tub
                FROM proyecto_hidrica pro
                JOIN trayectoria_tubo tra ON pro.id_pro = tra.id_pro
                JOIN tubo tub ON pro.id_pro = tub.id_pro 
                JOIN codo cod ON cod.id_cod = tub.id_cod
                WHERE pro.id_pro = %s
                ORDER BY tub.created_at ASC;
            ''', (id_pro,))
            
            tub_com = cur.fetchall()
            
            alt_tra = sum(
                l * math.sin(math.radians(0 if a == "No Aplica" else float(a))) * (-1 if o == 'Derecha' else 1)
                for l, a, o in tub_com
            )

            if alt_tra<0:
                alt_tra = -(alt_tra)

            
            # Actualizar la trayectoria del tubo con la nueva altura
            cur.execute('''
                UPDATE trayectoria_tubo SET dia_tra = %s, alt_tra = %s WHERE id_pro = %s;
            ''', (dia_tra, alt_tra, id_pro))
            conn.commit()

    return redirect(url_for('hidrica.inicio_proyecto_hidrica', id_pro=id_pro))
################################################################################################################################################

#Modificar coordenadas de cada arreglo que muevo
@hidrica_bp.route('/update_coordinates_hidrica', methods=['POST'])
def update_coordinates_hidrica():
    from app import get_db_connection
    data = request.get_json()
    # Recibir los datos del JSON  
    id_pro = data.get('pro_id')  # ID del proyecto  
    id_pcar = data.get('pcar_id')  # ID del proyecto
    x_mot = data.get('x_mot')    # Nueva coordenada X de la motobomba
    y_mot = data.get('y_mot')    # Nueva coordenada Y de la motobomba
    x_tan = data.get('x_tan')    # Nueva coordenada X de la motobomba
    y_tan = data.get('y_tan')    # Nueva coordenada Y de la motobomba
    x_pcar = data.get('x_pcar')    # Nueva coordenada X de la carga
    y_pcar = data.get('y_pcar')    # Nueva coordenada Y de la carga
    print('carga: ',x_pcar,y_pcar)
    print('motobomba: ',x_mot,y_mot)
    print('tanque: ',x_tan,y_tan)
    with get_db_connection() as conn:
        with conn.cursor() as cur:            
            # Validar que id_car sea un valor válido antes de ejecutar la consulta
            if id_pcar !='None':
                cur.execute('''
                    UPDATE proyecto_cargah SET x_pcar = %s, y_pcar = %s WHERE id_pcar = %s;
                ''', (x_pcar, y_pcar, id_pcar))
                conn.commit()
            # Validar que id_pro sea un valor válido antes de ejecutar la consulta
            if id_pro !='None':
                cur.execute('''
                    UPDATE proyecto_hidrica SET x_mot = %s, y_mot = %s WHERE id_pro = %s;
                ''', (x_mot, y_mot, id_pro))
                conn.commit()
                cur.execute('''
                    UPDATE tanque SET x_tan = %s, y_tan = %s WHERE id_pro = %s;
                ''', (x_tan, y_tan, id_pro))
                conn.commit()

    return jsonify(success=True)  # Respuesta de éxito

################################################################################################################################################
#--------------------------------------------EDITAR PROYECTO HIDRICO-------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################

#Lista de proyectos hidricos creados
@hidrica_bp.route('/list_project_hidrica')
def list_project_hidrica():
    from app import get_db_connection
    buscar = request.args.get('buscar_h')
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
                SELECT pro.id_pro, pro.nom_pro, pro.created_at, mot.*, gen_pro.*,gen.*, tan.*, tur_pro.*,tur.*
                FROM 
                    proyecto_hidrica pro
                LEFT JOIN motobomba mot on pro.id_mot=mot.id_mot 
                LEFT JOIN proyecto_generador gen_pro ON pro.id_pro = gen_pro.id_pro
                LEFT JOIN generador gen ON gen_pro.id_gen = gen.id_gen
                LEFT JOIN tanque tan ON pro.id_pro = tan.id_pro
                LEFT JOIN proyecto_turbina tur_pro ON pro.id_pro = tur_pro.id_pro
                LEFT JOIN turbina tur ON tur_pro.id_tur = tur.id_tur
                WHERE 
                pro.id_usu = %s AND pro.status = true  
            '''
            params = [user_id]

            # Modificar consulta si hay búsqueda
            if buscar:
                sql_query += " AND pro.nom_pro ILIKE %s"
                params.append(f'%{buscar}%')
            sql_query += '''
                GROUP BY pro.id_pro, mot.id_mot,gen_pro.id_pgen, gen.id_gen, tan.id_tan, tur_pro.id_ptur,tur.id_tur 
                ORDER BY pro.created_at DESC;
            '''

            # Ejecutar la consulta con o sin filtro de búsqueda
            cur.execute(sql_query, tuple(params))
            pro_list = cur.fetchall()
            print(pro_list)
            
    # Renderizar la plantilla con los resultados y notificaciones si existen
    return render_template(
        'creacion_de_proyecto/list_project_hidrico.html' if not buscar else 'creacion_de_proyecto/search_project_hidrico.html',
        user=user, pro_list=pro_list, success=success, error=error
    )


#Eliminar generador
@hidrica_bp.route('/ver_modal_del_gen')
def ver_modal_del_gen():
    from app import get_db_connection
    id_pgen = request.args.get('id_pgen')
    id_pro = request.args.get('id_pro')
    id_pgen_del = request.args.get('id_pgen_del')
    if id_pgen_del is not None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:            
                # Ejecutamos la eliminación del generador del proyecto
                cur.execute('''
                    UPDATE proyecto_generador SET id_gen = %s, cau_pgen = %s, deleted_at = CURRENT_TIMESTAMP  WHERE id_pro = %s;
                ''', (None, 0, id_pro))
                cur.execute('''
                    UPDATE proyecto_turbina SET id_tur = %s, cant_ptur = %s, vel_ptur=%s, deleted_at = CURRENT_TIMESTAMP  WHERE id_pro = %s;
                ''', (None, 6, 0, id_pro))
                conn.commit()
        
        # Redirigir al inicio del proyecto
        return redirect(url_for('hidrica.inicio_proyecto_hidrica', id_pro=id_pro))
    
    else:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Obtener los detalles del generador que se esta usando en el proyecto
                cur.execute('SELECT id_pgen,id_pro FROM proyecto_generador WHERE id_pgen = %s;', (id_pgen,))
                pgen = cur.fetchone()
        
        # Renderizar la plantilla para mostrar el modal de eliminación
        return render_template('creacion_de_proyecto/delete_generador_project.html', pgen=pgen)
################################################################################################################################################

#Eliminar tanque
@hidrica_bp.route('/ver_modal_del_tan')
def ver_modal_del_tan():
    from app import get_db_connection
    id_tan = request.args.get('id_tan')
    id_pro = request.args.get('id_pro')
    id_tan_del = request.args.get('id_tan_del')
    if id_tan_del is not None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:            
                # Ejecutamos la eliminación del tanque del proyecto
                cur.execute('''
                    UPDATE tanque SET cap_tan = %s, x_tan = %s, y_tan = %s, deleted_at = CURRENT_TIMESTAMP  WHERE id_pro = %s;
                ''', (0 ,515 ,300 , id_pro))
                conn.commit()
        
        # Redirigir al inicio del proyecto
        return redirect(url_for('hidrica.inicio_proyecto_hidrica', id_pro=id_pro))
    
    else:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Obtener los detalles del tanque que se esta usando en el proyecto
                cur.execute('SELECT id_tan,id_pro FROM tanque WHERE id_tan = %s;', (id_tan,))
                tan = cur.fetchone()
        
        # Renderizar la plantilla para mostrar el modal de eliminación
        return render_template('creacion_de_proyecto/delete_tanque_project.html', tan=tan)
################################################################################################################################################

#Eliminar motobomba
@hidrica_bp.route('/ver_modal_del_mot')
def ver_modal_del_mot():
    from app import get_db_connection
    id_pro = request.args.get('id_pro')
    id_mot_del = request.args.get('id_mot_del')
    if id_mot_del is not None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:            
                # Ejecutamos la eliminación del motobomba del proyecto
                cur.execute('''
                    UPDATE proyecto_hidrica SET id_mot = %s, x_mot=%s, y_mot=%s  WHERE id_pro = %s;
                ''', (None, 395, 80, id_pro))
                cur.execute('delete from tubo where id_pro=%s;', (id_pro,))
                conn.commit()
        
        # Redirigir al inicio del proyecto
        return redirect(url_for('hidrica.inicio_proyecto_hidrica', id_pro=id_pro))
    
    else:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Obtener los detalles del motobomba que se esta usando en el proyecto
                cur.execute('SELECT id_mot,id_pro FROM proyecto_hidrica WHERE id_pro = %s;', (id_pro,))
                mot = cur.fetchone()
        
        # Renderizar la plantilla para mostrar el modal de eliminación
        return render_template('creacion_de_proyecto/delete_motobomba_project.html', mot=mot)
    
#Resetear Tuberia
@hidrica_bp.route('/reset_tub')
def reset_tub():
    from app import get_db_connection
    id_pro = request.args.get('id_pro')
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('delete from tubo where id_pro=%s;', (id_pro,))
            cur.execute('''
                UPDATE trayectoria_tubo SET alt_tra = %s  WHERE id_pro = %s;
            ''', (0, id_pro))
            conn.commit()
    return redirect(url_for('hidrica.inicio_proyecto_hidrica', id_pro=id_pro))

################################################################################################################################################
#--------------------------------------------ELIMINAR PROYECTO HIDRICO-------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################


#Eliminar un proyecto
@hidrica_bp.route('/delete_project_hidrica')
def delete_project_hidrica():
    from app import get_db_connection
    id_pro = request.args.get('id_pro')
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Ejecutar la consulta para actualizar el estado del proyecto a "false"
            cur.execute('''
                UPDATE proyecto_hidrica SET status = false WHERE id_pro = %s
            ''', (id_pro,))
            
            # Confirmar los cambios en la base de datos
            conn.commit()
    
    # Redirigir de vuelta a la lista de proyectos
    return redirect(url_for('hidrica.list_project_hidrica'))

################################################################################################################################################
#---------------------------------------------------------INFORMES------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################
@hidrica_bp.route('/informes_hidrica',methods=['GET', 'POST'])
def informes_hidrica():
    from app import get_db_connection
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
                # Ejecuta la consulta usando id_pro como parámetro
                cur.execute('''
                    select p.created_at, p.nom_pro, avg(e.tot_ene)as tot_ene, avg(e.efi_ene)as efi_ene, p.eje_pro
                    from  proyecto_hidrica p 
                    join trayectoria_tubo t on t.id_pro=p.id_pro 
                    join energia_generada e on e.id_pro=t.id_pro group by p.created_at, p.nom_pro, p.eje_pro order by p.created_at desc limit 30;

                ''')
                sist_optima = cur.fetchall()  # Obtiene todos los resultados de la consulta
                if request.method == 'POST':
                    start_date = request.form['start_date']
                    end_date = request.form['end_date'] 
                    start_date = f"{start_date} 00:00:00"  # Agrega hora 06:00:00 a la fecha de inicio
                    end_date = f"{end_date} 23:59:59"
                    print('DAMOS INFORMES',start_date,'-',end_date)
                    # Ejecuta la consulta usando id_pro como parámetro
                    cur.execute('''
                        SELECT p.id_pro, p.created_at,  p.nom_pro, 
                        (SELECT COUNT(id_mot) FROM motobomba WHERE id_mot = p.id_mot) AS cant_mot,
                        (SELECT COUNT(id_gen) FROM proyecto_generador WHERE id_pro = p.id_pro) AS cant_gen,
                        (SELECT COUNT(id_tur) FROM proyecto_turbina WHERE id_pro = p.id_pro) AS cant_tur,
                        (SELECT COUNT(id_tan) FROM tanque WHERE id_pro = p.id_pro and cap_tan!=0) AS cant_tan,
                        (SELECT COUNT(id_pcar) FROM proyecto_cargah WHERE id_pro = p.id_pro and pot_pcar!=0) AS cant_pcar,
                        avg(e.tot_ene), p.status
                        from  proyecto_hidrica p 
                        left join trayectoria_tubo t on t.id_pro=p.id_pro 
                        left join energia_generada e on e.id_pro=t.id_pro
                        WHERE p.created_at >= %s AND p.created_at <= %s
                        GROUP BY p.id_pro, p.created_at, p.nom_pro order by created_at desc;
                    ''', (start_date, end_date,))
                else:
                    print('DAMOS INFORMES',start_date,'-',end_date)
                    # Ejecuta la consulta usando id_pro como parámetro
                    cur.execute('''
                        SELECT p.id_pro, p.created_at,  p.nom_pro, 
                        (SELECT COUNT(id_mot) FROM motobomba WHERE id_mot = p.id_mot) AS cant_mot,
                        (SELECT COUNT(id_gen) FROM proyecto_generador WHERE id_pro = p.id_pro) AS cant_gen,
                        (SELECT COUNT(id_tur) FROM proyecto_turbina WHERE id_pro = p.id_pro) AS cant_tur,
                        (SELECT COUNT(id_tan) FROM tanque WHERE id_pro = p.id_pro and cap_tan!=0) AS cant_tan,
                        (SELECT COUNT(id_pcar) FROM proyecto_cargah WHERE id_pro = p.id_pro and pot_pcar!=0) AS cant_pcar,
                        avg(e.tot_ene), p.status
                        from  proyecto_hidrica p 
                        left join trayectoria_tubo t on t.id_pro=p.id_pro 
                        left join energia_generada e on e.id_pro=t.id_pro
                        GROUP BY p.id_pro, p.created_at, p.nom_pro order by created_at desc limit 30;
                    ''')
                estructuras = cur.fetchall()  # Obtiene todos los resultados de la consulta
        return render_template('informe_y_Estadistica/informes_hidrica.html',sist_optima=sist_optima,estructuras=estructuras)
    else:
        return redirect(url_for('inicio_principal'))


################################################################################################################################################
#--------------------------------------------EJECUTAR PROYECTO HIDRICO-------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################

def ejecutar_proyecto_hidrica():
    from app import get_db_connection
    
    global corriente_hidrica
    global voltaje_VDC_hidrica
    global fechahora_dato
    print("ENTREA 2 HIHI")
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Obtener todos los proyectos con eje_pro = True
            cur.execute('''
                SELECT t.alt_tra, p.id_pro, g.id_pgen, gen.pot_gen, mot.pre_mot, t.dia_tra
                FROM trayectoria_tubo t 
                JOIN proyecto_hidrica p ON t.id_pro = p.id_pro 
                JOIN proyecto_generador g ON g.id_pro = p.id_pro 
                JOIN generador gen ON gen.id_gen = g.id_gen
				JOIN motobomba mot ON mot.id_mot = p.id_mot
                WHERE p.eje_pro = %s
                GROUP BY p.id_pro, t.alt_tra, g.id_pgen, gen.pot_gen, mot.pre_mot, t.dia_tra;
            ''', (True,))
            
            proyectos = cur.fetchall()
            
            for tot_alt, id_pro, id_pgen, pot_gen, pre_mot, dia_tra in proyectos:

                # Buscar última fecha de registro de energía
                cur.execute('SELECT created_at FROM energia_generada WHERE id_pro = %s ORDER BY created_at DESC LIMIT 1;', (id_pro,))
                fecha = cur.fetchone()
                fecha_dato = fecha[0] if fecha else None  # Puede que no exista aún
                
                gravedad=9.8#Gravedad como constante
                densidad_agua=997#Densidad del agua
                area=math.pi*((dia_tra*0.01)**2/4)# Calculo de area transversal

                if tot_alt>0:# en caso de que que la altura fuera menor que 0
                    presion = round(densidad_agua * gravedad * tot_alt,2)
                    velocidad= math.sqrt(2*gravedad*tot_alt)
                else:
                    presion = pre_mot * 100000 #conversion de bar a pascales
                    velocidad= math.sqrt(2*presion/densidad_agua)
                print("presion",presion)
                print("densidad",densidad_agua)
                print("velocidad",velocidad)
                # Caudal en m³/s
                caudal_m3s = area*velocidad

                # Potencia hidráulica real en W
                potencia_hidrica = round((presion * caudal_m3s),2)

                potencia_electrica = round((voltaje_VDC_hidrica * corriente_hidrica),2)

                print("potencia_electrica: ",potencia_electrica,"potencia_hidrica: ",potencia_hidrica)
                print("Proyecto:", id_pro)
                print("Altura:", tot_alt)
                print("Area:", area," * velocidad:", velocidad,"=",area*velocidad)
                print("Presión calculada:", presion," * caudal calculada:", caudal_m3s,"=",presion*caudal_m3s)
                print("Última fecha:", fecha_dato, "- Nueva fecha:", fechahora_dato)

                # Calcular eficiencia energética
                efi_ene = round((potencia_electrica / potencia_hidrica) * 100,2) if pot_gen else 0
                print("potencia_electrica: ",potencia_electrica,"potencia_hidrica: ",potencia_hidrica,"Eficiencia: ",efi_ene)
                # Buscar energía acumulada anterior
                cur.execute('SELECT tot_ene FROM energia_generada WHERE id_pro = %s ORDER BY created_at DESC LIMIT 1;', (id_pro,))
                resultado = cur.fetchone()
                energia_prev = resultado[0] if resultado else 0

                # Calcular energía generada en el intervalo de 5 minutos (en kWh)
                energia_intervalo = (potencia_hidrica / 1000.0) * (5 / 60.0)  # 5 min = 1/12 h
                energia_total = round(energia_prev + energia_intervalo, 3)

                # Insertar si es una nueva medición
                if not fecha_dato or str(fecha_dato) != str(fechahora_dato):
                    print("Inserta nueva medición")
                    cur.execute('''
                        INSERT INTO energia_generada (id_pro, tot_ene, id_pgen, efi_ene, cau_ene, alt_ene, pre_ene, vsal_ene, csal_ene, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (id_pro, energia_total, id_pgen, efi_ene, caudal_m3s, tot_alt, presion, voltaje_VDC_hidrica, corriente_hidrica, fechahora_dato))
                    conn.commit()
                
                cur.execute('''
                    UPDATE proyecto_generador SET cau_pgen = %s WHERE id_pro = %s ;
                ''', (caudal_m3s, id_pro))
                conn.commit()

                print(f"Registro actualizado para id_pro {id_pro} con eficiencia {efi_ene:.2f}%\n")


#mostrar modal para establecer conexion sesores hidrica
@hidrica_bp.route('/modal_conexion_sensor_hidrica')
def modal_conexion_sensor_hidrica():    
    from app import get_db_connection
    id_pro = request.args.get('id_pro')
    num_info = request.args.get('num_info')
    eje = request.args.get('eje')
    print("Si ENTRA MODAL HIDRICA CODE")
    # Obtener detalles del proyecto usando SQLAlchemy con la conexión abierta
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select * from proyecto_hidrica where id_pro= %s ;', (id_pro,))
            pro = cur.fetchone() 
    return render_template('creacion_de_proyecto/conexion_sensor_hidrica.html', pro = pro, num_info=num_info,eje=eje)
            

#Mostrar datos de proyecto generacion de energia
def mostrar_ejecucion_proyecto_hidrica(id_pro,start_date,end_date):
    from app import get_db_connection
    print(start_date,'-',end_date)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if start_date is None and end_date is None:
                cur.execute('''SELECT p.id_pro, e.efi_ene, e.tot_ene, e.created_at, p.eje_pro, e.alt_ene, e.cau_ene, e.pre_ene, e.vsal_ene, e.csal_ene FROM trayectoria_tubo t JOIN proyecto_hidrica p ON t.id_pro = p.id_pro JOIN energia_generada e ON e.id_pro= t.id_pro where p.id_pro=%s ORDER BY e.created_at desc limit 257;''', (id_pro,))
            else:
                cur.execute('SELECT p.id_pro, e.efi_ene, e.tot_ene, e.created_at, p.eje_pro, e.alt_ene, e.cau_ene, e.pre_ene, e.vsal_ene, e.csal_ene FROM trayectoria_tubo t JOIN proyecto_hidrica p ON t.id_pro = p.id_pro JOIN energia_generada e ON e.id_pro = t.id_pro WHERE (e.created_at >= %s and e.created_at <= %s) and p.id_pro=%s ORDER BY e.created_at desc;', (start_date, end_date, id_pro,))
            result_proyect_ene = cur.fetchall()# Obtener el id_pro de la carga
            return result_proyect_ene
        
# Ruta para obtener los últimos datos del proyecto en formato JSON
@hidrica_bp.route('/get_latest_proyecto_data/<int:id_pro>', methods=['GET'])
def get_latest_proyecto_data(id_pro):
    from app import get_db_connection
    with get_db_connection() as conn:  
        with conn.cursor() as cur:  
            # Ejecuta la consulta usando id_pro como parámetro
            cur.execute('''
                SELECT p.id_pro, e.tot_ene, e.efi_ene, e.cau_ene, e.alt_ene, e.created_at, e.pre_ene, e.vsal_ene, e.csal_ene  
                FROM energia_generada e 
				JOIN trayectoria_tubo t ON t.id_pro = e.id_pro
                JOIN proyecto_hidrica p ON t.id_pro = p.id_pro 
                WHERE p.id_pro = %s
                ORDER BY e.created_at DESC 
                LIMIT 1
            ''', (id_pro,))
            db_irr = cur.fetchall()  # Obtiene todos los resultados de la consulta

    # Estructura los datos en una lista de diccionarios con formato ajustado
    data = [{
        'tot_ene': f"{float(row[1]):.3f}",        
        'efi_ene': f"{float(row[2]):.2f}",
        'cau_ene': f"{float(row[3]):.3f}",
        'alt_ene': f"{float(row[4]):.3f}",
        'created_at': row[5].strftime('%Y-%m-%d %H:%M:%S'),
        'pre_ene': f"{float(row[6]):.3f}",
        'vsal_ene': f"{float(row[7]):.3f}",
        'csal_ene': f"{float(row[8]):.3f}",
    } for row in db_irr]
    
    return jsonify(data)  # Devuelve los datos en formato JSON

def procesar_datos_hidrica(data):
    global voltaje_VDC_hidrica, codigo_VDC_hidrica, caudal_hidrica, presion_hidrica, corriente_hidrica, fechahora_dato

    if all(k in data for k in ['voltaje', 'codigo', 'caudal', 'corriente', 'presion']):
        with lock:            
            voltaje_VDC_hidrica = data['voltaje']
            codigo_VDC_hidrica = data['codigo']
            caudal_hidrica = data['caudal']
            corriente_hidrica = data['corriente']
            presion_hidrica = data['presion']
            print(f"Código: {codigo_VDC_hidrica}")
            ahora = datetime.now()
            print("AHORA", ahora)
            if ahora.minute % 5 == 0:  
                ahora = ahora.replace(second=0)
                fechahora_dato=ahora.timestamp() 
                print(fechahora_dato)
                fechahora_dato = datetime.fromtimestamp(fechahora_dato).strftime('%Y-%m-%d %H:%M:%S')    
                print(fechahora_dato)         
                print("ENTRA 2")
                print(f"💧 Hidráulica -> V: {voltaje_VDC_hidrica} V | A: {corriente_hidrica} A | Caudal: {caudal_hidrica} L/min | P: {presion_hidrica} bar | Código: {codigo_VDC_hidrica}| FechaHora: {fechahora_dato}")
                ejecutar_proyecto_hidrica() 
        return True
    return False