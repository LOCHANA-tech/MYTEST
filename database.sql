-- Create students table for Student Management System
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data for testing
INSERT INTO students (name, age) VALUES 
('John Doe', 20),
('Jane Smith', 22),
('Mike Johnson', 21),
('Sarah Williams', 19),
('David Brown', 23);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_students_name ON students(name);
CREATE INDEX IF NOT EXISTS idx_students_age ON students(age);
