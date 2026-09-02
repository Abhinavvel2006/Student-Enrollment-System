create database college_project_2;
use college_project_2;

-- creating tables
create table admin(
admin_username varchar(50) not null unique,
admin_password varchar(255) not null
);

desc admin;

create table department(
department_id int primary key,
department_name varchar(100) not null,
course_count int not null,
staff_count int not null,
student_count int not null
);

desc department;

create table student_admission(
application_id int auto_increment primary key,
student_name varchar(100) not null,
dob date,
gender varchar(20) not null,
department_id int,
email varchar(100) not null,
phone varchar(15) not null,
address text,
status varchar(20) not null,
submitted_at datetime,
constraint fk_student_department
foreign key(department_id)
references department(department_id)
);

desc student_admission;

create table student_detail(
student_id int primary key,
application_id int,
student_name varchar(100) not null,
dob date,
gender varchar(20) not null,
department_id int,
email varchar(20) not null,
phone varchar(15) not null,
address text,
status varchar(20) not null,
joined_at datetime,
constraint fk_student_application
foreign key (application_id)
references student_admission(application_id),
constraint fk_detail_department
foreign key(department_id)
references department(department_id)
);

desc student_detail;

create table student_login(
student_id int primary key,
username varchar(50) not null,
dob date,
student_password varchar(255) not null,
is_active bool,
constraint fk_login_student
foreign key(student_id)
references student_detail(student_id)
);

desc student_login;

ALTER TABLE student_detail
MODIFY email VARCHAR(100) NOT NULL;

desc student_detail;

ALTER TABLE student_login
ADD CONSTRAINT uq_student_username UNIQUE (username);

desc student_login;

ALTER TABLE student_detail
ADD CONSTRAINT uq_student_application UNIQUE (application_id);

desc student_detail;
select * from department;
select * from student_admission;
desc department;

INSERT INTO department
(department_id, department_name)
VALUES
(1, 'BCA'),
(2, 'B.Sc Computer Science'),
(3, 'B.Com'),
(4, 'B.Sc Physics'),
(5, 'B.Sc Chemistry');

select * from department;
select * from student_admission;
use student_admission;
use college_project_2;
select * from student_admission;

update student_admission
set submitted_at = current_timestamp
where submitted_at is null;

UPDATE student_admission
SET submitted_at = CURRENT_TIMESTAMP
WHERE submitted_at IS NULL
AND application_id > 0;

select * from student_admission;
ALTER TABLE student_admission
MODIFY submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;

select * from student_admission;

-- admin username and password
desc admin;
insert into admin
(admin_username, admin_password) values
('admin@123', 'admin12345678');

select * from admin;

use college_project_2;
select * from student_admission;

delete from student_admission
where application_id = 7;

use college_project_2;
show tables;

drop table department;

set foreign_key_checks = 0;
drop table department;
set foreign_key_checks = 1;
create table department
(
department_id int primary key,
department_name varchar(100)
);
desc department;

INSERT INTO department
(department_id, department_name)
VALUES
(1, 'BCA'),
(2, 'B.Sc Computer Science'),
(3, 'B.Com'),
(4, 'B.Sc Physics'),
(5, 'B.Sc Chemistry');
select * from department;

select * from student_admission;

use college_project_2;
show tables;
desc student_detail;
alter table student_detail add department_name varchar(100) not null;
desc student_detail;

select * from student_detail;
desc department;

alter table student_detail add class_no int not null;

-- One-time migration: student IDs use the scc0001 text format.
ALTER TABLE student_login DROP FOREIGN KEY fk_login_student;
ALTER TABLE student_detail MODIFY student_id VARCHAR(20) NOT NULL;
ALTER TABLE student_login MODIFY student_id VARCHAR(20) NOT NULL;
ALTER TABLE student_login
ADD CONSTRAINT fk_login_student
FOREIGN KEY (student_id) REFERENCES student_detail(student_id);

desc student_login;

select * from student_detail;

select database();

desc student_detail;