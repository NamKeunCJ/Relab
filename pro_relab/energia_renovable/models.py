from app import db

class Usuario(db.Model):
    id_usu = db.Column(db.Integer, primary_key=True)
    nom_usu = db.Column(db.String(50), nullable=False)
    ape_usu = db.Column(db.String(50), nullable=False)
    cor_usu = db.Column(db.String(100), unique=True, nullable=False)
    per_usu = db.Column(db.String(15), nullable=False, default='Cliente')
    doc_usu = db.Column(db.String(10), unique=True, nullable=False)
    con_usu = db.Column(db.String(35), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=False, default=1)

class Roles(db.Model):
    id_rol = db.Column(db.Integer, primary_key=True)
    tip_rol = db.Column(db.String(30), nullable=False)

class Panel(db.Model):
    id_pan = db.Column(db.Integer, primary_key=True)
    ref_pan = db.Column(db.String(100), nullable=False)
    pmax_pan = db.Column(db.Float, nullable=False)
    vmp_pan = db.Column(db.Float, nullable=False)
    imp_pan = db.Column(db.Float, nullable=False)
    voc_pan = db.Column(db.Float, nullable=False)
    isc_pan = db.Column(db.Float, nullable=False)
    lar_pan = db.Column(db.Float, nullable=False)
    anc_pan = db.Column(db.Float, nullable=False)
    are_pan = db.Column(db.Float, nullable=False)
    efi_pan = db.Column(db.Float, nullable=False)
    id_tec = db.Column(db.Integer, db.ForeignKey('tecnologia_panel.id_tec'), nullable=False)
    den_pan = db.Column(db.Float, nullable=False) 
    id_usu = db.Column(db.Integer, db.ForeignKey('usuario.id_usu'), nullable=False)
    idu_pan = db.Column(db.String(13), nullable=False)
    est_pan = db.Column(db.String(13), nullable=False, default='Habilitado')
    

class TecnologiaPanel(db.Model):
    id_tec = db.Column(db.Integer,primary_key=True)
    nom_tec = db.Column (db.String(100),nullable=False)

class Inversor(db.Model):
    id_inv = db.Column(db.Integer, primary_key=True)
    ref_inv = db.Column(db.String(100), nullable=False)
    ent_inv = db.Column(db.Integer, nullable=False)
    pmax_inv = db.Column(db.Float, nullable=False)
    vme_inv = db.Column(db.Float, nullable=False)
    ime_inv = db.Column(db.Float, nullable=False)
    vsa_inv = db.Column(db.Float, nullable=False)
    ond_inv = db.Column(db.String(7), nullable=False)
    efi_inv = db.Column(db.Float, nullable=False)
    id_usu = db.Column(db.Integer, db.ForeignKey('usuario.id_usu'), nullable=False)
    idu_inv = db.Column(db.String(13), nullable=False)
    est_inv = db.Column(db.String(13), nullable=False, default='Habilitado')

class Bateria(db.Model):
    id_bat = db.Column(db.Integer, primary_key=True)
    ref_bat = db.Column(db.String(100), nullable=False)
    vol_bat = db.Column(db.Float, nullable=False)
    cap_bat = db.Column(db.Float, nullable=False)
    ene_bat = db.Column(db.Float, nullable=False)
    id_usu = db.Column(db.Integer, db.ForeignKey('usuario.id_usu'), nullable=False)
    idu_bat = db.Column(db.String(13), nullable=False)
    est_bat = db.Column(db.String(13), nullable=False, default='Habilitado')

class Proyecto(db.Model):
    id_pro = db.Column(db.Integer, primary_key=True)
    nom_pro = db.Column(db.String(100), nullable=False)
    fec_pro = db.Column(db.TIMESTAMP, server_default=db.func.now(), nullable=False)
    id_usu = db.Column(db.Integer, db.ForeignKey('usuario.id_usu'), nullable=False)
    cred_pro = db.Column(db.String(2), nullable=False)
    cbat_pro = db.Column(db.String(2), nullable=False)
    id_inv = db.Column(db.Integer, db.ForeignKey('inversor.id_inv'))
    est_pro = db.Column(db.String(13), nullable=False, default='Habilitado')
    eje_pro = db.Column(db.String(6), nullable=False, default='F')

