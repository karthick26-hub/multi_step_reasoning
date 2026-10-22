import json

from planner import create_plan
from executor import execute_plan
from verifier import verify_solution


MAX_RETRIES = 2


def solve(question: str) -> dict:
    """
    Solve a question using planning, execution,
    verification, and limited retries.
    """

    retries = 0
    checks = []
    plan = []

    while retries <= MAX_RETRIES:
        plan = create_plan(question)
        solution = execute_plan(question, plan)
        verification = verify_solution(question, solution)

        checks.append({
            "check_name": f"verification_attempt_{retries + 1}",
            "passed": verification["passed"],
            "details": verification["details"],
        })

        if verification["passed"]:
            return {
                "answer": solution["answer"],
                "status": "success",
                "reasoning_visible_to_user": solution["explanation"],
                "metadata": {
                    "plan": plan,
                    "checks": checks,
                    "retries": retries,
                },
            }

        # Retry the planning and execution process
        retries += 1

    return {
        "answer": "Unable to solve the question reliably.",
        "status": "failed",
        "reasoning_visible_to_user": (
            "The proposed solution could not pass verification."
        ),
        "metadata": {
            "plan": plan,
            "checks": checks,
            "retries": retries,
        },
    }


if __name__ == "__main__":
    print("Multi-Step Reasoning Agent")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Enter your question: ").strip()

        if question.lower() == "exit":
            print("Goodbye, buddy!")
            break

        if not question:
            print("Please enter a question.\n")
            continue

        result = solve(question)
        print("\nAgent Response:")
        print(json.dumps(result, indent=4))
        print()
