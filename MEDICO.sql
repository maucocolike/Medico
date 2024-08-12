CREATE DATABASE MEDICO

CREATE TABLE Estudios (
    EstudiosID INT IDENTITY PRIMARY KEY,
    tipo_estudio VARCHAR(255) NOT NULL
);
CREATE TABLE Roles (
    rolID INT IDENTITY (1,1) PRIMARY KEY,
    especialidad NVARCHAR(100) NOT NULL,
    nombre NVARCHAR(100) NOT NULL,
    cedula NVARCHAR(20) NOT NULL UNIQUE
);
CREATE TABLE Especialidad (
    especialidadID INT IDENTITY(1,1) PRIMARY KEY,
    tipo_especialidad VARCHAR(100)
);
CREATE TABLE Medicos (
    medicoID INT IDENTITY (1,1) PRIMARY KEY ,
    RFC NVARCHAR(13) NOT NULL UNIQUE,
    nombre NVARCHAR(255) NOT NULL,
    cedula NVARCHAR(20) NOT NULL UNIQUE,
    correo NVARCHAR(255) NOT NULL UNIQUE,
    contrase�a VARCHAR(255) NOT NULL,
    rolID INT,
	especialidadID INT,
    FOREIGN KEY (rolID) REFERENCES Roles(rolID),
	FOREIGN KEY (especialidadID) REFERENCES Especialidad(especialidadID)
);

CREATE TABLE Pacientes (
    pacienteID INT IDENTITY (1,1) PRIMARY KEY ,
    nombre NVARCHAR(255) NOT NULL,
    resultado_exploracion TEXT,
);
ALTER TABLE Pacientes
ADD FOREIGN KEY (expedienteID) REFERENCES Expedientes(expedienteID);

CREATE TABLE Citas (
    citaID INT IDENTITY (1,1) PRIMARY KEY,
    fecha DATETIME NOT NULL,
    pacienteID INT NOT NULL,
    medicoID INT NOT NULL,
    FOREIGN KEY (medicoID) REFERENCES Medicos(medicoID),
	FOREIGN KEY (pacienteID) REFERENCES Pacientes(pacienteID)
);
CREATE TABLE Diagnosticos (
    diagnosticoID INT IDENTITY(1,1) PRIMARY KEY,
    citaID INT NOT NULL,
    resultado_exploracion TEXT,
    sintomas TEXT,
    Dx TEXT,
    tratamiento TEXT,
    estudiosID INT,
    FOREIGN KEY (citaID) REFERENCES Citas(citaID),
    FOREIGN KEY (estudiosID) REFERENCES Estudios(estudiosID)
);
CREATE TABLE Exploraciones (
    exploracionID INT IDENTITY (1,1) PRIMARY KEY ,
    pacienteID INT NOT NULL,
    fecha DATETIME NOT NULL,
    peso DECIMAL(5,2),
    altura DECIMAL(5,2),
    temperatura DECIMAL(4,2),
    saturacion_glucosa DECIMAL(5,2),
    edad INT,
    FOREIGN KEY (pacienteID) REFERENCES Pacientes(pacienteID)
);
CREATE TABLE Recetas (
    recetaID INT IDENTITY (1,1)PRIMARY KEY,
    fecha DATETIME NOT NULL,
    pacienteID INT NOT NULL,
    diagnosticoID INT NOT NULL,
    FOREIGN KEY (pacienteID) REFERENCES Pacientes(pacienteID),
    FOREIGN KEY (diagnosticoID) REFERENCES Diagnosticos(diagnosticoID)
);

CREATE TABLE Expedientes(
    expedienteID INT IDENTITY (1,1)PRIMARY KEY,
    medicoID INT NOT NULL,
    nombre NVARCHAR(255) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    enfer_cronicas TEXT,
    alergias TEXT,
    fecha_creacion DATE,
    fecha_actualizacion DATE,
    diagnosticoID INT,
    exploracionID INT,
    FOREIGN KEY (medicoID) REFERENCES Medicos(medicoID),
    FOREIGN KEY (diagnosticoID) REFERENCES Diagnosticos(diagnosticoID),
    FOREIGN KEY (exploracionID) REFERENCES Exploraciones(exploracionID)
);

-------------------------------------------------------------

