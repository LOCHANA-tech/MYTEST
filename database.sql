-- Student Management System Database Schema
-- This SQL script creates the necessary tables and inserts initial data for the student management system

-- Create students table
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 1 AND age <= 120),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_students_name ON students(name);
CREATE INDEX IF NOT EXISTS idx_students_age ON students(age);

-- Insert sample data
INSERT INTO students (name, age) VALUES 
    ('John Doe', 20),
    ('Jane Smith', 22),
    ('Mike Johnson', 21),
    ('Sarah Williams', 19),
    ('David Brown', 23),
    ('Emily Davis', 20),
    ('Chris Wilson', 24),
    ('Amanda Miller', 21),
    ('James Taylor', 22),
    ('Lisa Anderson', 20)
ON CONFLICT DO NOTHING;

-- Create trigger for updating updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to students table
DROP TRIGGER IF EXISTS update_students_updated_at ON students;
CREATE TRIGGER update_students_updated_at
    BEFORE UPDATE ON students
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for student statistics
CREATE OR REPLACE VIEW student_stats AS
SELECT 
    COUNT(*) as total_students,
    AVG(age) as average_age,
    MIN(age) as youngest_age,
    MAX(age) as oldest_age
FROM students;

-- Grant permissions (adjust as needed for your Supabase setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO anon;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO anon;

-- Comments for documentation
COMMENT ON TABLE students IS 'Stores student information including name and age';
COMMENT ON COLUMN students.id IS 'Unique identifier for each student';
COMMENT ON COLUMN students.name IS 'Full name of the student';
COMMENT ON COLUMN students.age IS 'Age of the student in years';
COMMENT ON COLUMN students.created_at IS 'Timestamp when the student record was created';
COMMENT ON COLUMN students.updated_at IS 'Timestamp when the student record was last updated';

-- Optional: Create a function to validate student data
CREATE OR REPLACE FUNCTION validate_student_data(p_name VARCHAR, p_age INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if name is not empty and age is within valid range
    IF p_name IS NULL OR LENGTH(TRIM(p_name)) = 0 THEN
        RETURN FALSE;
    END IF;
    
    IF p_age IS NULL OR p_age < 1 OR p_age > 120 THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ language 'plpgsql';

-- Optional: Create a trigger function for data validation
CREATE OR REPLACE FUNCTION validate_student_before_insert()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT validate_student_data(NEW.name, NEW.age) THEN
        RAISE EXCEPTION 'Invalid student data: name cannot be empty and age must be between 1 and 120';
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply validation trigger
DROP TRIGGER IF EXISTS validate_student_insert ON students;
CREATE TRIGGER validate_student_insert
    BEFORE INSERT ON students
    FOR EACH ROW
    EXECUTE FUNCTION validate_student_before_insert();

-- Apply validation trigger for updates as well
DROP TRIGGER IF EXISTS validate_student_update ON students;
CREATE TRIGGER validate_student_update
    BEFORE UPDATE ON students
    FOR EACH ROW
    EXECUTE FUNCTION validate_student_before_insert();
