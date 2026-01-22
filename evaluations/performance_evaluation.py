"""Run `uv pip install openai agno memory_profiler` to install dependencies."""

import os
import sys
import time
from agno.agent import Agent
from agno.models.openai import OpenAIChat

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


# 🔥 Evaluator Agent
evaluator_agent = Agent(
    name="SQL Evaluator",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions="""
You are a strict SQL evaluator.

Compare:
1. The user's question
2. The agent SQL output
3. The expected SQL pattern

Score from 0 to 1:
- 1 = logically equivalent SQL
- 0.7 = mostly correct with minor differences
- 0.4 = partially correct
- 0 = wrong logic

Return JSON:
{
  "score": float,
  "reason": string,
  "pass": boolean
}
"""
)


def run_single_iteration():
    agent = sql_agent
    results = []
    total_time = 0
    passed = 0
    total_score = 0

    print("\n" + "=" * 80)
    print("SQL AGENT EVALUATION - Single Run")
    print("=" * 80)

    for i, question in enumerate(TEST_CASES, 1):
        expected_sql = EXPECTED_OUTPUT_SQL_PATTERN[i - 1]

        print(f"\n{'='*80}")
        print(f"Test {i}/{len(TEST_CASES)}")
        print(f"{'='*80}")
        print(f"Question: {question}\n")

        # Measure performance
        start_time = time.time()
        response = agent.run(question)
        agent_output = response.content
        elapsed_time = time.time() - start_time

        print(f"Agent Output:\n{agent_output}\n")
        print(f"⏱️  Execution Time: {elapsed_time:.2f}s")

        # Run evaluator
        eval_prompt = f"""
User Question:
{question}

Expected SQL Pattern:
{expected_sql}

Agent Output:
{agent_output}

Evaluate correctness.
"""

        eval_response = evaluator_agent.run(eval_prompt)
        evaluation = eval_response.content

        print(f"\n📊 Evaluation:\n{evaluation}")

        # Track metrics
        total_time += elapsed_time
        
        # Parse score from evaluation (assuming JSON response)
        try:
            import json
            eval_data = json.loads(evaluation)
            score = eval_data.get("score", 0)
            pass_status = eval_data.get("pass", False)
            total_score += score
            if pass_status:
                passed += 1
        except:
            score = 0
            pass_status = False

        results.append({
            "test_number": i,
            "question": question,
            "expected_sql": expected_sql,
            "agent_output": agent_output,
            "evaluation": evaluation,
            "execution_time": elapsed_time,
            "score": score,
            "pass": pass_status
        })

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {len(TEST_CASES)}")
    print(f"Passed: {passed}/{len(TEST_CASES)} ({passed/len(TEST_CASES)*100:.1f}%)")
    print(f"Average Score: {total_score/len(TEST_CASES):.2f}")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Average Time per Test: {total_time/len(TEST_CASES):.2f}s")
    print("=" * 80 + "\n")

    return results


if __name__ == "__main__":
    results = run_single_iteration()