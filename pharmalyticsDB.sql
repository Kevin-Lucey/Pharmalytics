drop database IF EXISTS Pharmalytics;
create database if not exists Pharmalytics;
use Pharmalytics;



## Creating the user login table
## where persona code is assigned when signed up to differentiate doctors, pharmacy techs ...
drop table if exists userLoginInfo;
CREATE TABLE IF NOT EXISTS userLoginInfo(
	username varchar(30) UNIQUE NOT NULL,
    usr_pwd  varchar(30) NOT NULL,
    personaCode int NOT NULL
);


## Doctor Information table
drop table if exists doctorInfo;
CREATE TABLE IF NOT EXISTS doctorInfo(
	doctorID int auto_increment primary key NOT NULL,
    doctorName varchar(40) NOT NULL,
    practiceAddr varchar(40) NOT NULL,
    username varchar(30) NOT NULL,
    usr_pwd varchar(30) NOT NULL
);

## Insurance Company Info
drop table if exists pharmacyInfo;
CREATE TABLE IF NOT EXISTS pharmacyInfo(
	pharmacyID int auto_increment primary key,
    pharmacyName varchar(30),
    username varchar(30),
    usr_pwd varchar(30)
);


## Patient Info table
drop table if exists patientInfo;
CREATE TABLE IF NOT EXISTS patientInfo(
	patientID int auto_increment primary key,
    patientName varchar(40) NOT NULL,
    username varchar(30) NOT NULL,
    usr_pwd  varchar(30) NOT NULL,
    doctorID int NOT NULL,
    pharmacyID int NOT NULL,
    FOREIGN KEY (doctorID) REFERENCES doctorInfo(doctorID),
    FOREIGN KEY (pharmacyID) REFERENCES pharmacyInfo(pharmacyID)
);


## Creating the Prescriptons info table
#drop table if exists medicationInfo;
CREATE TABLE IF NOT EXISTS medicationInfo(
	rxID int auto_increment primary key,
    rxName varchar(50),
    pharmaCompany varchar(30)
);

CREATE TABLE IF NOT EXISTS prescriptionInfo(
	prescriptionID  int auto_increment NOT NULL primary key,
    prescriptionName varchar(30) NOT NULL,
    prescriptionDosage int NOT NULL,
    prescriptionDate date NOT NULL,
    patientID int NOT NULL,
    doctorID int NOT NULL,
	quantity int NOT NULL,
    approved boolean NOT NULL,
    filled boolean NOT NULL,
    FOREIGN KEY (patientID) REFERENCES patientInfo(patientID),
    FOREIGN KEY (doctorID) REFERENCES doctorInfo(doctorID)
);
select * from prescriptionInfo;

CREATE TABLE IF NOT EXISTS Inventory(
	rxID int not null primary key,
    rxName varchar(30) NOT NULL,
    quantity int not null,
    foreign key (rxID) REFERENCES medicationInfo(rxID)
);



 INSERT IGNORE INTO userLoginInfo (username, usr_pwd, personaCode) VALUES
    ('dr_smith', 'doctorpass', 2),
    ('dr_brown', 'doctorpass2', 2),
    ('dr_johnson', 'doctorpass',2),
    ('dr_patel', 'doctorpass',2),
    ('dr_garcia', 'doctorpass',2),
    ('tech_pharma1', 'techpharmapass', 3),
    ('tech_pharma2', 'techpharmapass', 3),
    ('patient_john', 'patientpass', 1),
    ('patient_sara', 'patientpass', 1),
    ('patient_mike', 'patientpass', 1),
    ('patient_emily', 'patientpass', 1),
    ('patient_olivia', 'patientpass', 1);


-- Adding 5 entries to doctorInfo table
INSERT IGNORE INTO doctorInfo(doctorName, practiceAddr, username, usr_pwd)
VALUES 
    ('Dr. Smith', '456 Oak St', 'dr_smith', 'doctorpass'),
    ('Dr. Johnson', '789 Elm St', 'dr_johnson', 'doctorpass'),
    ('Dr. Brown', '101 Pine St', 'dr_brown', 'doctorpass'),
    ('Dr. Patel', '246 Maple St', 'dr_patel', 'doctorpass'),
    ('Dr. Garcia', '369 Cedar St', 'dr_garcia', 'doctorpass');
select * from doctorInfo;
-- Adding 5 entries to pharmacyInfo table
INSERT IGNORE INTO pharmacyInfo(pharmacyName, username, usr_pwd)
VALUES 
    ('MediCare Pharmacy', 'tech_pharma1', 'techpharmapass'),
    ('Healthy Choice Pharmacy', 'tech_pharma2', 'techpharmapass');

-- Adding 5 entries to patientInfo table
INSERT IGNORE INTO patientInfo(patientName, username, usr_pwd, doctorID, pharmacyID)
VALUES 
    ('Mike Johnson', 'patient_mike', 'patientpass', 2, 1),
    ('Sara Miller', 'patient_sara', 'patientpass', 3, 1),
    ('Emily Davis', 'patient_emily', 'patientpass', 4, 2),
    ('John Smith', 'patient_john', 'patientpass', 5, 2),
    ('Olivia White', 'patient_olivia', 'patientpass', 5, 2);

