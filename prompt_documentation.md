# Prompt Documentation

## Overview

Prompt text is centralized in `prompts.py` rather than scattered through the code. The live Gemini call currently uses `PLANNER_PROMPT`. The Executor and Verifier are implemented as deterministic Python functions; they do not currently call an LLM.

## Planner prompt

**Purpose:** turn the user's plain-text question into a concise ordered plan.

**Expected output:** numbered steps, one step per line. The Planner parser removes numbering and stores the steps in `metadata.plan`.

**Design choices:**
- Requests a plan only, not a final answer.
- Keeps the plan short and focused on identifying inputs, calculating, and checking.
- Separates planning from deterministic execution.

**Known limitation:** the model may include a heading such as `Plan:`. This is harmless to the calculation but can be cleaned from the parsed plan.

## Executor prompt

The assignment only requires a separate Executor prompt if an LLM is used to execute the plan. This project currently uses deterministic Python in `executor.py`, so `EXECUTOR_PROMPT` is retained in `prompts.py` as a documented prompt/template, but it is not sent to Gemini.

The code executor currently supports:
- Apple counts with a “twice as many” relationship.
- Train duration between two times, including overnight journeys.
- Meeting-slot selection based on required duration.

## Verifier prompt

`VERIFIER_PROMPT` is retained in `prompts.py` to document how an LLM-based verifier could be instructed to inspect a question and proposed solution. The current live verifier is a Python function in `verifier.py`, which validates supported problem types deterministically. It checks quantities/totals, duration consistency, and meeting-slot constraints.

This is an intentional design choice: the assignment permits code-based validation, and deterministic checks reduce the chance of accepting an inconsistent arithmetic result.

## Examples used for testing

1. **Apple count:** “Alice has 3 red apples and twice as many green apples. How many apples does she have?” Expected total: 9.
2. **Train duration:** “A train leaves at 14:30 and arrives at 18:05. How long is the journey?” Expected duration: 3 hours 35 minutes.
3. **Overnight journey:** “A train leaves at 23:30 and arrives at 01:15. How long is the journey?” Expected duration: 1 hour 45 minutes.
4. **Meeting constraint:** “I have free slots from 09:00-09:20, 10:00-11:00, and 13:00-13:30. Which slots can fit a 45-minute meeting?” Expected slot: 10:00-11:00.
5. **Unsupported question:** “What is the capital of France?” Expected behavior: fail safely because this domain is not implemented.
6. **Inconsistent apple relationship:** “Alice has 3 red apples and 4 green apples. How many apples does she have?” Expected behavior: fail safely because the implemented apple solver expects the twice-as-many relationship.

## Approaches that did not work well

- The initial meeting-duration parser recognized “45 minutes” but not the hyphenated adjective “45-minute”. The regex was updated to accept optional hyphens/spaces.
- Calling Gemini during every unit test made tests slow and vulnerable to transient 503 service errors. The Planner is now mocked in `test_agent.py`; a separate script checks live Gemini connectivity.
- A heavier model was not necessary for the short planning task, so the configured model was changed to a lighter available model after service errors.

## What could be improved

- Strip headings such as `Plan:` when parsing Planner output.
- Use a structured JSON response for plans.
- Add explicit tests for invalid clock times, slots ending before they start, and no-suitable-slot cases.
- Make retry limits and backoff settings configurable.
- Add more supported word-problem categories and evaluate live model plans separately from unit tests.
