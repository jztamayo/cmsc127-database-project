-- ST2-4L
-- CUSTODIO, QUEVIN JAMES A.
-- JOYOSA, EUNEL JACOB C.
-- TAMAYO, JOHANNES NIKOLAI WENDELLSOHN Z.
-- project

-- clear 'student_org_db' database if there are any to make sure
DROP DATABASE IF EXISTS student_org_db;

-- Create user & grant access 
CREATE OR REPLACE USER 'admin_user'@'localhost' IDENTIFIED BY 'ilove127';
CREATE DATABASE IF NOT EXISTS student_org_db;
GRANT ALL PRIVILEGES ON student_org_db.* TO 'admin_user'@'localhost';
FLUSH PRIVILEGES;

-- use newly created database to insert tables and values
-- Use the database
USE student_org_db;

-- Tables ------------------------------------------------------------------------------------------------
-- Student Organization Table
CREATE TABLE IF NOT EXISTS student_org (
  org_name VARCHAR(50) PRIMARY KEY,
  username VARCHAR(25) NOT NULL, -- unique username for each organization admin
  password VARCHAR(25) NOT NULL, -- password for each organization admin
  organization_type VARCHAR(50), -- e.g. Academic, Non-Academic
  maximum_capacity INT(4) -- maximum number of members allowed in the organization
);

-- Member Table
CREATE TABLE IF NOT EXISTS member (
  member_id INT(5) AUTO_INCREMENT PRIMARY KEY NOT NULL,
  username VARCHAR(25) NOT NULL, -- unique username for each member
  password VARCHAR(45) NOT NULL, -- password for each member
  gender VARCHAR(1),
  batch INT(4) NOT NULL, -- e.g. 2023, 2024
  degree_program VARCHAR(10) NOT NULL,  -- e.g. ComSci, Stat, ChemEng, MechEng, Agri
  date_joined DATE NOT NULL -- date when the member joined the organization
);

-- Relationship Table ==> student_org_member
CREATE TABLE IF NOT EXISTS student_org_member (
  org_name VARCHAR(50) NOT NULL,  -- foreign key
  member_id INT(4) NOT NULL,  -- foreign key
  role VARCHAR(15) NOT NULL,  -- e.g. President, Vice President, Secretary, Treasurer, Member
  status VARCHAR(10) NOT NULL -- e.g. Active, Inactive, Expelled, Suspended, Alumni
  CHECK (status IN ('Active', 'Inactive', 'Expelled', 'Suspended', 'Alumni')), -- uncomment if want to restrict status values
  is_executive INT(1) NOT NULL,  -- 1 for executive, 0 for non-executive
  acad_yr VARCHAR(5) NOT NULL,   -- sample: 23-24
  semester INT(1) NOT NULL,      -- 1 for first sem, 2 for second sem
  PRIMARY KEY (org_name, member_id, acad_yr, semester),
  CONSTRAINT student_org_member_student_org_org_name FOREIGN KEY (org_name) REFERENCES student_org(org_name),
  CONSTRAINT student_org_member_member_member_id FOREIGN KEY (member_id) REFERENCES member(member_id)
);

-- Fee Table
CREATE TABLE IF NOT EXISTS fee (
  fee_id INT(10) AUTO_INCREMENT PRIMARY KEY,
  purpose VARCHAR(20) NOT NULL, -- e.g. Annual Dues, Membership, Event Fee, Equipment, Leadership Training, Executive Dues, Donation
  acad_yr VARCHAR(5) NOT NULL, -- sample: 24-25
  due_date DATE, -- can be NULL if no due date (e.g. for donations)
  amount DECIMAL(7,2) NOT NULL, -- amount in PHP
  org_name VARCHAR(50) NOT NULL, -- foreign key
  CONSTRAINT fee_student_org_org_name FOREIGN KEY (org_name) REFERENCES student_org(org_name)
);

