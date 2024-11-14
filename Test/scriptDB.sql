DROP DATABASE IF EXISTS teste_upload;

CREATE DATABASE teste_upload;

USE teste_upload;

CREATE TABLE arquivo (
	idarquivo INT PRIMARY KEY AUTO_INCREMENT,
    nomearquivo VARCHAR(100) NOT NULL,
    data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
