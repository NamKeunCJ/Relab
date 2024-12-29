CREATE TABLE IF NOT EXISTS public.motobomba
(
    id_mot serial NOT NULL,
    ref_mot character varying(100) COLLATE pg_catalog."default" NOT NULL,
    pot_mot double precision NOT NULL,
    vol_mot double precision NOT NULL,
    cau_mot double precision NOT NULL,
    dent_mot double precision NOT NULL,
    dsal_mot double precision NOT NULL,
    fre_mot double precision NOT NULL,
    pre_mot double precision NOT NULL,
    id_usu integer NOT NULL,
    idu_mot character varying(13) COLLATE pg_catalog."default" NOT NULL,
    status boolean NOT NULL DEFAULT true,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp without time zone,
    CONSTRAINT motobomba_pkey PRIMARY KEY (id_mot)
);
ALTER TABLE IF EXISTS public.motobomba
    ADD CONSTRAINT motobomba_id_usu_fkey FOREIGN KEY (id_usu)
    REFERENCES public.usuario (id_usu) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

CREATE TABLE IF NOT EXISTS public.generador
(
    id_gen serial NOT NULL,
    ref_gen character varying(100) COLLATE pg_catalog."default" NOT NULL,
    pot_get double precision NOT NULL,
    vol_gen double precision NOT NULL,
    vel_gen double precision NOT NULL,
    dia_gen double precision NOT NULL,
    id_usu integer NOT NULL,
    idu_gen character varying(13) COLLATE pg_catalog."default" NOT NULL,
    status boolean NOT NULL DEFAULT true,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp without time zone,
    CONSTRAINT generador_pkey PRIMARY KEY (id_gen)
);
ALTER TABLE IF EXISTS public.generador
    ADD CONSTRAINT generador_id_usu_fkey FOREIGN KEY (id_usu)
    REFERENCES public.usuario (id_usu) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

CREATE TABLE IF NOT EXISTS public.codo
(
    id_cod serial NOT NULL,
    ang_cod double precision NOT NULL,
    dia_cod double precision NOT NULL,
    status boolean NOT NULL DEFAULT true,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp without time zone,
    CONSTRAINT codo_pkey PRIMARY KEY (id_cod)
);


CREATE TABLE IF NOT EXISTS public.codo
(
    id_cod serial NOT NULL,
    ang_cod double precision NOT NULL,
    dia_cod double precision NOT NULL,
    status boolean NOT NULL DEFAULT true,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp without time zone,
    CONSTRAINT codo_pkey PRIMARY KEY (id_cod)
);

CREATE TABLE IF NOT EXISTS public.turbina
(
    id_tur serial NOT NULL,
    tip_tur character varying(30) COLLATE pg_catalog."default" NOT NULL,
    status boolean NOT NULL DEFAULT true,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp without time zone,
    CONSTRAINT turbina_pkey PRIMARY KEY (id_tur)
);


CREATE TABLE IF NOT EXISTS public.proyecto_hidrica
(
    id_pro serial NOT NULL,
    nom_pro character varying(100) COLLATE pg_catalog."default" NOT NULL,
    id_usu integer NOT NULL,
    cred_pro character varying(2) COLLATE pg_catalog."default" NOT NULL,
    id_mot integer,
    eje_pro boolean NOT NULL DEFAULT false,
    status boolean NOT NULL DEFAULT true,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp without time zone,
    CONSTRAINT proyecto_hidrica_pkey PRIMARY KEY (id_pro)
);

ALTER TABLE IF EXISTS public.proyecto_hidrica
    ADD CONSTRAINT proyecto_hidrica_id_usu_fkey FOREIGN KEY (id_usu)
    REFERENCES public.usuario (id_usu) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.proyecto_hidrica
    ADD CONSTRAINT proyecto_hidrica_id_mot_fkey FOREIGN KEY (id_mot)
    REFERENCES public.motobomba (id_mot) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

CREATE TABLE IF NOT EXISTS public.proyecto_generador
(
    id_pgen serial NOT NULL,
    cau_pgen  double precision NOT NULL DEFAULT 0,
    status boolean NOT NULL DEFAULT true,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp without time zone,
    id_gen integer NOT NULL,
    id_pro integer NOT NULL,
    CONSTRAINT proyecto_generador_pkey PRIMARY KEY (id_pgen)
);

ALTER TABLE IF EXISTS public.proyecto_generador
    ADD CONSTRAINT proyecto_generador_id_pro_fkey FOREIGN KEY (id_pro)
    REFERENCES public.proyecto_hidrica (id_pro) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.proyecto_generador
    ADD CONSTRAINT proyecto_generador_id_gen_fkey FOREIGN KEY (id_gen)
    REFERENCES public.generador (id_gen) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