-- Relationship Table ==> MEMBER_PAYS_FEE
CREATE TABLE IF NOT EXISTS member_pays_fee (
  member_id INT(4) NOT NULL,  -- foreign key
  fee_id INT(10) NOT NULL,  -- foreign key
  status VARCHAR(10) NOT NULL, -- Unpaid OR Completed
  payment_date DATE,  -- can be NULL if not paid yet
  PRIMARY KEY(member_id, fee_id),
  CONSTRAINT member_pays_fee_member_member_id FOREIGN KEY (member_id) REFERENCES member(member_id),
  CONSTRAINT member_pays_fee_fee_fee_id FOREIGN KEY (fee_id) REFERENCES fee(fee_id) 
);

--------- INSERTING VALUES ON TABLES  ---------------------------------------------------------------------------------

-- make 2 organizations
INSERT INTO student_org VALUES('Yellow', 'yellow_admin', 'admin', 'Academic', 200);
INSERT INTO student_org VALUES('Red', 'red_admin', 'admin', 'Non-Academic', 240);

--------- INSERTING INTO YELLOW ORG  ---------------------------------------------------------------------------------

-- MEMBERS
INSERT INTO member VALUES
  (2000, 'Juan', 'juandcruz', 'M', 2017, 'ComSci', str_to_date('15-AUG-2017','%d-%b-%Y')),   -- Alumni
  (2001, 'Matthew', 'matt20', 'M', 2016, 'Agri', str_to_date('20-AUG-2016','%d-%b-%Y')),     -- Alumni
  (2002, 'Mark', 'tahimiklngaq', 'M', 2022, 'ChemEng', str_to_date('01-SEP-2022','%d-%b-%Y')), -- Exec Secretary
  (2003, 'Luke', 'luke2025', 'M', 2023, 'MechEng', str_to_date('10-AUG-2023','%d-%b-%Y')),   -- Member
  (2004, 'Ester', 'ester@', 'F', 2023, 'MechEng', str_to_date('10-AUG-2023','%d-%b-%Y')),    -- Member
  (2005, 'Mary', 'm4ry', 'F', 2022, 'Stat', str_to_date('01-SEP-2022','%d-%b-%Y')),          -- Exec VicePres (Stat, F)
  (2006, 'John', 'johnnn', 'M', 2021, 'ComSci', str_to_date('15-AUG-2021','%d-%b-%Y')),      -- Exec Pres (ComSci, M)
  (2007, 'Paul', 'paul254', 'M', 2021, 'Stat', str_to_date('15-AUG-2021','%d-%b-%Y')),       -- Inactive
  (2008, 'Anna', 'anna2022', 'F', 2022, 'ChemEng', str_to_date('01-SEP-2022','%d-%b-%Y')),   -- Exec Treasurer (ChemEng, F)
  (2009, 'James', 'james@12', 'M', 2015, 'Agri', str_to_date('20-AUG-2015','%d-%b-%Y'));     -- Alumni

-- STUDENT_ORG_MEMBER
INSERT INTO student_org_member VALUES
  ('Yellow', 2006, 'President', 'Active', 1, '24-25', 1),      -- ComSci, M, sem 1
  ('Yellow', 2005, 'Vice President', 'Active', 1, '24-25', 2), -- Stat, F, sem 2
  ('Yellow', 2002, 'Secretary', 'Active', 1, '23-24', 2),      -- ChemEng, M, sem 2
  ('Yellow', 2008, 'Treasurer', 'Active', 1, '23-24', 1),      -- ChemEng, F, sem 1
  ('Yellow', 2000, 'Member', 'Alumni', 0, '19-20', 2),         -- ComSci, M, sem 2
  ('Yellow', 2001, 'Member', 'Alumni', 0, '18-19', 1),         -- Agri, M, sem 1
  ('Yellow', 2009, 'Member', 'Alumni', 0, '18-19', 2),         -- Agri, M, sem 2
  ('Yellow', 2003, 'Member', 'Active', 0, '24-25', 2),         -- MechEng, M, sem 2
  ('Yellow', 2004, 'Member', 'Active', 0, '23-24', 1),         -- MechEng, F, sem 1
  ('Yellow', 2007, 'Member', 'Inactive', 0, '22-23', 2);       -- Stat, M, sem 2

