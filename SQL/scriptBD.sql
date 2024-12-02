DROP DATABASE IF EXISTS emprego;

CREATE DATABASE emprego;

USE emprego;

CREATE TABLE company (
    companyID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    cnpj CHAR(14) NOT NULL,
    phone CHAR(11) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(30) NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'active' NOT NULL
) ;

CREATE TABLE vacancy (
    vacancyID INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    arrangement ENUM('Onsite', 'Hybrid', 'Remote') NOT NULL,
    type ENUM ('CLT', 'PJ') NOT NULL,
    location VARCHAR(100),
    salary VARCHAR(10),
    companyID INT NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'active' NOT NULL,
    FOREIGN KEY (companyID) REFERENCES company(companyID)
) ;

CREATE TABLE apply (
    applyID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fileName VARCHAR(100),
    vacancyID INT,
    FOREIGN KEY (vacancyID) REFERENCES vacancy(vacancyID) 
) ;

CREATE USER 'emprego'@'localhost'
IDENTIFIED WITH mysql_native_password
BY 'empregoadmin' ;

GRANT ALL PRIVILEGES ON emprego.* TO 'emprego'@'localhost' ; 