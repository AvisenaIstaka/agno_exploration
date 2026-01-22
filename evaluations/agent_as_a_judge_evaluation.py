"""Run `uv pip install openai agno memory_profiler` to install dependencies."""
import os
import sys
from agno.eval.performance import PerformanceEval
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from sql_agent import sql_agent

TEST_CASES = [
    "Berapa jumlah karyawan aktif di setiap departemen?",
    "Siapa saja karyawan yang bekerja di departemen Engineering?",
    "Berapa gaji rata-rata karyawan saat ini?",
    "Tampilkan karyawan yang statusnya bukan 'Active' atau 'Terminated'",
    "Hitung berapa hari karyawan sudah bekerja sejak tahun 2023",
    "Tampilkan absensi karyawan yang check_in_time nya setelah jam 8 pagi",
    "Cari karyawan yang gaji awalnya di bawah 10 juta tapi sekarang di atas 15 juta",
    "Hitung total biaya training yang statusnya 'Completed' per departemen",
    "Tampilkan karyawan yang performance rating terbarunya antara 3.5 dan 4.5",
    "Cari training yang durasinya lebih dari 20 jam dan dapat sertifikasi"
]

EXPECTED_OUTPUT_SQL_PATTERN = [
    "SELECT d.department_name, COUNT(e.employee_id) ... FROM departments d JOIN employees e ... WHERE e.employment_status = 'Active' GROUP BY ...",
    "SELECT e.first_name, e.last_name, e.email ... FROM employees e JOIN departments d ... WHERE d.department_name = 'Engineering' AND e.employment_status = 'Active'",
    "SELECT AVG(sh.salary_amount) ... FROM salary_history sh WHERE sh.effective_date = (SELECT MAX(sh2.effective_date) FROM salary_history sh2 WHERE sh2.employee_id = sh.employee_id)",
    "SELECT ... FROM employees WHERE employment_status NOT IN ('Active', 'Terminated') OR employment_status IN ('Inactive', 'On Leave')",
    "SELECT first_name, last_name, hire_date, CURRENT_DATE - hire_date AS days_employed FROM employees WHERE employment_status = 'Active'",
    "SELECT ... FROM attendance WHERE check_in_time > '08:00:00' OR status = 'Late'",
    "WITH first_salary AS (...MIN(effective_date)...), current_salary AS (...MAX(effective_date)...) SELECT ... WHERE fs.salary_amount < 10000000 AND cs.salary_amount > 15000000",
    "SELECT d.department_name, SUM(COALESCE(th.cost, 0)) ... WHERE th.status = 'Completed' GROUP BY d.department_name",
    "SELECT ... FROM employees e JOIN performance_reviews pr ... WHERE pr.review_date = (SELECT MAX(pr2.review_date) ...) AND pr.overall_rating BETWEEN 3.5 AND 4.5",
    "SELECT training_name, duration_hours FROM training_history WHERE duration_hours > 20 AND certification_obtained = TRUE"
]

def run_all_tests():
    agent = sql_agent
    results = []

    for i, question in enumerate(TEST_CASES, 1):
        print(f"\n=== Running Test {i}/{len(TEST_CASES)} ===")
        print(f"Prompt: {question}")

        response = agent.run(question)

        print(f"Response:\n{response.content}")
        print("=" * 50)

        results.append({
            "question": question,
            "response": response.content
        })

    return results


multi_test_perf = PerformanceEval(
    name="SQL Agent Multi Test Evaluation",
    func=run_all_tests,
    num_iterations=1,
    warmup_runs=0,
)

if __name__ == "__main__":
    multi_test_perf.run(print_results=True, print_summary=True)