-- INSERT VALUES to fee table
INSERT INTO fee VALUES
  (201, 'Annual Dues', '24-25', str_to_date('15-JUL-2024','%d-%M-%Y'), 3500.00, 'Yellow'),           
  (202, 'Membership', '24-25', str_to_date('01-AUG-2024','%d-%M-%Y'), 300.00, 'Yellow'),             
  (203, 'Event Fee', '24-25', str_to_date('10-DEC-2024','%d-%M-%Y'), 800.00, 'Yellow'),              
  (204, 'Equipment', '24-25', str_to_date('15-FEB-2025','%d-%M-%Y'), 2500.00, 'Yellow'),             
  (205, 'Leadership Training', '24-25', str_to_date('20-JAN-2025','%d-%M-%Y'), 1200.00, 'Yellow'),   
  (206, 'Executive Dues', '24-25', str_to_date('01-MAR-2025','%d-%M-%Y'), 1500.00, 'Yellow'),        
  (207, 'Donation', '24-25', NULL, 5000.00, 'Yellow'),                                               

  (208, 'Annual Dues', '23-24', str_to_date('17-JUL-2023','%d-%M-%Y'), 3400.00, 'Yellow'),
  (209, 'Membership', '23-24', str_to_date('05-AUG-2023','%d-%M-%Y'), 300.00, 'Yellow'),
  (210, 'Event Fee', '23-24', str_to_date('12-NOV-2023','%d-%M-%Y'), 900.00, 'Yellow'),
  (211, 'Equipment', '23-24', str_to_date('20-FEB-2024','%d-%M-%Y'), 2300.00, 'Yellow'),
  (212, 'Leadership Training', '23-24', str_to_date('18-JAN-2024','%d-%M-%Y'), 1100.00, 'Yellow'),
  (213, 'Executive Dues', '23-24', str_to_date('05-MAR-2024','%d-%M-%Y'), 2100.00, 'Yellow'),

  (214, 'Alumni Fund', '19-20', str_to_date('30-SEP-2019','%d-%M-%Y'), 1000.00, 'Yellow'),
  (215, 'Alumni Homecoming', '19-20', str_to_date('15-DEC-2019','%d-%M-%Y'), 500.00, 'Yellow');
  
-- INSERT VALUES to member_pays_fee
-- 2006: John, President, Active, exec, '24-25'
INSERT INTO member_pays_fee VALUES
  (2006, 201, 'Completed', '2024-07-14'), -- Annual Dues, paid on time
  (2006, 202, 'Completed', '2024-08-01'), -- Membership, paid on time
  (2006, 203, 'Unpaid', NULL),            -- Event Fee, not yet paid
  (2006, 204, 'Completed', '2025-02-16'), -- Equipment, paid late
  (2006, 205, 'Completed', '2025-01-19'), -- Leadership Training, paid late
  (2006, 206, 'Unpaid', NULL);            -- Executive Dues, not yet paid

-- 2005: Mary, Vice President, Active, exec, '24-25'
INSERT INTO member_pays_fee VALUES
  (2005, 201, 'Completed', '2024-07-15'),
  (2005, 202, 'Completed', '2024-08-02'),
  (2005, 203, 'Completed', '2024-12-09'), -- paid on time
  (2005, 204, 'Unpaid', NULL),
  (2005, 205, 'Completed', '2025-01-25'), -- paid late
  (2005, 206, 'Completed', '2025-03-01'); -- paid on time

-- 2002: Mark, Secretary, Active, exec, '23-24'
INSERT INTO member_pays_fee VALUES
  (2002, 208, 'Completed', '2023-07-18'),
  (2002, 209, 'Completed', '2023-08-05'),
  (2002, 210, 'Completed', '2023-11-13'),
  (2002, 211, 'Unpaid', NULL),
  (2002, 212, 'Completed', '2024-01-20'),
  (2002, 213, 'Unpaid', NULL);

