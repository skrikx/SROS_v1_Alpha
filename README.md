# SROS v1: Sovereign Runtime Operating System

SROS is an AI operating system designed to orchestrate complex agentic workflows. It provides a structured environment where AI agents can collaborate, governed by strict policies and observed by a mirror system.

## The Four Planes
1. **Kernel**: Core resource and process management.
2. **Runtime**: Agent execution and communication.
3. **Governance**: Policy enforcement and safety.
4. **MirrorOS**: Observability and introspection.

## Quickstart

### Installation
```bash
pip install -e .
```

### Initialization
Initialize the system configuration and database:
```bash
sros init
```

### Run Demo
Run the built-in demo to verify your installation:
```bash
sros run-demo
```

## Testing Guide

SROS v1 Alpha includes a comprehensive test suite and stress testing capabilities.

### 1. Master Test Script
Run the full test suite (unit, integration, and system tests) with a single command:
```bash
python run_all_tests.py
```
This script executes all tests in the `tests/` directory using `pytest`.

### 2. Stress Testing
Verify system robustness by running the complex feature workflow:
```bash
sros workflow run examples/complex_feature_workflow.srxml
```
This workflow simulates a multi-agent feature implementation cycle (Analyze -> Build -> Test) to verify:
- Agent coordination
- Context preservation
- Logging and telemetry

### 3. Manual Verification
You can manually run specific components:
- **Workflow Engine**: `sros workflow run examples/hello_world_workflow.srxml`
- **Specific Tests**: `pytest tests/test_ouroboros.py`

## Documentation
- [Study Guide](docs/SROS_STUDY_GUIDE_v1.md)
- [API Reference](docs/API_REFERENCE.md)
- [CLI Guide](docs/CLI_GUIDE.md)
- [Demo Guide](docs/DEMO.md)

## Configuration
If you plan to use external models (like Gemini or OpenAI), ensure you have set the necessary environment variables or configured them in `sros_config.yml`.
