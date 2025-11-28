# SROS Study Guide v1

## 1. What SROS Is
SROS (Sovereign Runtime Operating System) is an AI operating system designed to orchestrate complex agentic workflows. It provides a structured environment where AI agents can collaborate, governed by strict policies and observed by a mirror system. It is built on four core planes: Kernel, Runtime, Governance, and MirrorOS.

## 2. Plane Overview
- **Kernel**: The core foundation that manages resources, process lifecycle, and low-level system integrity.
- **Runtime**: The execution layer where agents live, communicate, and perform tasks. It handles the "physics" of the agent world.
- **Governance**: The policy enforcement layer. It ensures that all agent actions comply with defined safety, security, and ethical rules.
- **MirrorOS**: The observability and reflection layer. It records everything that happens (traces) and allows for introspection and debugging of agent behaviors.

## 3. Getting Started
To get started with SROS, follow these steps:

1.  **Install SROS**:
    ```bash
    pip install -e .
    ```

2.  **Initialize the System**:
    ```bash
    sros init
    ```

3.  **Run the Demo**:
    ```bash
    sros run-demo
    ```

**Note**: If you plan to use external models (like Gemini or OpenAI), ensure you have set the necessary environment variables or configured them in `sros_config.yml`.

## 4. First Workflow
You can run your first workflow using the provided example.
See `examples/hello_world_workflow.srxml`.

To run it:
```bash
sros workflow run examples/hello_world_workflow.srxml
```

SROS will parse the XML, instantiate the required agents, and execute the defined steps, logging all telemetry to the MirrorOS layer.

## 5. Extending SROS
SROS is designed to be extended.
- **Agents**: Create new agents in `sros/runtime/agents`.
- **Adapters**: Add new tool or model adapters in `sros/adapters`.
- **Policies**: Define new governance rules in `sros/governance/policies`.

## 6. Safety and Limits
**Alpha Status**: SROS v1 is currently in Alpha. APIs are subject to change.
**Governance**: Always review and configure governance policies before running SROS in a production environment or with sensitive data. The default policies are permissive for development but should be tightened for real-world use.