-- 2008: Anna, Treasurer, Active, exec, '23-24'
INSERT INTO member_pays_fee VALUES
  (2008, 208, 'Completed', '2023-07-17'),
  (2008, 209, 'Completed', '2023-08-06'),
  (2008, 210, 'Unpaid', NULL),
  (2008, 211, 'Completed', '2024-02-20'), -- paid late
  (2008, 212, 'Completed', '2024-01-18'),
  (2008, 213, 'Completed', '2024-03-06'); -- paid late

-- 2003: Luke, Member, Active, '24-25'
INSERT INTO member_pays_fee VALUES
  (2003, 201, 'Unpaid', NULL),
  (2003, 202, 'Completed', '2024-08-03'),
  (2003, 203, 'Completed', '2024-12-10'),
  (2003, 204, 'Unpaid', NULL);

-- 2004: Ester, Member, Active, '23-24'
INSERT INTO member_pays_fee VALUES
  (2004, 208, 'Completed', '2023-07-19'),
  (2004, 209, 'Unpaid', NULL),
  (2004, 210, 'Completed', '2023-11-12'),
  (2004, 211, 'Completed', '2024-02-21');

-- 2007: Paul, Member, Inactive, '22-23'
INSERT INTO member_pays_fee VALUES
  (2007, 210, 'Unpaid', NULL);            -- Event Fee (23-24), not paid

-- 2000: Juan, Member, Alumni, '19-20'
INSERT INTO member_pays_fee VALUES
  (2000, 214, 'Completed', '2019-09-25'), -- Alumni Fund, paid
  (2000, 215, 'Unpaid', NULL);            -- Homecoming, not paid

-- 2001: Matthew, Member, Alumni, '18-19'
INSERT INTO member_pays_fee VALUES
  (2001, 207, 'Completed', '2023-11-10'); -- Donation

-- 2009: James, Member, Alumni, '18-19'
INSERT INTO member_pays_fee VALUES
  (2009, 214, 'Unpaid', NULL);  -- Alumni Fund, not paid

-- --------- INSERTING INTO RED ORG  ---------------------------------------------------------------------------------

-- -- INSERT values INTO member table (For Red Org)
-- INSERT INTO member
-- VALUES
--   (3000, 'Matthew', 'matt20', 'M', 2020, 'Stat', str_to_date('14-NOV-2019','%d-%M-%Y'));

-- -- insert w/o member_id for auto_increment
-- INSERT INTO member (username, password, gender, batch, degree_program, date_joined)
-- VALUES
--   -- for Yellow
--   ('Aiden', 'aidenpw', 'M', 2018, 'Agri', str_to_date('14-NOV-2019','%d-%M-%Y')),
--   ('Sophia', 'sophiapw', 'F', 2023, 'ChemEng', str_to_date('07-MAY-2024','%d-%M-%Y')),
--   ('Liam', 'liampw', 'M', 2024, 'MechEng', str_to_date('11-NOV-2024','%d-%M-%Y')),
--   ('Olivia', 'oliviapw', 'F', 2024, 'MechEng', str_to_date('20-MAR-2025','%d-%M-%Y')),
--   ('Noah', 'noahpw', 'M', 2023, 'ComSci', str_to_date('20-NOV-2023','%d-%M-%Y')),
--   ('Emma', 'emmapw', 'F', 2022, 'Stat', str_to_date('26-MAR-2023','%d-%M-%Y')),
--   ('Lucas', 'lucaspw', 'M', 2020, 'Stat', str_to_date('20-APR-2021','%d-%M-%Y')),
--   ('Mia', 'miapw', 'F', 2013, 'ChemEng', str_to_date('20-APR-2014','%d-%M-%Y')),
--   ('Ethan', 'ethanpw', 'M', 2015, 'Agri', str_to_date('16-MAR-2016','%d-%M-%Y'));

