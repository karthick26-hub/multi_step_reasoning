import re

def verify_solution(question: str, solution: dict) -> dict:
    """
    Verify the proposed solution using independent checks.
    """

    answer = solution.get("answer", "")
    results = solution.get("intermediate_results", {})

    # Reject missing answers
    if not answer:
        return {
            "passed": False,
            "details": "The executor did not produce a valid answer.",
            "corrected_answer": None,
        }

    question_lower = question.lower()

    
    # Verify meeting-slot constraints independently
    if any(word in question_lower for word in [
        "meeting", "free slots", "time slots"
    ]):
        slots = re.findall(
            r"\b(\d{1,2}:\d{2})\s*[-–—]\s*(\d{1,2}:\d{2})\b",
            question
        )

        duration_match = re.search(
           r"\b(\d+)\s*[- ]?\s*(?:minutes?|mins?)\b",
            question_lower
        )

        if not slots or not duration_match:
            return {
                "passed": False,
                "details": (
                    "Meeting duration or available slots are missing."
                ),
                "corrected_answer": None,
            }

        required_minutes = int(duration_match.group(1))
        expected_slots = []

        for start_time, end_time in slots:
            start_hour, start_minute = map(
                int, start_time.split(":")
            )
            end_hour, end_minute = map(
                int, end_time.split(":")
            )

            start = start_hour * 60 + start_minute
            end = end_hour * 60 + end_minute
            duration = end - start

            if duration >= required_minutes:
                expected_slots.append(
                    f"{start_time}-{end_time}"
                )

        expected_answer = (
            ", ".join(expected_slots)
            if expected_slots
            else "No available slots fit the meeting."
        )

        passed = (
            answer == expected_answer
            and results.get("required_minutes") == required_minutes
            and results.get("suitable_slots") == expected_slots
        )

        return {
            "passed": passed,
            "details": (
                "Meeting slots satisfy the duration constraint."
                if passed
                else "The selected meeting slots failed verification."
            ),
            "corrected_answer": (
                expected_answer if not passed else None
            ),
        }


    # Verify apple calculations independently
    if "apple" in question_lower:
        red = results.get("red_apples")
        green = results.get("green_apples")
        total = results.get("total_apples")

        if not all(isinstance(n, int) and n >= 0
                   for n in [red, green, total]):
            return {
                "passed": False,
                "details": "Apple quantities are missing or invalid.",
                "corrected_answer": None,
            }

        if "twice" in question_lower:
            expected_green = red * 2
        else:
            return {
                "passed": False,
                "details": "The quantity relationship is unsupported.",
                "corrected_answer": None,
            }

        expected_total = red + expected_green
        expected_answer = f"{expected_total} apples"

        passed = (
            green == expected_green
            and total == expected_total
            and answer == expected_answer
        )

        return {
            "passed": passed,
            "details": (
                "All apple quantities and the total are correct."
                if passed
                else "The apple quantities or total are inconsistent."
            ),
            "corrected_answer": (
                expected_answer if not passed else None
            ),
        }

    # Verify journey-duration calculations
    if any(word in question_lower for word in ["journey", "train"]):
        duration = results.get("duration_minutes")

        if not isinstance(duration, int) or duration < 0:
            return {
                "passed": False,
                "details": "The journey duration is missing or invalid.",
                "corrected_answer": None,
            }

        hours, minutes = divmod(duration, 60)
        expected_answer = f"{hours} hours {minutes} minutes"

        passed = answer == expected_answer

        return {
            "passed": passed,
            "details": (
                "The duration and formatted answer are consistent."
                if passed
                else "The duration and answer do not match."
            ),
            "corrected_answer": (
                expected_answer if not passed else None
            ),
        }

    return {
        "passed": False,
        "details": "No verification rule exists for this question type.",
        "corrected_answer": None,
    }
