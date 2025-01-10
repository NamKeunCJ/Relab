import psycopg2
import hashlib
from datetime import datetime, timedelta
import threading
import time
import requests # elementos para datos davis
# hidrica.py
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify


# Crear un Blueprint para las rutas hídricas
hidrica_bp = Blueprint('hidrica', __name__, static_folder='static',template_folder='templates')

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
            cur.execute('SELECT id_pro FROM proyecto_hidrica WHERE nom_pro = %s AND id_usu = %s;', (nom_pro, user_id))
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
                conn.commit()
                
                return jsonify({'id_pro': id_pro})

#Iniciar Proyecto
@hidrica_bp.route('/inicio_proyecto_hidrica', methods=['GET', 'POST'])
def inicio_proyecto_hidrica(): 
    from app import get_db_connection
    num_info = request.args.get('num_info') 
    id_pro = request.args.get('id_pro')
    user_id = session.get('user_id')
    
    if user_id is None:
        # Si el usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
        return redirect(url_for('inicio_sesion')) 
    
    # Obtener detalles del proyecto
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Obtenemos el proyecto principal
            cur.execute('''SELECT 
                pro.*, mot.*, gen_pro.*,gen.*, tan.*, tur_pro.*,tur.*
                FROM 
                    proyecto_hidrica pro
                LEFT JOIN motobomba mot on pro.id_mot=mot.id_mot 
                LEFT JOIN proyecto_generador gen_pro ON pro.id_pro = gen_pro.id_pro
                LEFT JOIN generador gen ON gen_pro.id_gen = gen.id_gen
                LEFT JOIN tanque tan ON pro.id_pro = tan.id_pro
                LEFT JOIN proyecto_turbina tur_pro ON pro.id_pro = tur_pro.id_pro
                LEFT JOIN turbina tur ON tur_pro.id_tur = tur.id_tur
                WHERE 
                pro.id_pro = %s;
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
            # Obtenemos el proyecto principal
            cur.execute('SELECT * FROM proyecto_hidrica WHERE id_pro = %s AND id_usu = %s AND status = true;', (id_pro, user_id))
            pro_h = cur.fetchone()
            if pro_h:
                # Pasamos todo a la plantilla
                return render_template('creacion_de_proyecto/proyecto_hidrico.html', pro_com=pro_com, car_com=car_com, num_info=num_info, pro_h=pro_h)
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

#agregar el caudalimetro alproyecto
@hidrica_bp.route('/add_caudalimetro_project', methods=['POST'])
def add_caudalimetro_project():     
    from app import get_db_connection
    id_pro = request.form['id_pro']
    cau_pgen = request.form['cau_pgen']
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                UPDATE proyecto_generador
                SET cau_pgen = %s 
                WHERE id_pro = %s;
            ''', (cau_pgen, id_pro))
            conn.commit()
    return redirect(url_for('hidrica.inicio_proyecto_hidrica', id_pro=id_pro))

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
#--------------------------------------------EDITAR PROYECTO FOTOVOLTAICO-------------------------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################################

#Lista de proyectos fotovoltaicos creados
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
    