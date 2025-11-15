AgenticScript MVP Technical Stack & Architecture

 Important Instructions:
 - Make extensive notes as you go in a NOTES.md file which you should only ever append new notes to.
 - Keep it simple, don't over engineer, for the MVP we want to have a non-overengineered but robust foundation to build upon.
 - For every phase completed, propose a commit on the repo with brief conventional commit format
 - Save the plan in docs/ai/PLAN-INITIAL.md, and before starting a new Phase
 - Before starting a new phase put together a plan for each respective phase and document it in docs/ai/PLAN-PHASE-<number>.md
 - After every phase completed review all the relevant docs/ai/ files and update the CLAUDE.md accordingly to reflect the current state.

 Core Technical Stack

 Development Environment

 - Package Manager: UV (ultra-fast Python package installer and resolver)
 - Python Version: Python 3.10+ managed by UV
 - Project Structure: UV-based pyproject.toml configuration
 - Virtual Environment: UV-managed environments for isolation

 Language Implementation

 - Host Language: Python 3.10+ (for rapid prototyping, extensive ecosystem, easy debugging)
 - Parser: Lark parser (Python-based, EBNF grammar, easy to modify, good error handling)
 - Interpreter: Tree-walking interpreter (simple, debuggable, no compilation complexity)
 - AST Representation: Python dataclasses with inheritance (simple, typed, extensible)

 Runtime Architecture

 - Agent Backend: Python classes with threading (simple concurrency, easy debugging)
 - Message Passing: Python queues + event system (built-in, reliable, simple)
 - Tool System: Plugin pattern with mock implementations (extensible, testable)
 - State Management: In-memory dictionaries (simple, fast for MVP)

 Development Tools

 - REPL: Python cmd module + Rich library (built-in foundation + beautiful output)
 - Debug Commands: Built-in debugging commands for object inspection and state analysis
 - Testing: pytest + coverage (industry standard, comprehensive)
 - Code Quality: ruff (fast linting and formatting, UV-compatible)

 Key Dependencies (Minimal Set)

 [project]
 dependencies = [
     "lark[regex]>=1.1.7",    # Parser generator
     "rich>=13.0.0",          # Terminal formatting
     "dataclasses-json>=0.6", # JSON serialization
 ]

 [project.optional-dependencies]
 dev = [
     "pytest>=7.4.0",        # Testing
     "pytest-cov>=4.1.0",    # Coverage
     "ruff>=0.1.0",          # Linting and formatting
 ]

 Technical Choices & Rationale

 ✅ Chosen Approaches

 UV for Package Management
 - ✅ 10-100x faster than pip for dependency resolution
 - ✅ Built-in virtual environment management
 - ✅ Modern pyproject.toml configuration
 - ✅ Excellent for rapid development iteration

 Lark Parser over Hand-written/ANTLR
 - ✅ EBNF grammar is readable and maintainable
 - ✅ Excellent error reporting out of the box
 - ✅ Pure Python, no external dependencies
 - ✅ Can generate parse trees automatically
 - ❌ Slightly slower than hand-written (acceptable for MVP)

 Tree-walking Interpreter over Bytecode VM
 - ✅ Direct AST execution, easier to debug
 - ✅ No compilation step, faster iteration
 - ✅ Simpler error reporting with line numbers
 - ❌ Slower execution (can optimize later)

 Threading over Asyncio for Agents
 - ✅ Simpler mental model for agent concurrency
 - ✅ Easier debugging with standard tools
 - ✅ More familiar to most developers
 - ❌ Higher memory overhead (acceptable for local simulation)

 Rich REPL with Debug Commands over Web UI
 - ✅ Faster to develop and iterate
 - ✅ No HTTP server complexity
 - ✅ Better for deep system introspection
 - ✅ Terminal-native workflow

 MVP Architecture Overview

 agenticscript/
 ├── pyproject.toml            # UV project configuration
 ├── src/agenticscript/
 │   ├── core/
 │   │   ├── lexer.py          # Lark-based tokenization
 │   │   ├── parser.py         # Grammar definition & parsing
 │   │   ├── ast_nodes.py      # AST node definitions (dataclasses)
 │   │   └── interpreter.py    # Tree-walking interpreter
 │   ├── runtime/
 │   │   ├── agent.py          # Base Agent class with threading
 │   │   ├── message_bus.py    # Queue-based messaging system
 │   │   ├── tool_registry.py  # Plugin system for tools
 │   │   └── local_backend.py  # Local simulation backend
 │   ├── stdlib/
 │   │   ├── agents.py         # Standard agent types
 │   │   ├── tools.py          # Mock tool implementations
 │   │   └── patterns.py       # Common patterns (routing, etc.)
 │   ├── debugger/
 │   │   ├── repl.py           # cmd-based interactive shell
 │   │   ├── commands.py       # Debug command implementations
 │   │   └── visualizer.py     # Text-based call graph visualization
 │   └── cli.py                # Main CLI entry point
 ├── tests/
 │   ├── test_parser.py        # Grammar and parsing tests
 │   ├── test_interpreter.py   # Execution tests
 │   └── test_agents.py        # Agent behavior tests
 └── examples/
     ├── basic_agent.as        # Hello world equivalent
     ├── agent_communication.as # Message passing
     └── research_workflow.as  # Complete example

 Implementation Philosophy

 UV-First Development
 - Use uv add, uv remove for dependency management
 - uv run for script execution
 - uv sync for environment consistency
 - uv build for distribution

 Simplicity First
 - Choose boring, well-tested technologies
 - Prefer Python standard library where possible
 - Minimize external dependencies but choose where adding libraries can reduce complexity
 - Prioritize readability over performance but avoid unnecessary verbosity; keep things simple

 Terminal-Native Debugging
 - Rich REPL with comprehensive debug commands
 - No web UI complexity
 - Deep introspection capabilities
 - Easy to use during development

 AgenticScript MVP Implementation Plan

 Important: For every phase, ensure there is a clear testing plan to be added to ensure that the language examples work correctly as expected. Ensure that
 if the language features are inconsistent, these are reviewed and can also request input from the user to make decisions as required.

 Phase 1: Core Language Infrastructure (3 weeks)

 Language Features: Basic syntax, agent spawning, property assignment
 Example Implementation:
 # Basic agent instantiation and property modification
 agent a = spawn Agent{ openai/gpt-4o }
 agent b = spawn Agent{ gemini/gemini-2.5-flash }
 agent c = spawn Agent{ bedrock/sonnet-3-7-thinking }

 # Dynamic property assignment using pointer syntax
 *b->goal = "Gives random reply"
 *c->goal = "Access web search"
 *a->goal = "Expert with access to multiple specialised agents"

 # Basic agent status inspection
 print(a.status)  # "active", "idle", "error"
 print(b.model)   # "gemini/gemini-2.5-flash"

 Implementation Focus:
 - UV project setup with pyproject.toml
 - Lark grammar definition for basic AgenticScript syntax
 - AST nodes using Python dataclasses for agent operations
 - Basic tree-walking interpreter with agent object creation
 - Simple Agent class with threading for concurrent execution

 Phase 1.5: Debug REPL Foundation (1 week)

 Debug REPL Features: Object inspection, state analysis, execution tracing

 Example Debug Session:
 $ uv run agenticscript repl
 AgenticScript REPL v0.1.0
 Type 'help debug' for debug commands

 as> agent a = spawn Agent{ openai/gpt-4o }
 Agent 'a' spawned successfully (id: agent_001)

 as> *a->goal = "Test agent"
 Property 'goal' set on agent 'a'

 as> debug agents
 ┌─────────┬──────────┬─────────────────┬────────┬──────────┐
 │ ID      │ Name     │ Model           │ Status │ Goal     │
 ├─────────┼──────────┼─────────────────┼────────┼──────────┤
 │ agent_001│ a       │ openai/gpt-4o   │ idle   │ Test agent│
 └─────────┴──────────┴─────────────────┴────────┴──────────┘

 as> debug dump a
 Agent Details (agent_001):
 ├── Name: a
 ├── Model: openai/gpt-4o
 ├── Status: idle
 ├── Goal: Test agent
 ├── Tools: []
 ├── Properties:
 │   ├── temperature: 0.7 (default)
 │   ├── max_tokens: 2000 (default)
 │   └── created_at: 2024-01-15T10:30:45Z
 ├── Message Queue: empty
 ├── Execution History: []
 └── Memory Usage: 2.1MB

 as> debug system
 System Status:
 ├── Active Agents: 1
 ├── Total Messages: 0
 ├── Memory Usage: 15.2MB
 ├── Uptime: 00:02:34
 └── Last Error: None

 as> debug trace on
 Execution tracing enabled

 as> print(a.status)
 TRACE: Accessing property 'status' on agent 'a' (agent_001)
 TRACE: Property access returned 'idle'
 idle

 as> debug messages
 Message Bus Status:
 ├── Total Messages Sent: 0
 ├── Pending Messages: 0
 ├── Failed Messages: 0
 └── Average Processing Time: N/A

 as> debug help
 Available Debug Commands:
 ├── debug agents              - List all active agents
 ├── debug dump <agent>        - Detailed agent information
 ├── debug system             - System status overview
 ├── debug messages           - Message bus statistics
 ├── debug trace <on|off>     - Toggle execution tracing
 ├── debug memory             - Memory usage analysis
 ├── debug history [limit]    - Show execution history
 ├── debug clear              - Clear debug output
 └── debug export <file>      - Export system state to JSON

 Debug Command Implementation:
 - debug agents: Table view of all agents with status
 - debug dump : Detailed object inspection with tree view
 - debug system: Overall system health and statistics
 - debug trace on/off: Real-time execution tracing
 - debug messages: Message bus introspection
 - debug memory: Memory usage breakdown by agent
 - debug history: Execution history with timestamps
 - debug export: JSON export of complete system state

 Phase 2: Agent System & Communication (3 weeks)

 Language Features: Module imports, tool assignment, inter-agent communication
 Example Implementation:
 # Module system and tool imports
 import agenticscript.stdlib.tools { WebSearch, AgentRouting }

 # Tool assignment and composition
 *c->tools = { WebSearch }
 *a->tools = AgentRouting{ b, c }

 # Direct agent communication
 response = a.ask("What's the weather in San Francisco?")
 b.tell("Process this data: [1,2,3,4]")

 # Agent coordination patterns
 if c.has_tool(WebSearch) {
     search_result = c.execute_tool(WebSearch, "AI news 2024")
     a.tell(f"Latest AI news: {search_result}")
 }

 Enhanced Debug Session:
 as> debug messages
 Message Bus Status:
 ├── Total Messages Sent: 3
 ├── Pending Messages: 1
 ├── Failed Messages: 0
 └── Message Flow:
     ├── a → b: "Process this data..." (delivered)
     ├── c → a: "Search result..." (delivered)
     └── a → system: "Status update" (pending)

 as> debug tools
 Tool Registry:
 ├── WebSearch (mock)
 │   ├── Used by: [c]
 │   ├── Call count: 1
 │   └── Last used: 2024-01-15T10:35:22Z
 └── AgentRouting
     ├── Used by: [a]
     ├── Routes to: [b, c]
     └── Active routes: 2

 Implementation Focus:
 - Module system with simple import resolution
 - Tool registry using plugin pattern with mock implementations
 - Message bus using Python queues for inter-agent communication
 - Enhanced debug commands for communication monitoring
 - Basic control flow (if/else) in interpreter

 Phase 3: Standard Library & Advanced Patterns (2 weeks)

 Language Features: Control flow, error handling, agent lifecycle management
 Example Implementation:
 import agenticscript.stdlib.tools { WebSearch, AgentRouting, FileManager }
 import agenticscript.stdlib.agents { SupervisorAgent }

 # Advanced agent spawning with configuration
 agent researcher = spawn Agent {
     model: "openai/gpt-4o",
     goal: "Research specialist with web access",
     tools: [WebSearch, FileManager],
     max_iterations: 5,
     temperature: 0.7
 }

 agent coordinator = spawn SupervisorAgent {
     children: [researcher],
     restart_policy: "one_for_one",
     goal: "Manage research workflow"
 }

 # Control flow and error handling
 try {
     query = "Impact of quantum computing on cryptography"
     research_data = researcher.ask(query, timeout=30)

     if research_data.status == "success" {
         coordinator.broadcast_to_children(f"Research complete: {research_data}")
     }

 } catch AgentTimeout {
     coordinator.restart_agent(researcher)
 } catch AgentError as e {
     print(f"Workflow error: {e.message}")
 }

 Implementation Focus:
 - Exception handling system with try/catch blocks
 - SupervisorAgent class with child lifecycle management
 - Standard library with essential tools (WebSearch, FileManager mocks)
 - Function definitions and advanced control flow

 Phase 4: Advanced Debugging & Monitoring (2 weeks)

 Language Features: Enhanced introspection, call graph visualization, performance analysis

 Advanced Debug Session:
 as> debug callgraph
 Agent Communication Graph (last 5 minutes):
 coordinator
 ├── researcher (3 messages)
 │   ├── → "Research: quantum computing..." (success, 1.2s)
 │   ├── → "Status check" (success, 0.1s)
 │   └── ← "Research complete" (pending)
 └── system (1 message)
     └── → "Supervisor started" (success, 0.05s)

 as> debug performance
 Performance Analysis:
 ├── Agent Response Times:
 │   ├── researcher: avg 1.1s (min: 0.8s, max: 1.5s)
 │   └── coordinator: avg 0.08s (min: 0.05s, max: 0.12s)
 ├── Tool Performance:
 │   ├── WebSearch: avg 0.9s (2 calls)
 │   └── FileManager: avg 0.3s (1 call)
 └── Memory Growth: +2.1MB over 5 minutes

 as> debug watch researcher.status
 Watching: researcher.status (current: active)
 Press Ctrl+C to stop watching...
 [10:45:23] researcher.status changed: active → busy
 [10:45:25] researcher.status changed: busy → active

 Implementation Focus:
 - Call graph visualization using text-based trees
 - Performance monitoring and analysis
 - Watch command for real-time property monitoring
 - Memory profiling and leak detection

 Phase 5: Complete Integration & Polish (2 weeks)

 Language Features: Complete workflow orchestration, documentation, testing
 Example Implementation:
 import agenticscript.stdlib.tools { WebSearch, AgentRouting }
 import agenticscript.stdlib.agents { SupervisorAgent }

 # Complete but simple research workflow
 function research_workflow(topic: string) -> string {
     researcher = spawn Agent {
         model: "openai/gpt-4o",
         goal: "Research the topic",
         tools: [WebSearch]
     }

     result = researcher.ask(f"Research: {topic}")
     return result
 }

 # Execute workflow
 topic = "Future of agentic programming languages"
 report = research_workflow(topic)
 print(f"Research complete: {report}")

 Final Debug Capabilities:
 as> debug profile research_workflow("AI trends")
 Function Profile: research_workflow
 ├── Execution time: 2.3s
 ├── Agent spawns: 1
 ├── Tool calls: 1 (WebSearch)
 ├── Memory allocated: 5.2MB
 └── Peak concurrent agents: 1

 as> debug benchmark
 Running performance benchmarks...
 ├── Agent spawn time: 15ms avg (100 trials)
 ├── Message throughput: 1,250 msgs/sec
 ├── Tool call overhead: 2ms avg
 └── Memory per agent: 2.1MB avg

 Implementation Focus:
 - Function definition and calling mechanisms
 - Performance profiling and benchmarking tools
 - Comprehensive test suite using pytest
 - Documentation with examples and language reference

 Key Deliverables

 1. Phase 1: UV-managed project with Lark parser and basic agent operations
 2. Phase 1.5: Rich debug REPL with comprehensive introspection commands
 3. Phase 2: Module system, tool integration, enhanced debugging for communication
 4. Phase 3: Exception handling, agent supervision, standard library
 5. Phase 4: Advanced debugging with call graphs and performance monitoring
 6. Phase 5: Complete system with profiling, benchmarks, and documentation

 This approach emphasizes powerful debugging capabilities accessible through a rich terminal interface, making development and troubleshooting efficient
 without web UI complexity.

