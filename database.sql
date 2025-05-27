-- ST2-4L
-- CUSTODIO, QUEVIN JAMES A.
-- JOYOSA, EUNEL JACOB C.
-- TAMAYO, JOHANNES NIKOLAI WENDELLSOHN Z.
-- project

-- clear 'project' database if there are any to make sure
DROP DATABASE IF EXISTS student_org_db;

-- Create user & grant access 
CREATE OR REPLACE USER 'admin_user' IDENTIFIED BY 'password';
CREATE DATABASE IF NOT EXISTS student_org_db;
GRANT ALL ON student_org_db.* TO 'admin_user'@'localhost';
FLUSH PRIVILEGES;

-- use newly created database
USE student_org_db;

-- Tables ------------------------------------------------------------------------------------------------
-- Student Organization Table
CREATE TABLE IF NOT EXISTS student_org (
  org_name VARCHAR(50) PRIMARY KEY,
  username VARCHAR(25) NOT NULL,
  password VARCHAR(25) NOT NULL,
  organization_type VARCHAR(50),
  maximum_capacity INT(4)
);

-- Member Table
CREATE TABLE IF NOT EXISTS member (
  member_id INT(5) AUTO_INCREMENT PRIMARY KEY NOT NULL,
  username VARCHAR(25) NOT NULL,
  password VARCHAR(45) NOT NULL,
  gender VARCHAR(1),
  batch INT(4) NOT NULL,
  degree_program VARCHAR(10) NOT NULL, 
  date_joined DATE NOT NULL 
);

-- Relationship Table ==> student_org_member
CREATE TABLE IF NOT EXISTS student_org_member (
  org_name VARCHAR(50) NOT NULL,  -- foreign key
  member_id INT(4) NOT NULL,  -- foreign key
  role VARCHAR(15) NOT NULL, 
  status VARCHAR(10) NOT NULL, 
  is_executive INT(1) NOT NULL,
  acad_yr VARCHAR(5) NOT NULL,   -- sample: 23-24
  semester INT(1) NOT NULL,
  PRIMARY KEY (org_name, member_id, acad_yr, semester),
  CONSTRAINT student_org_member_student_org_org_name FOREIGN KEY (org_name) REFERENCES student_org(org_name),
  CONSTRAINT student_org_member_member_member_id FOREIGN KEY (member_id) REFERENCES member(member_id)
  -- CONSTRAINT student_org_member_acad_yr_uk UNIQUE(acad_yr),
  -- CONSTRAINT student_org_member_semester_uk UNIQUE(semester)
);

-- Fee Table
CREATE TABLE IF NOT EXISTS fee (
  fee_id INT(10) AUTO_INCREMENT PRIMARY KEY,
  purpose VARCHAR(20) NOT NULL,
  acad_yr VARCHAR(5) NOT NULL,
  due_date DATE NOT NULL,
  amount DECIMAL(7,2) NOT NULL,
  org_name VARCHAR(50) NOT NULL,
  CONSTRAINT fee_student_org_org_name FOREIGN KEY (org_name) REFERENCES student_org(org_name)
);

-- Relationship Table ==> MEMBER_PAYS_FEE
CREATE TABLE IF NOT EXISTS member_pays_fee (
  member_id INT(4) NOT NULL,  -- foreign key
  fee_id INT(10) NOT NULL,  -- foreign key
  status VARCHAR(10) NOT NULL, -- pending, completed
  payment_date DATE,  -- can be NULL if not paid yet
  PRIMARY KEY(member_id, fee_id),
  CONSTRAINT member_pays_fee_member_member_id FOREIGN KEY (member_id) REFERENCES member(member_id),
  CONSTRAINT member_pays_fee_fee_fee_id FOREIGN KEY (fee_id) REFERENCES fee(fee_id) 
);

