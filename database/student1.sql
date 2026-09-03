ALTER TABLE student_login
DROP FOREIGN KEY fk_login_student;

ALTER TABLE student_detail
MODIFY COLUMN student_id VARCHAR(20) NOT NULL;

ALTER TABLE student_login
MODIFY COLUMN student_id VARCHAR(20) NOT NULL;

ALTER TABLE student_login
ADD CONSTRAINT fk_login_student
FOREIGN KEY (student_id) REFERENCES student_detail(student_id);

-- One-time migration for databases created before the joined_at field existed.
ALTER TABLE student_detail
ADD COLUMN joined_at DATETIME NULL;

UPDATE student_detail sd
LEFT JOIN student_admission sa ON sa.application_id = sd.application_id
SET sd.joined_at = COALESCE(sa.submitted_at, CURRENT_TIMESTAMP)
WHERE sd.joined_at IS NULL;

desc student_detail;

select * from student_detail;

select * from student_admission;

use college_project_2;
select * from student_detail;
