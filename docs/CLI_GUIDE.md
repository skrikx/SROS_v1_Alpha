# SROS v1 - CLI Guide

## Overview

The SROS CLI provides command-line access to all SROS operations including kernel management, agent execution, workflow orchestration, and memory operations.

## Installation

The CLI is automatically available after installing SROS:

```bash
cd sros_v1
python -m sros.nexus.cli.main --help
```

## Commands

### System Status

```bash
# Get overall system status
python -m sros.nexus.cli.main status system

# Get adapter status
python -m sros.nexus.cli.main status adapters

# Get cost summary
python -m sros.nexus.cli.main status costs
```

### Kernel Management

```bash
# Boot the kernel
python -m sros.nexus.cli.main kernel boot

# Get kernel status
python -m sros.nexus.cli.main kernel status

# Shutdown kernel
python -m sros.nexus.cli.main kernel shutdown
```

### Agent Operations

```bash
# List available agents
python -m sros.nexus.cli.main agent list

# Run an agent
python -m sros.nexus.cli.main agent run architect "Analyze the memory system"
python -m sros.nexus.cli.main agent run builder "Create a new adapter"
python -m sros.nexus.cli.main agent run tester "Generate tests for the CLI"
```

### Workflow Execution

```bash
# List workflows
python -m sros.nexus.cli.main workflow list

# Run a workflow
python -m sros.nexus.cli.main workflow run ./workflows/example.srxml
```

### Memory Operations

```bash
# Read from memory
python -m sros.nexus.cli.main memory read --layer short
python -m sros.nexus.cli.main memory read --layer long --query "search term"
python -m sros.nexus.cli.main memory read --layer long --key "specific_key"

# Write to memory
python -m sros.nexus.cli.main memory write "Important note" --layer short
python -m sros.nexus.cli.main memory write "Persistent data" --layer long --key "data_001"

# Get memory statistics
python -m sros.nexus.cli.main memory stats
```

## Output Formats

### Text Output (default)

```bash
python -m sros.nexus.cli.main status system
```

Output:
```
status: operational
version: 1.0.0
tenant: PlatXP
environment: dev
```

### JSON Output

```bash
python -m sros.nexus.cli.main status system --json
```

Output:
```json
{
  "status": "operational",
  "version": "1.0.0",
  "tenant": "PlatXP",
  "environment": "dev"
}
```

## Verbose Mode

Enable detailed logging:

```bash
python -m sros.nexus.cli.main --verbose status system
```

## Examples

### Complete Agent Workflow

```bash
# 1. Boot kernel
python -m sros.nexus.cli.main kernel boot

# 2. Check status
python -m sros.nexus.cli.main status system

# 3. Run architect agent
python -m sros.nexus.cli.main agent run architect "Design a new feature"

# 4. Store result in memory
python -m sros.nexus.cli.main memory write "Design complete" --layer long

# 5. Check costs
python -m sros.nexus.cli.main status costs
```

### Memory Management

```bash
# Write to different layers
python -m sros.nexus.cli.main memory write "Session data" --layer short
python -m sros.nexus.cli.main memory write "Important record" --layer long --key "record_001"

# Search memory
python -m sros.nexus.cli.main memory read --layer long --query "important"

# Get statistics
python -m sros.nexus.cli.main memory stats --json
```

## Error Handling

The CLI returns appropriate exit codes:
- `0`: Success
- `1`: Error

Use in scripts:

```bash
if python -m sros.nexus.cli.main kernel boot; then
    echo "Kernel booted successfully"
else
    echo "Kernel boot failed"
    exit 1
fi
```