-- INSERT values INTO student_org table
INSERT INTO student_org VALUES('Yellow', 'yellow_admin', 'admin', 'Academic', 200);
INSERT INTO student_org VALUES('Red', 'red_admin', 'admin', 'Non-Academic', 240);
INSERT INTO student_org VALUES('Blue', 'blue_admin', 'admin', 'Socio-cultural', 200);
INSERT INTO student_org VALUES('Green', 'green_admin', 'admin', 'Varsitarian', 200);

-- INSERT values INTO member table
INSERT INTO member -- initial insert
VALUES
  (2000, 'Juan', 'juandcruz', 'M', 2020, 'ComSci', str_to_date('07-SEP-2021','%d-%M-%Y'));

-- insert w/o member_id for auto_increment
INSERT INTO member (username, password, gender, batch, degree_program, date_joined)
VALUES
  ('Matthew', 'matt20', 'M', 2018, 'Agri', str_to_date('14-NOV-2019','%d-%M-%Y')),
  ('Mark', 'tahimiklngaq', 'M', 2023, 'Chem', str_to_date('07-MAY-2023','%d-%M-%Y')),
  ('Luke', 'luke2025', 'M', 2024, 'BioSci', str_to_date('11-JAN-2025','%d-%M-%Y')),
  ('Ester', 'ester@', 'F', 2024, 'MechEng', str_to_date('20-APR-2025','%d-%M-%Y'));

-- INSERT VALUES to fee table
INSERT INTO fee -- initial insert
VALUES
  (100, 'Org Fund', '22-23', str_to_date('20-APR-2023','%d-%M-%Y'), 300.00, 'Red');
  
-- insert w/o fee_id for auto_increment
INSERT INTO fee (purpose, acad_yr, due_date, amount, org_name)
VALUES
  ('Membership', '22-23', str_to_date('20-APR-2023','%d-%M-%Y'), 200.00, 'Yellow'),
  ('Event', '23-24', str_to_date('17-NOV-2023','%d-%M-%Y'), 50000.00, 'Blue'),
  ('Org Fund', '24-25', str_to_date('20-APR-2025','%d-%M-%Y'), 1000.00, 'Green'),
  ('Equipment', '21-22', str_to_date('14-OCT-2021','%d-%M-%Y'), 4200.00, 'Red'),
  ('Donation', '23-24', CURDATE(), 200.00, 'Blue');

-- INSERT VALUES to student_org_member
INSERT INTO student_org_member
VALUES
  ('Yellow', 2000, 'President', 'Active', 1, '24-25', 1),
  ('Yellow', 2001, 'Secretary', 'Active', 1, '24-25', 1),
  ('Blue', 2002, 'Member', 'Inactive', 0, '22-23', 2),
  ('Yellow', 2003, 'Treasurer', 'Active', 1, '24-25', 1),
  ('Green', 2004, 'Member', 'Active', 0, '22-23', 1);

-- INSERT VALUES to member_pays_fee
INSERT INTO member_pays_fee
VALUES
  (2000, 100, 'Completed', '2023-04-15'),
  (2001, 101, 'Completed', '2023-04-15'),
  (2003, 103, 'Pending', NULL),
  (2004, 104, 'Completed', '2023-11-17'),
  (2002, 102, 'Completed', NULL);

-- CRUD OPERATIONS
-- SELECT tables to view all rows and columns
SELECT * FROM student_org;
SELECT * FROM member;
SELECT * FROM student_org_member;
SELECT * FROM fee;
SELECT * FROM member_pays_fee;

-- UPDATE Operations
START TRANSACTION;

UPDATE member_pays_fee
SET status = 'Completed', payment_date = CURDATE()
WHERE member_id = 2003 AND fee_id = 103;
SAVEPOINT update_fee_103;

SELECT * FROM member_pays_fee; -- view table upate

UPDATE student_org_member
SET role = "Member", is_executive = 0
WHERE member_id = 2003;

SELECT * FROM student_org_member; -- view table update


-- DELETE Operations
DELETE FROM fee
WHERE fee_id = 105;

SELECT * FROM fee; -- view table update

-- ROLLBACK changes
-- ROLLBACK; -- optional

