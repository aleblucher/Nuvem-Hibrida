DROP DATABASE IF EXISTS banana;
CREATE DATABASE banana;
USE banana;

CREATE TABLE tarefa (
    id_tarefa INT NOT NULL,
    description VARCHAR(120),
    difficulty INT,
    PRIMARY KEY (id_tarefa)
    );
