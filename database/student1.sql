ALTER TABLE student_login
DROP FOREIGN KEY fk_login_student;

ALTER TABLE student_detail
MODIFY COLUMN student_id VARCHAR(20) NOT NULL;

ALTER TABLE student_login
MODIFY COLUMN student_id VARCHAR(20) NOT NULL;

ALTER TABLE student_login
ADD CONSTRAINT fk_login_student
FOREIGN KEY (student_id) REFERENCES student_detail(student_id);

desc student_detail;

select * from student_detail;

select * from student_admission;