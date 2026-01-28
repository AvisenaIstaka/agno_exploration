-- <query name>average_salary_by_department</query name>
-- <query description>
-- Calculate average current salary by department.
-- Handles: Latest salary using MAX(effective_date) subquery
-- </query description>
-- <query>
SELECT
    d.department_name,
    COUNT(e.employee_id) AS employee_count,
    ROUND(AVG(sh.salary_amount), 2) AS avg_salary,
    MIN(sh.salary_amount) AS min_salary,
    MAX(sh.salary_amount) AS max_salary
FROM departments d
JOIN employees e ON d.department_id = e.department_id
JOIN salary_history sh ON e.employee_id = sh.employee_id
WHERE e.employment_status = 'Active'
    AND sh.effective_date = (
        SELECT MAX(sh2.effective_date)
        FROM salary_history sh2
        WHERE sh2.employee_id = e.employee_id
    )
GROUP BY d.department_name
ORDER BY avg_salary DESC
-- </query>


-- <query name>top_performers_recent_review</query name>
-- <query description>
-- Find employees with highest performance ratings in latest review.
-- Handles: Rating as DECIMAL(3,2), latest review date per employee
-- </query description>
-- <query>
SELECT
    e.first_name,
    e.last_name,
    d.department_name,
    jp.position_title,
    pr.overall_rating,
    pr.review_date
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN job_positions jp ON e.position_id = jp.position_id
JOIN performance_reviews pr ON e.employee_id = pr.employee_id
WHERE e.employment_status = 'Active'
    AND pr.review_date = (
        SELECT MAX(pr2.review_date)
        FROM performance_reviews pr2
        WHERE pr2.employee_id = e.employee_id
    )
    AND pr.overall_rating >= 4.0
ORDER BY pr.overall_rating DESC, pr.review_date DESC
LIMIT 50
-- </query>


-- <query name>attendance_summary_current_month</query name>
-- <query description>
-- Attendance summary for current month by employee.
-- Handles: Various attendance status types (Present, Late, Absent, etc.)
-- </query description>
-- <query>
SELECT
    e.first_name,
    e.last_name,
    d.department_name,
    COUNT(*) AS total_records,
    SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present,
    SUM(CASE WHEN a.status = 'Late' THEN 1 ELSE 0 END) AS late,
    SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS absent,
    SUM(CASE WHEN a.status = 'Remote' THEN 1 ELSE 0 END) AS remote,
    ROUND(SUM(a.work_hours), 2) AS total_hours
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN attendance a ON e.employee_id = a.employee_id
WHERE e.employment_status = 'Active'
    AND DATE_PART('month', a.attendance_date) = DATE_PART('month', CURRENT_DATE)
    AND DATE_PART('year', a.attendance_date) = DATE_PART('year', CURRENT_DATE)
GROUP BY e.employee_id, e.first_name, e.last_name, d.department_name
ORDER BY late DESC, absent DESC
LIMIT 50
-- </query>


-- <query name>employee_hierarchy</query name>
-- <query description>
-- Show employee-manager relationships.
-- Handles: Self-referencing employees.manager_id (can be NULL)
-- </query description>
-- <query>
SELECT
    e.first_name || ' ' || e.last_name AS employee_name,
    e.email,
    jp.position_title,
    d.department_name,
    COALESCE(m.first_name || ' ' || m.last_name, 'No Manager') AS manager_name,
    COALESCE(mjp.position_title, '-') AS manager_position
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN job_positions jp ON e.position_id = jp.position_id
LEFT JOIN employees m ON e.manager_id = m.employee_id
LEFT JOIN job_positions mjp ON m.position_id = mjp.position_id
WHERE e.employment_status = 'Active'
ORDER BY d.department_name, jp.position_title
LIMIT 50
-- </query>


-- <query name>training_completion_by_employee</query name>
-- <query description>
-- Count completed trainings and certifications by employee.
-- Handles: Training status types, certification flag
-- </query description>
-- <query>
SELECT
    e.first_name,
    e.last_name,
    d.department_name,
    COUNT(*) AS total_trainings,
    SUM(CASE WHEN th.status = 'Completed' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN th.certification_obtained = TRUE THEN 1 ELSE 0 END) AS certifications,
    ROUND(SUM(th.cost), 2) AS total_training_cost
FROM employees e
JOIN departments d ON e.department_id = d.department_id
LEFT JOIN training_history th ON e.employee_id = th.employee_id
WHERE e.employment_status = 'Active'
GROUP BY e.employee_id, e.first_name, e.last_name, d.department_name
HAVING COUNT(*) > 0
ORDER BY certifications DESC, completed DESC
LIMIT 50
-- </query>


