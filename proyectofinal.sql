CREATE DATABASE  indicadores_agua_inegi;
USE indicadores_agua_inegi;

CREATE TABLE indicadores(
id_indicador BIGINT PRIMARY KEY,
nom_Ind VARCHAR (60)
);


CREATE TABLE estados(
id_estado INT PRIMARY KEY,
nom_Est VARCHAR (60)
);

CREATE TABLE datos(
id_dato INT auto_increment PRIMARY KEY,
año INT,
id_estado INT,
valor FLOAT,
id_indicador BIGINT,
FOREIGN KEY (id_indicador) REFERENCES indicadores(id_indicador),
FOREIGN KEY (id_estado) REFERENCES estados (id_estado)
);


select * from estados;

desc log_indicadores;
show tables;

