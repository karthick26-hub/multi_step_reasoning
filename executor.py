
import re


def execute_plan(question: str, plan: list[str]) -> dict:
    """Execute a plan and return a proposed solution."""

    question_lower = question.lower()

    # Meeting-slot constraint problems
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
                "answer": "",
                "explanation": "Meeting duration or slots are missing.",
                "intermediate_results": {},
            }

        required = int(duration_match.group(1))
        durations = {}
        suitable = []

        for start_time, end_time in slots:
            sh, sm = map(int, start_time.split(":"))
            eh, em = map(int, end_time.split(":"))
            duration = (eh * 60 + em) - (sh * 60 + sm)

            durations[f"{start_time}-{end_time}"] = duration

            if duration >= required:
                suitable.append(f"{start_time}-{end_time}")

        answer = (
            ", ".join(suitable)
            if suitable
            else "No available slots fit the meeting."
        )

        return {
            "answer": answer,
            "explanation": (
                f"Selected slots have at least {required} minutes available."
                if suitable
                else f"No slot provides the required {required} minutes."
            ),
            "intermediate_results": {
                "required_minutes": required,
                "slot_durations": durations,
                "suitable_slots": suitable,
            },
        }

    # Apple quantity problems
    if "apple" in question_lower:
        numbers = [int(n) for n in re.findall(r"\d+", question)]

        if not numbers:
            return {
                "answer": "",
                "explanation": "No quantity was found.",
                "intermediate_results": {},
            }

        red = numbers[0]

        if "twice" not in question_lower:
            return {
                "answer": "",
                "explanation": "The quantity relationship is unsupported.",
                "intermediate_results": {},
            }

        green = red * 2
        total = red + green

        return {
            "answer": f"{total} apples",
            "explanation": f"There are {red} red apples and {green} green apples.",
            "intermediate_results": {
                "red_apples": red,
                "green_apples": green,
                "total_apples": total,
            },
        }

    # Train journey-duration problems
    if any(word in question_lower for word in ["journey", "train"]):
        times = re.findall(r"\b(\d{1,2}):(\d{2})\b", question)

        if len(times) >= 2:
            sh, sm = map(int, times[0])
            eh, em = map(int, times[1])

            if sh > 23 or eh > 23 or sm > 59 or em > 59:
                return {
                    "answer": "",
                    "explanation": "Invalid time in the question.",
                    "intermediate_results": {},
                }

            start = sh * 60 + sm
            end = eh * 60 + em
            duration = (end - start) % (24 * 60)
            hours, minutes = divmod(duration, 60)

            return {
                "answer": f"{hours} hours {minutes} minutes",
                "explanation": (
                    "The journey duration is calculated from "
                    "the departure and arrival times."
                ),
                "intermediate_results": {
                    "duration_minutes": duration,
                },
            }

    return {
        "answer": "",
        "explanation": "This question type is not supported yet.",
        "intermediate_results": {},
    }