CREATE TABLE IF NOT EXISTS public.proyecto_turbina
(
    id_ptur serial NOT NULL,
	cant_ptur integer NOT NULL,
    vel_ptur double precision NOT NULL DEFAULT 0,
    status boolean NOT NULL DEFAULT true,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp without time zone,
    id_tur integer NOT NULL,
    id_pro integer NOT NULL,
    CONSTRAINT proyecto_turbina_pkey PRIMARY KEY (id_ptur)
);

ALTER TABLE IF EXISTS public.proyecto_turbina
    ADD CONSTRAINT proyecto_turbina_id_pro_fkey FOREIGN KEY (id_pro)
    REFERENCES public.proyecto_hidrica (id_pro) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.proyecto_turbina
    ADD CONSTRAINT proyecto_turbina_id_tur_fkey FOREIGN KEY (id_tur)
    REFERENCES public.turbina (id_tur) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

CREATE TABLE IF NOT EXISTS public.proyecto_cargah
(
    id_pcar serial NOT NULL,
    pot_pcar double precision NOT NULL DEFAULT 0,
    status boolean NOT NULL DEFAULT true,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp without time zone,
    id_car integer NOT NULL,
    id_pro integer NOT NULL,
    x_pcar double precision NOT NULL DEFAULT 494,
    y_pcar double precision NOT NULL DEFAULT 20,
    CONSTRAINT proyecto_cargah_pkey PRIMARY KEY (id_pcar)
);

ALTER TABLE IF EXISTS public.proyecto_cargah
    ADD CONSTRAINT proyecto_cargah_id_car_fkey FOREIGN KEY (id_car)
    REFERENCES public.carga (id_car) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.proyecto_cargah
    ADD CONSTRAINT proyecto_cargah_id_pro_fkey FOREIGN KEY (id_pro)
    REFERENCES public.proyecto_hidrica (id_pro) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

CREATE TABLE IF NOT EXISTS public.tubo
(
    id_tub serial NOT NULL,
    lon_tub double precision NOT NULL,
	dia_tub double precision NOT NULL,
    status boolean NOT NULL DEFAULT true,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp without time zone,
    id_pro integer NOT NULL,
    CONSTRAINT tubo_pkey PRIMARY KEY (id_tub)
);

ALTER TABLE IF EXISTS public.tubo
    ADD CONSTRAINT tubo_id_pro_fkey FOREIGN KEY (id_pro)
    REFERENCES public.proyecto_hidrica (id_pro) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

CREATE TABLE IF NOT EXISTS public.tanque
(
    id_tan serial NOT NULL,
    cap_tan  double precision NOT NULL DEFAULT 0,
    status boolean NOT NULL DEFAULT true,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp without time zone,
    id_pro integer NOT NULL,
    CONSTRAINT tanque_pkey PRIMARY KEY (id_tan)
);

ALTER TABLE IF EXISTS public.tanque
    ADD CONSTRAINT tanque_id_pro_fkey FOREIGN KEY (id_pro)
    REFERENCES public.proyecto_hidrica (id_pro) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

CREATE TABLE IF NOT EXISTS public.tubo_codo
(
    id_tco serial NOT NULL,
	ori_tco character varying(10) COLLATE pg_catalog."default" NOT NULL DEFAULT 'Derecha'::character varying,
    alt_tco double precision NOT NULL DEFAULT 0,
    status boolean NOT NULL DEFAULT true,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp without time zone,
    id_cod integer NOT NULL,
    id_tub integer NOT NULL,
    CONSTRAINT tubo_codo_pkey PRIMARY KEY (id_tco)
);

ALTER TABLE IF EXISTS public.tubo_codo
    ADD CONSTRAINT tubo_codo_id_cod_fkey FOREIGN KEY (id_cod)
    REFERENCES public.codo (id_cod) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.tubo_codo
    ADD CONSTRAINT tubo_codo_id_tub_fkey FOREIGN KEY (id_tub)
    REFERENCES public.tubo (id_tub) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


CREATE TABLE IF NOT EXISTS public.energia_generada
(
    id_ene serial NOT NULL,
	tot_ene double precision NOT NULL DEFAULT 0,
    status boolean NOT NULL DEFAULT true,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp without time zone,
    id_pgen integer NOT NULL,
    id_tco integer NOT NULL,
    CONSTRAINT energia_generada_pkey PRIMARY KEY (id_ene)
);

ALTER TABLE IF EXISTS public.energia_generada
    ADD CONSTRAINT energia_generada_id_pgen_fkey FOREIGN KEY (id_pgen)
    REFERENCES public.proyecto_generador (id_pgen) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.energia_generada
    ADD CONSTRAINT energia_generada_id_tco_fkey FOREIGN KEY (id_tco)
    REFERENCES public.tubo_codo (id_tco) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