class EnergiaArreglo(db.Model):
    id_ene = db.Column(db.Integer, primary_key=True)    
    efi_ene = db.Column(db.Float, nullable=False)
    tot_ene = db.Column(db.Float, nullable=False)
    id_pro = db.Column(db.Integer, db.ForeignKey('proyecto.id_pro'), nullable=False)
    id_sen = db.Column(db.Integer, db.ForeignKey('sensor_irradiancia.id_sen'), nullable=False)
    fec_ene = db.Column(db.TIMESTAMP, nullable=False)

class SensorIrradiancia(db.Model):
    id_sen = db.Column(db.Integer, primary_key=True)    
    fec_sen = db.Column(db.TIMESTAMP, nullable=False)
    g_sen = db.Column(db.Float, nullable=False)
    ref_sen = db.Column(db.String(50), nullable=False)

class Carga(db.Model):
    id_car = db.Column(db.Integer, primary_key=True)
    tip_car = db.Column(db.String(10), nullable=False)
    pot_car = db.Column(db.Float, default=0,nullable=False)        
    id_pro = db.Column(db.Integer, db.ForeignKey('proyecto.id_pro'), nullable=False)
    
class ArregloDePaneles(db.Model):
    id_arr = db.Column(db.Integer, primary_key=True)
    ptot_arr = db.Column(db.Float, default=0, nullable=False)
    vmax_arr = db.Column(db.Float, default=0, nullable=False)
    imax_arr = db.Column(db.Float, default=0, nullable=False)
    area_arr = db.Column(db.Float, default=0, nullable=False)
    fil_arr = db.Column(db.Integer, nullable=False)
    col_arr = db.Column(db.Integer, nullable=False)    
    id_pro = db.Column(db.Integer, db.ForeignKey('proyecto.id_pro'), nullable=False)
    efi_arr = db.Column(db.Float, nullable=False)
    
class ParaleloArreglo(db.Model):
    id_parr = db.Column(db.Integer, primary_key=True)
    fec_parr = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), nullable=False)
    pser_parr = db.Column(db.Float, default=0, nullable=False)
    vser_parr = db.Column(db.Float, default=0, nullable=False)
    iser_parr = db.Column(db.Float, default=0, nullable=False)
    aser_parr = db.Column(db.Float, default=0, nullable=False)
    id_arr = db.Column(db.Integer, db.ForeignKey('arreglo_de_paneles.id_arr'), nullable=False)
    efi_parr = db.Column(db.Float, nullable=False)
    
class SerieArreglo(db.Model):
    id_sarr = db.Column(db.Integer, primary_key=True)
    id_pan = db.Column(db.Integer, db.ForeignKey('panel.id_pan'))
    fec_sarr = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), nullable=False)
    id_parr = db.Column(db.Integer, db.ForeignKey('paralelo_arreglo.id_parr'), nullable=False)

class BancoDeBaterias(db.Model):
    id_ban = db.Column(db.Integer, primary_key=True)
    vol_ban = db.Column(db.Float, default=0, nullable=False)
    cap_ban = db.Column(db.Float, default=0, nullable=False)
    ene_ban = db.Column(db.Float, default=0, nullable=False)
    fil_ban = db.Column(db.Integer, nullable=False)
    col_ban = db.Column(db.Integer, nullable=False) 
    dod_ban = db.Column(db.Float, default=60, nullable=False)
    id_pro = db.Column(db.Integer, db.ForeignKey('proyecto.id_pro'), nullable=False)

class ParaleloBanco(db.Model):
    id_pban = db.Column(db.Integer, primary_key=True)
    fec_pban = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False)
    vser_pban = db.Column(db.Float, default=0, nullable=False)
    cser_pban = db.Column(db.Float, default=0, nullable=False)
    eser_pban = db.Column(db.Float, default=0, nullable=False)
    id_ban = db.Column(db.Integer, db.ForeignKey('banco_de_baterias.id_ban'), nullable=False)

class SerieBanco(db.Model):
    id_sban = db.Column(db.Integer, primary_key=True)
    id_bat = db.Column(db.Integer, db.ForeignKey('bateria.id_bat'))
    fec_sban = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False)
    id_pban = db.Column(db.Integer, db.ForeignKey('paralelo_banco.id_pban'), nullable=False)