-- <query name>salary_growth_by_employee</query name>
-- <query description>
-- Track salary growth for employees over time.
-- Handles: Multiple salary history records per employee
-- </query description>
-- <query>
WITH first_last_salary AS (
    SELECT
        employee_id,
        MIN(effective_date) AS first_date,
        MAX(effective_date) AS last_date
    FROM salary_history
    GROUP BY employee_id
)
SELECT
    e.first_name,
    e.last_name,
    d.department_name,
    sh1.salary_amount AS first_salary,
    sh2.salary_amount AS current_salary,
    sh2.salary_amount - sh1.salary_amount AS salary_increase,
    ROUND(((sh2.salary_amount - sh1.salary_amount) / sh1.salary_amount * 100), 2) AS increase_percent,
    fls.first_date,
    fls.last_date
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN first_last_salary fls ON e.employee_id = fls.employee_id
JOIN salary_history sh1 ON e.employee_id = sh1.employee_id AND sh1.effective_date = fls.first_date
JOIN salary_history sh2 ON e.employee_id = sh2.employee_id AND sh2.effective_date = fls.last_date
WHERE e.employment_status = 'Active'
    AND fls.first_date != fls.last_date
ORDER BY increase_percent DESC
LIMIT 50
-- </query>


-- <query name>department_headcount_by_status</query name>
-- <query description>
-- Employee count by department and employment status.
-- Handles: Multiple employment_status values
-- </query description>
-- <query>
SELECT
    d.department_name,
    COUNT(*) AS total_employees,
    SUM(CASE WHEN e.employment_status = 'Active' THEN 1 ELSE 0 END) AS active,
    SUM(CASE WHEN e.employment_status = 'On Leave' THEN 1 ELSE 0 END) AS on_leave,
    SUM(CASE WHEN e.employment_status = 'Inactive' THEN 1 ELSE 0 END) AS inactive,
    SUM(CASE WHEN e.employment_status = 'Terminated' THEN 1 ELSE 0 END) AS terminated
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name
ORDER BY active DESC
-- </query>


-- <query name>tenure_analysis</query name>
-- <query description>
-- Analyze employee tenure (time with company).
-- Handles: Date calculations using hire_date
-- </query description>
-- <query>
SELECT
    e.first_name,
    e.last_name,
    d.department_name,
    jp.position_title,
    e.hire_date,
    CURRENT_DATE - e.hire_date AS days_employed,
    ROUND((CURRENT_DATE - e.hire_date) / 365.25, 1) AS years_employed
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN job_positions jp ON e.position_id = jp.position_id
WHERE e.employment_status = 'Active'
ORDER BY days_employed DESC
LIMIT 50
-- </query>


-- <query name>late_attendance_pattern</query name>
-- <query description>
-- Find employees with frequent late attendance.
-- Handles: Attendance status filtering, date ranges
-- </query description>
-- <query>
SELECT
    e.first_name,
    e.last_name,
    d.department_name,
    COUNT(*) AS late_count,
    MIN(a.attendance_date) AS first_late,
    MAX(a.attendance_date) AS last_late
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN attendance a ON e.employee_id = a.employee_id
WHERE a.status = 'Late'
    AND e.employment_status = 'Active'
    AND a.attendance_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY e.employee_id, e.first_name, e.last_name, d.department_name
HAVING COUNT(*) >= 3
ORDER BY late_count DESC
LIMIT 50
-- </query>


-- <query name>training_budget_by_department</query name>
-- <query description>
-- Calculate training costs by department.
-- Handles: NULL cost values, aggregation by department
-- </query description>
-- <query>
SELECT
    d.department_name,
    COUNT(DISTINCT th.employee_id) AS employees_trained,
    COUNT(th.training_id) AS total_trainings,
    ROUND(SUM(COALESCE(th.cost, 0)), 2) AS total_cost,
    ROUND(AVG(COALESCE(th.cost, 0)), 2) AS avg_cost_per_training
FROM departments d
JOIN employees e ON d.department_id = e.department_id
LEFT JOIN training_history th ON e.employee_id = th.employee_id
WHERE th.status = 'Completed'
GROUP BY d.department_id, d.department_name
ORDER BY total_cost DESC
-- </query>


-- <query name>performance_rating_distribution</query name>
-- <query description>
-- Distribution of performance ratings across departments.
-- Handles: DECIMAL ratings, latest review per employee
-- </query description>
-- <query>
SELECT
    d.department_name,
    COUNT(*) AS reviews_count,
    ROUND(AVG(pr.overall_rating), 2) AS avg_rating,
    SUM(CASE WHEN pr.overall_rating >= 4.5 THEN 1 ELSE 0 END) AS excellent,
    SUM(CASE WHEN pr.overall_rating >= 4.0 AND pr.overall_rating < 4.5 THEN 1 ELSE 0 END) AS good,
    SUM(CASE WHEN pr.overall_rating >= 3.0 AND pr.overall_rating < 4.0 THEN 1 ELSE 0 END) AS average,
    SUM(CASE WHEN pr.overall_rating < 3.0 THEN 1 ELSE 0 END) AS below_average
FROM departments d
JOIN employees e ON d.department_id = e.department_id
JOIN performance_reviews pr ON e.employee_id = pr.employee_id
WHERE e.employment_status = 'Active'
    AND pr.review_date = (
        SELECT MAX(pr2.review_date)
        FROM performance_reviews pr2
        WHERE pr2.employee_id = e.employee_id
    )
GROUP BY d.department_id, d.department_name
ORDER BY avg_rating DESC
-- </query>