-- CORE FUNCTIONALITYIES ----------------------------------------------------------------------------------------

--------- MEMBERSHIP MANAGEMENT ---------------------------------------------------------------------------------

-- 1 ADD MEMBER
INSERT INTO member (username, password, gender, batch, degree_program, date_joined)
VALUES ('Quevin', 'quevin26', 'M', 2023, 'BSCS', str_to_date('26-JUN-2023','%d-%M-%Y'));

-- 2 UPDATE MEMBER USING MEMBER ID
UPDATE member SET username = "Kevin", gender = "F", batch = 2022, degree_program = "BCIT", date_joined = str_to_date('21-JUN-2023','%d-%M-%Y') WHERE member_id = 2005;

-- 3 DELETE MEMBER USING MEMBER ID
DELETE FROM member WHERE member_id = 2005;

-- 4 SEARCH FOR ALL MEMBER NAMES
SELECT username FROM member;

-- 4 SEARCH FOR ALL MEMBER NAMES AND DETAILS
SELECT * FROM member;

-- 4 SEARCH FOR ONE MEMBER AND ALL DETAILS USING MEMBER ID
SELECT * FROM member WHERE member_id = 2003;

-- 5 


--------- REPORTS TO BE GENERATED ---------------------------------------------------------------------------------

-- 1 
SELECT member_id, username, role, status, gender, batch, degree_program, is_executive FROM student_org_member JOIN member USING(member_id) WHERE org_name = "Yellow";

-- 2
SELECT member_id, fee_id, mem.org_name, username, pays.status, purpose, amount, fee.acad_yr, due_date FROM member JOIN member_pays_fee pays USING(member_id) JOIN fee USING(fee_id) JOIN student_org_member mem USING(member_id) WHERE mem.org_name = "Blue" AND pays.status = "Unpaid";

-- 3
SELECT * FROM student_org_member JOIN member_pays_fee USING(member_id) WHERE org_name = "Yellow" AND member_id = 2000 AND member_pays_fee.status = "Unpaid";

-- 4
SELECT * FROM student_org_member WHERE role != "Member" AND acad_yr = "24-25" AND org_name = "Yellow";

-- 5 
SELECT * FROM student_org_member WHERE role != "Member" AND org_name = "Yellow" ORDER BY acad_yr desc;

-- 6
SELECT * FROM member_pays_fee JOIN fee USING(fee_id) JOIN student_org_member USING(member_id) WHERE payment_date > due_date AND student_org_member.org_name = "Green" AND student_org_member.acad_yr = "22-23" AND semester = 1;

-- 7
SELECT org_name, member_id, role, status, acad_yr, semester, (COUNT(CASE WHEN status = 'Active' THEN 1 END) * 1.0 /COUNT(member_id)) * 100.0 AS "Active Member Percetage" FROM student_org_member WHERE org_name = 'Yellow' AND acad_yr = "24-25" AND semester = 1 GROUP BY org_name, acad_yr, semester;

-- 8 


-- 9 
SELECT member_id, fee_id, member_pays_fee.status, amount, student_org_member.org_name, SUM(amount) FROM member_pays_fee JOIN fee USING(fee_id) JOIN student_org_member USING (member_id) GROUP BY status;
SELECT member_id, fee_id, member_pays_fee.status, amount, student_org_member.org_name, SUM(amount) FROM member_pays_fee JOIN fee USING(fee_id) JOIN student_org_member USING (member_id) WHERE student_org_member.org_name = "blue" GROUP BY status; --Wala pang date

-- 10
SELECT member_id, student_org_member.org_name, username, fee_id, purpose, amount, due_date, student_org_member.acad_yr, semester FROM member JOIN member_pays_fee USING(member_id) JOIN student_org_member USING(member_id) JOIN fee USING(fee_id) WHERE member_pays_fee.status = "Unpaid" AND student_org_member.org_name = "Blue" AND student_org_member.acad_yr = "22-23" AND semester = 2 ORDER BY amount DESC;