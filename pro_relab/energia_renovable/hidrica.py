import psycopg2
import hashlib
from datetime import datetime, timedelta
import threading
import time
import requests # elementos para datos davis
# hidrica.py
from flask import Blueprint, render_template, request, session, redirect, url_for


# Crear un Blueprint para las rutas hídricas
hidrica_bp = Blueprint('hidrica', __name__, static_folder='static',template_folder='templates')

print("Hola")
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