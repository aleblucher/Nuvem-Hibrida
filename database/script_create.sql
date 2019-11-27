DROP DATABASE IF EXISTS banana;
CREATE DATABASE banana;
USE banana;

CREATE TABLE tarefa (
    id_tarefa INT AUTO_INCREMENT,
    description VARCHAR(120),
    difficulty INT,
    PRIMARY KEY (id_tarefa)
    );