-- -- INSERT VALUES to fee table
-- INSERT INTO fee -- initial insert
-- VALUES
--   (100, 'Org Fund', '22-23', str_to_date('20-APR-2023','%d-%M-%Y'), 300.00, 'Red');
  
-- -- insert w/o fee_id for auto_increment
-- INSERT INTO fee (purpose, acad_yr, due_date, amount, org_name)
-- VALUES
--   ('Membership', '22-23', str_to_date('20-APR-2023','%d-%M-%Y'), 200.00, 'Yellow'),
--   ('Event', '23-24', str_to_date('17-NOV-2023','%d-%M-%Y'), 50000.00, 'Blue'),
--   ('Org Fund', '24-25', str_to_date('20-APR-2025','%d-%M-%Y'), 1000.00, 'Green'),
--   ('Equipment', '21-22', str_to_date('14-OCT-2021','%d-%M-%Y'), 4200.00, 'Red'),
--   ('Donation', '23-24', CURDATE(), 200.00, 'Blue'),
--   ('Membership', '24-25', str_to_date('20-APR-2025','%d-%M-%Y'), 300.00, 'Yellow'),
--   ('Event', '22-23', str_to_date('17-NOV-2022','%d-%M-%Y'), 50000.00, 'Green'),
--   ('Org Fund', '23-24', str_to_date('20-APR-2024','%d-%M-%Y'), 1000.00, 'Red'),
--   ('Equipment', '22-23', str_to_date('14-OCT-2022','%d-%M-%Y'), 4200.00, 'Blue'),
--   ('Donation', '24-25', CURDATE(), 200.00, 'Green');  

-- -- INSERT VALUES to student_org_member
-- INSERT INTO student_org_member
-- VALUES
--   ('Yellow', 2000, 'President', 'Active', 1, '24-25', 1),
--   ('Yellow', 2001, 'Secretary', 'Active', 1, '24-25', 1),
--   ('Blue', 2002, 'Member', 'Inactive', 0, '22-23', 2),
--   ('Yellow', 2003, 'Treasurer', 'Active', 1, '24-25', 1),
--   ('Green', 2004, 'Member', 'Active', 0, '22-23', 1),
--   ('Red', 2005, 'Member', 'Active', 0, '22-23', 1),
--   ('Blue', 2006, 'Member', 'Active', 0, '22-23', 1),
--   ('Yellow', 2007, 'Member', 'Active', 0, '24-25', 1),
--   ('Red', 2008, 'Member', 'Active', 0, '24-25', 1),
--   ('Green', 2009, 'Member', 'Active', 0, '24-25', 1);

-- -- INSERT VALUES to member_pays_fee
-- INSERT INTO member_pays_fee
-- VALUES
--   (2000, 100, 'Completed', '2023-04-15'),
--   (2001, 101, 'Completed', '2023-04-15'),
--   (2003, 103, 'Unpaid', NULL),
--   (2004, 104, 'Completed', '2023-11-17'),
--   (2002, 102, 'Completed', NULL);

-- -- CRUD OPERATIONS
-- SELECT tables to view all rows and columns
SELECT * FROM student_org;
SELECT * FROM member;
SELECT * FROM student_org_member;
SELECT * FROM fee;
SELECT * FROM member_pays_fee;

-- -- UPDATE Operations
-- START TRANSACTION;

-- UPDATE member_pays_fee
-- SET status = 'Completed', payment_date = CURDATE()
-- WHERE member_id = 2003 AND fee_id = 103;
-- SAVEPOINT update_fee_103;

-- SELECT * FROM member_pays_fee; -- view table upate

-- UPDATE student_org_member
-- SET role = "Member", is_executive = 0
-- WHERE member_id = 2003;

-- SELECT * FROM student_org_member; -- view table update


-- -- DELETE Operations
-- DELETE FROM fee
-- WHERE fee_id = 105;

-- SELECT * FROM fee; -- view table update

-- -- ROLLBACK changes
-- -- ROLLBACK; -- optional

