SELECT to_char(created_at, 'YYYY-MM-DD HH24:00:00') AS datetime, SUM(dat_dem) AS total_dem
	FROM dato_demanda 
	GROUP BY to_char(created_at, 'YYYY-MM-DD HH24:00:00')
	ORDER BY to_char(created_at, 'YYYY-MM-DD HH24:00:00');

--Excedente
SELECT DATE(created_at),SUM(dat_dem) FROM dato_demanda GROUP BY DATE(created_at) ORDER BY DATE(created_at);

--Consumo
SELECT DATE(datetime),SUM(total_dem) 
FROM (SELECT to_char(created_at, 'YYYY-MM-DD HH24:00:00') AS datetime, SUM(dat_dem) AS total_dem
	FROM dato_demanda 
	GROUP BY to_char(created_at, 'YYYY-MM-DD HH24:00:00')
	ORDER BY to_char(created_at, 'YYYY-MM-DD HH24:00:00')) AS datos
WHERE total_dem>=0 GROUP BY DATE(datetime) ORDER BY DATE(datetime);
--Energia Perdida
SELECT DATE(datetime),SUM(total_dem) 
FROM (SELECT to_char(created_at, 'YYYY-MM-DD HH24:00:00') AS datetime, SUM(dat_dem) AS total_dem
	FROM dato_demanda 
	GROUP BY to_char(created_at, 'YYYY-MM-DD HH24:00:00')
	ORDER BY to_char(created_at, 'YYYY-MM-DD HH24:00:00')) AS datos
WHERE total_dem<=0  GROUP BY DATE(datetime) ORDER BY DATE(datetime);


-----------------------------------------------------
--Promedio consumo neto
SELECT 'Promedio consumo neto' as nom_adem, AVG(exc_adem) FROM analisis_demanda WHERE per_adem < -2500 AND per_adem IS NOT NULL;
--Promedio actual neto
SELECT 'Promedio actual neto' as nom_adem, AVG(con_adem) FROM analisis_demanda WHERE per_adem < -2500 AND per_adem IS NOT NULL;
--Energía perdida
SELECT 'Energía perdida' as nom_adem, AVG(per_adem) FROM analisis_demanda WHERE per_adem < -2500 AND per_adem IS NOT NULL;
-- Pagaría a full
SELECT 'Pagaría a full' as nom_adem, AVG(con_adem) FROM analisis_demanda WHERE per_adem IS NULL;

-----------------------------------------------------
--consumo neto
SELECT 'Consumo neto' as nom_adem, SUM(exc_adem)*1,5 FROM analisis_demanda;
--consumo actual neto
SELECT 'Consumo actual neto' as nom_adem, SUM(con_adem)*1,5 FROM analisis_demanda;
--Energía perdida
SELECT 'Energía perdida' as nom_adem, SUM(per_adem)*1,5 FROM analisis_demanda;
-- Pagaría a full
SELECT 'Pagaría a full' as nom_adem, SUM(con_adem)*10 FROM analisis_demanda WHERE per_adem IS NULL;

---tabla analisis demanda
SELECT fec_adem, exc_adem, con_adem, per_adem FROM analisis_demanda ORDER BY fec_adem ASC;

--MODELO DE PREDICCION
select * from dato_irradiancia where created_at >= '2024-08-13' and created_at < '2024-08-18' order by created_at desc;



--delete from dato_irradiancia;
--SELECT setval(pg_get_serial_sequence('dato_irradiancia', 'id_irr'), 1, false);
--COPY PUBLIC.dato_irradiancia (created_at,prom_irr,max_irr) FROM 'C:\Dataset_2013_2024_Completo.csv' DELIMITER ',' CSV HEADER;
delete from energia_generada;
SELECT setval(pg_get_serial_sequence('energia_generada', 'id_ene'), 1, false);
delete from proyecto_generador;
SELECT setval(pg_get_serial_sequence('proyecto_generador', 'id_pgen'), 1, false);
delete from tanque;
SELECT setval(pg_get_serial_sequence('tanque', 'id_tan'), 1, false);
delete from proyecto_turbina;
SELECT setval(pg_get_serial_sequence('proyecto_turbina', 'id_ptur'), 1, false);
delete from proyecto_cargah;
SELECT setval(pg_get_serial_sequence('proyecto_cargah', 'id_pcar'), 1, false);
delete from tubo;
SELECT setval(pg_get_serial_sequence('tubo', 'id_tub'), 1, false);
delete from trayectoria_tubo;
SELECT setval(pg_get_serial_sequence('trayectoria_tubo', 'id_tra'), 1, false);
delete from proyecto_hidrica;
SELECT setval(pg_get_serial_sequence('proyecto_hidrica', 'id_pro'), 1, false);

---NO EJECUTAR
delete from energia_arreglo;
SELECT setval(pg_get_serial_sequence('energia_arreglo', 'id_ene'), 1, false);
delete from serie_arreglo;
SELECT setval(pg_get_serial_sequence('serie_arreglo', 'id_sarr'), 1, false);
delete from paralelo_arreglo;
SELECT setval(pg_get_serial_sequence('paralelo_arreglo', 'id_parr'), 1, false);
delete from arreglo_de_paneles;
SELECT setval(pg_get_serial_sequence('arreglo_de_paneles', 'id_arr'), 1, false);
delete from serie_banco;
SELECT setval(pg_get_serial_sequence('serie_banco', 'id_sban'), 1, false);
delete from paralelo_banco;
SELECT setval(pg_get_serial_sequence('paralelo_banco', 'id_pban'), 1, false);
delete from banco_de_baterias;
SELECT setval(pg_get_serial_sequence('banco_de_baterias', 'id_ban'), 1, false);
delete from proyecto_carga;
SELECT setval(pg_get_serial_sequence('proyecto_carga', 'id_pcar'), 1, false);
delete from proyecto_fotovoltaica;
SELECT setval(pg_get_serial_sequence('proyecto_fotovoltaica', 'id_pro'), 1, false);


delete from panel;
SELECT setval(pg_get_serial_sequence('panel', 'id_pan'), 1, false);
delete from bateria;
SELECT setval(pg_get_serial_sequence('bateria', 'id_bat'), 1, false);
delete from inversor;
SELECT setval(pg_get_serial_sequence('inversor', 'id_inv'), 1, false);
delete from regulador;
SELECT setval(pg_get_serial_sequence('regulador', 'id_reg'), 1, false);