-- Adding 5 entries to medicationInfo table
INSERT IGNORE INTO medicationInfo(rxName, pharmaCompany)
VALUES 
    ('Medicine C', 'PharmaHealth'),
    ('Medicine D', 'PharmaCorp'),
    ('Medicine E', 'HealthMeds'),
    ('Medicine F', 'PharmaCo'),
    ('Medicine G', 'PharmaHealth');

-- Adding 5 entries to prescriptionInfo table
INSERT IGNORE INTO prescriptionInfo(prescriptionName, prescriptionDosage, prescriptionDate, patientID,quantity, doctorID, approved, filled)
VALUES 
    ('Medicine C', 100, '2023-03-25',2, 10, 2, true, true),
    ('Medicine D', 25, '2023-04-10',3, 10, 3, false, false),
    ('Medicine C', 60, '2023-05-15',4, 10, 4, true, false),
    ('Medicine E', 40, '2023-06-20',1, 10, 5, true, false),
    ('Medicine G', 80, '2023-07-25',1, 10, 1, false, false);
-- Adding 5 entries to Inventory table
show tables;
INSERT IGNORE INTO Inventory(rxID, rxName, quantity)
VALUES 
    (1,'Medicine C',200),
    (2,'Medicine D', 150),
    (3,'Medicine E',300),
    (4,'Medicine F',100),
    (5,'Medicine G',250);


### Breadth of SQL
## 1) Stored procedure
##   return a doctor's patient data, and only their specific patients\
## This procedure works
DELIMITER //
CREATE PROCEDURE doctorSpecificPatients(
	IN specDoctorID int
)
BEGIN
	SELECT * FROM patientInfo 
    WHERE doctorID = specDoctorID;
END//
DELIMITER ;
CALL doctorSpecificPatients(5);
select * from Inventory;
## 2) Stored procedure for a doctor to check which of their patients 
##  has a prescription that needs to be approved.
drop procedure if exists doctorSpecificPendingScripts;
DELIMITER //
CREATE PROCEDURE doctorSpecificPendingScripts( 
	IN specDoctorID int)
BEGIN
	SELECT * FROM patientinfo as pat INNER JOIN prescriptionInfo as per 
		ON pat.patientID = per.patientID 
    WHERE pat.doctorID = specDoctorID AND approved = 0;
END//
DELIMITER ;
CALL doctorSpecificPendingScripts(2);
select * from doctorInfo;
## 3) Stored procedure to approve a prescription (i.e. change approval from 0 to 1)
DELIMITER //
CREATE PROCEDURE approveScript( IN specificPrescriptionID int)
BEGIN
	UPDATE prescriptionInfo
    SET approved = 1
    WHERE prescriptionID = specificPrescriptionID;
END//
DELIMITER ;
CALL approveScript(5);
select * from prescriptionInfo;
UPDATE prescriptionInfo
    SET approved = 0
    WHERE prescriptionID = 5;
## 4) A stored procedure to remove prescriptions 
##
DELIMITER //
CREATE PROCEDURE removeScript( IN specificPrescriptionID int)
BEGIN
	DELETE FROM prescriptionInfo WHERE prescriptionID = specificPrescriptionID;
END//
DELIMITER ;
CALL removeScript(7); ##return 0 rows affected unless there are 7 values in the table.

SELECT * FROM patientinfo as pat INNER JOIN prescriptionInfo as pre on pat.patientID = pre.patientID;
## A procedure for patients to view their prescriptions
DELIMITER //
CREATE PROCEDURE patientPrescriptions( IN specificPatientID int)
BEGIN
	SELECT * FROM
    (SELECT pat.patientID, pre.prescriptionName,pre.prescriptionDosage, pre.prescriptionDate, pre.quantity, pre.approved FROM patientinfo as pat INNER JOIN prescriptionInfo as pre ON pat.patientID = pre.patientID) 
    as j
    WHERE j.patientID = specificPatientID;
END//
DELIMITER ;
CALL patientPrescriptions(1);
## VIEWS
## 1) A view for pharmacy staff to view all accepted scripts that ahven't been filled
CREATE VIEW needToBeFilled AS
SELECT * FROM prescriptionInfo
WHERE prescriptionInfo.approved = 1 AND prescriptionInfo.filled = 0;
select * from needToBeFilled;
       
CREATE VIEW patientOnlyLogin AS
SELECT * FROM userLoginInfo
WHERE userLoginInfo.personaCode = 1;
SELECT * FROM patientOnlyLogin;

CREATE VIEW doctorOnlyLogin AS
SELECT * FROM userLoginInfo
WHERE userLoginInfo.personaCode = 2;
SELECT * FROM doctorOnlyLogin;

CREATE VIEW pharmacyOnlyLogin AS
SELECT * FROM userLoginInfo
WHERE userLoginInfo.personaCode = 3;
SELECT * FROM pharmacyOnlyLogin;

## trigger to update inventory when a prescription is added
## to the prescriptionInfo table
DELIMITER //

CREATE TRIGGER updateInventory AFTER UPDATE ON prescriptionInfo
FOR EACH ROW
BEGIN
    DECLARE prescriptionQuant INT;
    
    SELECT quantity INTO prescriptionQuant FROM prescriptionInfo WHERE prescriptionID = NEW.prescriptionID;

    UPDATE Inventory
    SET quantity = quantity - prescriptionQuant
    WHERE rxID = (SELECT rxID FROM medicationInfo WHERE rxName = NEW.prescriptionName);
END;
//
DELIMITER ;

select * from Inventory;
select * FROM prescriptionInfo;
