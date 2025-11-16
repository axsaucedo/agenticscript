# AgenticScript

<div align="center">

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**A distributed agent programming language for the future of AI coordination**

[Features](#features) |
[Quick Start](#quick-start) |
[Language Guide](#language-guide) |
[Examples](#examples) |
[Documentation](#documentation) |
[Contributing](#contributing)

</div>

---

## Overview

AgenticScript is a programming language designed specifically for distributed agent systems. It provides first-class support for agent spawning, inter-agent communication, tool management, and coordination patterns that are essential for modern AI applications.

### Key Capabilities

- **Agent-First Design**: Native syntax for spawning and managing AI agents
- **Inter-Agent Communication**: Built-in message passing with `ask` and `tell` operations
- **Tool Management**: Dynamic tool assignment and execution framework
- **Message Bus**: Thread-safe communication with delivery guarantees
- **Rich Debugging**: Live agent status, call graphs, and performance metrics
- **Module System**: Import and organize agent types and tools
- **High Performance**: Threading-based concurrent execution

## Quick Start

### Prerequisites

- Python 3.12 or higher
- UV package manager (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/agenticscript.git
cd agenticscript

# Install dependencies with UV
uv sync --dev

# Or with pip
pip install -e .
```

### Your First AgenticScript Program

Create a file called `hello_agents.as`:

```zig
import agenticscript.stdlib.tools { WebSearch, AgentRouting }

# Spawn multiple agents with different capabilities
agent coordinator = spawn Agent{ openai/gpt-4o }
agent researcher = spawn Agent{ claude/sonnet }
agent analyzer = spawn Agent{ gemini/pro }

# Configure agent goals and tools
*coordinator->goal = "Coordinate research and analysis tasks"
*researcher->goal = "Research information using web search"
*analyzer->goal = "Analyze research data"

*coordinator->tools = { AgentRouting{ researcher, analyzer } }
*researcher->tools = { WebSearch }

# Inter-agent communication
coordination_response = coordinator.ask("What is your current status?")
print("Coordinator status:")
print(coordination_response)

researcher.tell("Start research on AI trends")
analyzer.tell("Prepare for data analysis")
```

Run your program:

```bash
uv run agenticscript hello_agents.as
```

## Interactive REPL

AgenticScript includes a rich terminal-based REPL with debugging capabilities:

```bash
> agenticscript

AgenticScript REPL v0.1.0
Type 'help debug' for debug commands

🤖> <your commands>
```

Available debug commands:
- `debug agents` - Show all active agents and their status
- `debug tools` - Display tool registry and usage statistics
- `debug messages` - View message bus performance metrics
- `debug flow` - Visualize agent communication patterns
- `debug stats` - Comprehensive system statistics
- `debug dump <agent>` - Detailed agent information

### Example Debug Agents

```bash
🤖> debug agents
                               Active Agents
┏━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID        ┃ Name        ┃ Model         ┃ Status ┃ Goal                 ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ agent_001 │ coordinator │ openai/gpt-4o │ idle   │ Coordinate resear... │
│ agent_002 │ researcher  │ claude/sonnet │ idle   │ Research informat... │
│ agent_003 │ analyzer    │ gemini/pro    │ idle   │ Analyze research ... │
└───────────┴─────────────┴───────────────┴────────┴──────────────────────┘
```

## Features

### Language Features
- **Agent Lifecycle Management**: Spawn, configure, and coordinate agents
- **Communication Primitives**: Direct agent-to-agent messaging
- **Tool Integration**: Pluggable tool system with registry management
- **Control Flow**: Conditional logic and boolean expressions
- **Import System**: Modular organization of agent types and tools
- **Variable Assignment**: Full expression evaluation and storage

### Runtime Features
- **Message Bus**: Priority queue-based message delivery
- **Tool Registry**: Plugin-pattern architecture for extensible tools
- **Threading Model**: Background processing and concurrent operations
- **Debug Interface**: Rich terminal-based debugging with live statistics
- **Performance Monitoring**: Message flow visualization and usage patterns

### Built-in Tools
- **WebSearch**: Simulated web search capabilities
- **AgentRouting**: Dynamic message routing between agents
- **Calculator**: Mathematical operations and computations
- **FileManager**: File system operations and management

## Language Guide

### Agent Declaration and Management

```zig
# Spawn an agent with a specific model
agent myAgent = spawn Agent{ openai/gpt-4o }

# Set agent properties
*myAgent->goal = "Process user requests"
*myAgent->temperature = 0.7
*myAgent->max_tokens = 1000
```

### Tool Assignment and Usage

```zig
# Import tools from stdlib
import agenticscript.stdlib.tools { WebSearch, Calculator }

# Assign tools to agents
*myAgent->tools = { WebSearch, Calculator }

# Check tool availability and execute
if myAgent.has_tool("WebSearch") {
    result = myAgent.execute_tool("WebSearch", "latest AI research")
    print(result)
}
```

### Inter-Agent Communication

```zig
# Synchronous communication (ask/response)
response = agent1.ask("What is your status?")

# Asynchronous communication (fire and forget)
agent2.tell("Process this data")

# Agent routing for coordination
*coordinator->tools = { AgentRouting{ worker1, worker2, worker3 } }
```

### Control Flow and Logic

```zig
# Conditional execution
if agent.status == "idle" {
    agent.tell("Start processing")
} else {
    print("Agent is busy")
}

# Boolean expressions
if agent.has_tool("WebSearch") and agent.status == "ready" {
    search_result = agent.execute_tool("WebSearch", "query")
}
```

## Examples

### Multi-Agent Research Pipeline

```zig
import agenticscript.stdlib.tools { WebSearch, AgentRouting }

# Create specialized agents
agent research_coordinator = spawn Agent{ openai/gpt-4o }
agent web_researcher = spawn Agent{ claude/sonnet }
agent data_analyst = spawn Agent{ gemini/pro }
agent report_writer = spawn Agent{ openai/gpt-4o }

# Configure the pipeline
*research_coordinator->goal = "Coordinate research pipeline"
*research_coordinator->tools = { AgentRouting{ web_researcher, data_analyst, report_writer } }

*web_researcher->tools = { WebSearch }
*data_analyst->goal = "Analyze research data"
*report_writer->goal = "Generate research reports"

# Execute the pipeline
if research_coordinator.has_tool("AgentRouting") {
    research_coordinator.tell("Start research on quantum computing")

    # Check pipeline status
    status = research_coordinator.ask("What is the pipeline status?")
    print(status)
}
```

### Tool Integration Example

```zig
import agenticscript.stdlib.tools { Calculator, FileManager }

agent math_agent = spawn Agent{ openai/gpt-4o }
*math_agent->tools = { Calculator, FileManager }

if math_agent.has_tool("Calculator") {
    result = math_agent.execute_tool("Calculator", "2 + 2 * 3")
    print("Calculation result:")
    print(result)
}
```

## Architecture

AgenticScript is built on a robust architecture designed for scalability and extensibility:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Lark Parser   │ -> │  AST Transformer │ -> │ Tree Interpreter│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Message Bus    │ <- │   Tool Registry  │ <- │  Agent System   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Components

- **Parser**: Lark-based grammar with EBNF syntax definitions
- **AST**: Comprehensive node hierarchy for all language constructs
- **Interpreter**: Tree-walking interpreter with runtime value system
- **Message Bus**: Thread-safe inter-agent communication
- **Tool Registry**: Plugin architecture for extensible functionality
- **Debug System**: Rich introspection and performance monitoring

## Development

### Project Structure

```
agenticscript/
├── src/agenticscript/
│   ├── core/                 # Core language implementation
│   │   ├── grammar.lark      # Language grammar definition
│   │   ├── ast_nodes.py      # AST node definitions
│   │   ├── parser.py         # Parser and transformer
│   │   ├── interpreter.py    # Tree-walking interpreter
│   │   └── module_system.py  # Import resolution
│   ├── runtime/              # Runtime systems
│   │   ├── message_bus.py    # Inter-agent communication
│   │   └── tool_registry.py  # Tool management
│   ├── stdlib/               # Standard library
│   │   ├── tools.py          # Built-in tools
│   │   └── agents.py         # Standard agent types
│   └── debugger/             # Debug interface
│       └── repl.py           # Interactive REPL
├── tests/                    # Comprehensive test suite
├── docs/                     # Documentation
└── examples/                 # Example programs
```

### Running Tests

```bash
# Run all tests
uv run python -m pytest tests/

# Run specific test categories
uv run python tests/test_parser.py
uv run python tests/test_interpreter.py
uv run python tests/test_phase2_integration.py

# Run enhanced debug tests
uv run python tests/test_enhanced_debug.py
```

### Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details. # TODO

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`uv run python -m pytest`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request


## Documentation

- [Language Reference](docs/language-reference.md) # TODO
- [API Documentation](docs/api.md) # TODO
- [Architecture Guide](docs/architecture.md) # TODO
- [Examples Gallery](examples/) # TODO
- [Development Notes](docs/ai/NOTES.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Lark](https://github.com/lark-parser/lark) for parsing
- Terminal interface powered by [Rich](https://github.com/Textualize/rich)
- Package management with [UV](https://github.com/astral-sh/uv)
- Inspired by distributed systems and agent-oriented programming research

---

<div align="center">

**[Back to Top](#agenticscript)**

</div>
