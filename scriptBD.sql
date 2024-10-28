CREATE DATABASE emprego;

USE emprego;

CREATE TABLE company (
    ID_Company INT PRIMARY KEY AUTO_INCREMENT,
    name_Company VARCHAR(100) NOT NULL,
    cnpj CHAR(14) NOT NULL,
    phone CHAR(11) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(30) NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'active' NOT NULL
) ;

CREATE TABLE vacancy (
    ID_Vacancy INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    arrangement ENUM('Onsite', 'Hybrid', 'Remote') NOT NULL,
    type ENUM ('CLT', 'PJ') NOT NULL,
    location VARCHAR(100),
    salary VARCHAR(10),
    ID_Company INT NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'active' NOT NULL,
    FOREIGN KEY (ID_Company) REFERENCES company(ID_Company)
) ;