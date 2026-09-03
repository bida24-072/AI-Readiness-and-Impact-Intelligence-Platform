-- Employee Table
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    job_function VARCHAR(100),
    department VARCHAR(100),
    seniority_level VARCHAR(20),
    hire_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Training Programs Table
CREATE TABLE training_programs (
    program_id SERIAL PRIMARY KEY,
    program_name VARCHAR(200),
    skill_category VARCHAR(100),
    program_type VARCHAR(50),
    duration_hours INTEGER,
    has_hands_on BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Training Completion Table
CREATE TABLE training_completions (
    completion_id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(employee_id),
    program_id INTEGER REFERENCES training_programs(program_id),
    completion_date DATE,
    score DECIMAL(5,2),
    time_spent_hours DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Tool Usage Table
CREATE TABLE ai_tool_usage (
    usage_id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(employee_id),
    tool_name VARCHAR(100),
    usage_date DATE,
    minutes_used INTEGER,
    tasks_completed INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Productivity Metrics Table
CREATE TABLE productivity_metrics (
    metric_id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(employee_id),
    metric_date DATE,
    efficiency_score DECIMAL(5,2),
    error_rate DECIMAL(5,2),
    client_satisfaction DECIMAL(5,2),
    utilization_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Views for Analysis
CREATE VIEW employee_training_summary AS
SELECT 
    e.employee_id,
    e.job_function,
    e.department,
    COUNT(tc.completion_id) as trainings_completed,
    AVG(tc.score) as avg_score,
    SUM(tc.time_spent_hours) as total_training_hours
FROM employees e
LEFT JOIN training_completions tc ON e.employee_id = tc.employee_id
GROUP BY e.employee_id, e.job_function, e.department;

CREATE VIEW adoption_metrics AS
SELECT 
    e.employee_id,
    COUNT(DISTINCT au.tool_name) as tools_used,
    SUM(au.minutes_used) as total_usage_minutes,
    AVG(pm.efficiency_score) as avg_efficiency
FROM employees e
LEFT JOIN ai_tool_usage au ON e.employee_id = au.employee_id
LEFT JOIN productivity_metrics pm ON e.employee_id = pm.employee_id
GROUP BY e.employee_id;