-- -- CORE FUNCTIONALITIES ----------------------------------------------------------------------------------------

-- --------- MEMBERSHIP MANAGEMENT ---------------------------------------------------------------------------------

-- -- 1 ADD MEMBER
-- INSERT INTO member (username, password, gender, batch, degree_program, date_joined)
-- VALUES ('Quevin', 'quevin26', 'M', 2023, 'BSCS', str_to_date('26-JUN-2023','%d-%M-%Y'));

-- -- 2 UPDATE MEMBER USING MEMBER ID
-- UPDATE member SET username = "Kevin", gender = "F", batch = 2022, degree_program = "BCIT", date_joined = str_to_date('21-JUN-2023','%d-%M-%Y') WHERE member_id = 2005;

-- -- 3 DELETE MEMBER USING MEMBER ID
-- DELETE FROM member WHERE member_id = 2005;

-- -- 4 SEARCH FOR ALL MEMBER NAMES
-- SELECT username FROM member;

-- -- 4 SEARCH FOR ALL MEMBER NAMES AND DETAILS
-- SELECT * FROM member;

-- -- 4 SEARCH FOR ONE MEMBER AND ALL DETAILS USING MEMBER ID
-- SELECT * FROM member WHERE member_id = 2003;

-- -- 5 


--------- REPORTS TO BE GENERATED ---------------------------------------------------------------------------------

-- 1 
SELECT member_id, username, role, status, gender, batch, degree_program, is_executive FROM student_org_member JOIN member USING(member_id) WHERE org_name = "Yellow";

-- 2
SELECT member_id, fee_id, mem.org_name, username, pays.status, purpose, amount, fee.acad_yr, due_date FROM member JOIN member_pays_fee pays USING(member_id) JOIN fee USING(fee_id) JOIN student_org_member mem USING(member_id) WHERE mem.org_name = "Yellow" AND pays.status = "Unpaid";

-- 3
SELECT * FROM student_org_member JOIN member_pays_fee USING(member_id) WHERE org_name = "Yellow" AND member_id = 2006 AND member_pays_fee.status = "Unpaid";

-- 4
SELECT * FROM student_org_member WHERE role != "Member" AND acad_yr = "24-25" AND org_name = "Yellow";

-- 5 
SELECT * FROM student_org_member WHERE role != "Member" AND org_name = "Yellow" ORDER BY acad_yr desc;

-- 6
SELECT * FROM member_pays_fee JOIN fee USING(fee_id) JOIN student_org_member USING(member_id) WHERE payment_date > due_date AND student_org_member.org_name = "Yellow" AND student_org_member.acad_yr = "23-24" AND semester = 1;

-- 7
SELECT org_name, member_id, role, status, acad_yr, semester, (COUNT(CASE WHEN status = 'Active' THEN 1 END) * 1.0 /COUNT(member_id)) * 100.0 AS "Active Member Percetage" FROM student_org_member WHERE org_name = 'Yellow' AND acad_yr = "24-25" AND semester = 1 GROUP BY org_name, acad_yr, semester;

-- 8 

-- 9
SELECT member_pays_fee.status, SUM(fee.amount) AS total_amount
FROM member_pays_fee
  JOIN fee ON member_pays_fee.fee_id = fee.fee_id
  JOIN student_org_member ON member_pays_fee.member_id = student_org_member.member_id
WHERE 
  student_org_member.org_name = 'Yellow'
  AND (fee.due_date IS NULL OR fee.due_date <= '2024-12-31') -- as of this date
GROUP BY 
  member_pays_fee.status;

-- 10
SELECT member_id, student_org_member.org_name, username, fee_id, purpose, amount, due_date, student_org_member.acad_yr, semester FROM member JOIN member_pays_fee USING(member_id) JOIN student_org_member USING(member_id) JOIN fee USING(fee_id) WHERE member_pays_fee.status = "Unpaid" AND student_org_member.org_name = "Blue" AND student_org_member.acad_yr = "22-23" AND semester = 2 ORDER BY amount DESC;