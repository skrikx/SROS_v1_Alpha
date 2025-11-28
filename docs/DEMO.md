# SROS v1 Demo Showcase

This document provides a step‑by‑step walkthrough that demonstrates the core capabilities of the **SROS v1** system.

## Prerequisites

- Python 3.10+ installed
- The repository root is `sros-v1-alpha`
- A valid Gemini API key is stored in `.env` (`GEMINI_API_KEY=YOUR_KEY`) (Optional, for external model calls)

## Demo Steps

1. **Boot the kernel**
   ```bash
   sros kernel boot
   ```
   The kernel starts the event bus, registers adapters, and loads the memory layers.

2. **Check system status**
   ```bash
   sros status system
   ```
   You should see an *operational* status with version, tenant, and environment information.

3. **Run the Architect agent**
   ```bash
   sros agent run architect "Analyze: The kernel event bus is experiencing message delivery delays."
   ```
   The Architect contacts the Gemini model, performs a root‑cause analysis and returns a structured recommendation.

4. **Store the analysis in short‑term memory**
   ```bash
   sros memory write "$(cat analysis.txt)" --layer short
   ```
   The result is kept for the current session.

5. **Run the Builder agent**
   ```bash
   sros agent run builder "Create a new adapter for a custom HTTP tool"
   ```
   The Builder generates production‑ready Python code for the requested adapter.

6. **Persist the generated code in long‑term memory**
   ```bash
   sros memory write "$(cat adapter.py)" --layer long --key "custom_http_adapter"
   ```

7. **Run the Tester agent**
   ```bash
   sros agent run tester "Generate pytest tests for the new adapter"
   ```
   The Tester returns a full pytest suite that can be saved and executed.

8. **Execute the generated tests**
   ```bash
   pytest generated_tests.py -q
   ```
   All tests should pass, confirming the adapter works as expected.

9. **View telemetry**
   ```bash
   sros status telemetry
   ```
   This prints a JSON summary of events, costs, and drift signals collected during the demo.

10. **Launch the real‑time dashboard**
    ```bash
    sros dashboard serve
    ```
    Open `http://localhost:8000` in a browser to see live charts of system health, cost, and drift.

## Expected Output

The demo should finish with:
- **System status:** `operational`
- **Architect analysis:** a multi‑paragraph recommendation with root‑cause, design, trade‑offs, and implementation steps.
- **Builder output:** a fully‑typed, PEP‑8‑compliant Python class for the HTTP adapter.
- **Tester output:** a pytest file that imports the generated adapter and runs a few sanity checks.
- **Telemetry dashboard:** live graphs showing CPU usage, request latency, Gemini cost, and any drift alerts.

Feel free to modify the prompts and explore different workflows – the SROS architecture is designed for rapid, safe, and observable self‑evolution.
