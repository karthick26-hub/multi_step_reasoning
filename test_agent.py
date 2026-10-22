
import unittest
from unittest.mock import patch

from agent import solve
from verifier import verify_solution


class TestReasoningAgent(unittest.TestCase):

    def setUp(self):
        # Keep unit tests independent of Gemini availability.
        self.planner_patcher = patch(
            "agent.create_plan",
            return_value=[
                "Identify the inputs.",
                "Calculate the answer.",
                "Verify the result.",
            ],
        )
        self.mock_planner = self.planner_patcher.start()
        self.addCleanup(self.planner_patcher.stop)

    # Easy questions
    def test_apple_count_1(self):
        result = solve(
            "Alice has 3 red apples and twice as many green apples. "
            "How many apples does she have?"
        )
        self.assertEqual(result["answer"], "9 apples")
        self.assertEqual(result["status"], "success")

    def test_apple_count_2(self):
        result = solve(
            "Alice has 5 red apples and twice as many green apples. "
            "How many apples does she have?"
        )
        self.assertEqual(result["answer"], "15 apples")
        self.assertEqual(result["status"], "success")

    def test_apple_count_3(self):
        result = solve(
            "Alice has 10 red apples and twice as many green apples. "
            "How many apples does she have?"
        )
        self.assertEqual(result["answer"], "30 apples")
        self.assertEqual(result["status"], "success")

    def test_train_duration_1(self):
        result = solve(
            "A train leaves at 14:30 and arrives at 18:05. "
            "How long is the journey?"
        )
        self.assertEqual(result["answer"], "3 hours 35 minutes")
        self.assertEqual(result["status"], "success")

    def test_train_duration_2(self):
        result = solve(
            "A train leaves at 09:00 and arrives at 11:30. "
            "How long is the journey?"
        )
        self.assertEqual(result["answer"], "2 hours 30 minutes")
        self.assertEqual(result["status"], "success")

    def test_meeting_slots(self):
        result = solve(
            "I have free slots from 09:00-09:20, 10:00-11:00, "
            "and 13:00-13:30. Which slots can fit a 45-minute meeting?"
        )
        self.assertEqual(result["answer"], "10:00-11:00")
        self.assertEqual(result["status"], "success")

    # Tricky and failure cases
    def test_overnight_train(self):
        result = solve(
            "A train leaves at 23:30 and arrives at 01:15. "
            "How long is the journey?"
        )
        self.assertEqual(result["answer"], "1 hours 45 minutes")
        self.assertEqual(result["status"], "success")

    def test_unsupported_question(self):
        result = solve("What is the capital of France?")
        self.assertEqual(result["status"], "failed")

    def test_unsupported_apple_relationship(self):
        result = solve(
            "Alice has 3 red apples and 4 green apples. "
            "How many apples does she have?"
        )
        self.assertEqual(result["status"], "failed")

    def test_verifier_rejects_wrong_total(self):
        question = (
            "Alice has 3 red apples and twice as many green apples. "
            "How many apples does she have?"
        )
        incorrect_solution = {
            "answer": "8 apples",
            "explanation": "Incorrect total.",
            "intermediate_results": {
                "red_apples": 3,
                "green_apples": 6,
                "total_apples": 8,
            },
        }

        result = verify_solution(question, incorrect_solution)
        self.assertFalse(result["passed"])

    def test_missing_train_times(self):
        result = solve("A train makes a journey. How long does it take?")
        self.assertEqual(result["status"], "failed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
