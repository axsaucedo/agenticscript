# Phase 2 Implementation Plan: Agent System & Communication

## Overview
**Duration**: 3 weeks
**Focus**: Module imports, tool assignment, inter-agent communication
**Foundation**: Building on completed Phase 1 (Core Language Infrastructure) and Phase 1.5 (Debug REPL Foundation)

## Comprehensive Language Features & Examples

### 1. Module System & Import Statements

**Valid Import Syntax:**
```agenticscript
// Basic tool imports
import agenticscript.stdlib.tools { WebSearch, AgentRouting }

// Multiple imports from same module
import agenticscript.stdlib.tools { WebSearch, FileManager, Calculator }

// Agent type imports (for future phases)
import agenticscript.stdlib.agents { SupervisorAgent }

// Mixed imports
import agenticscript.stdlib.tools { WebSearch }
import agenticscript.stdlib.agents { SupervisorAgent }
```

**Invalid Import Syntax (Should Error):**
```agenticscript
// Missing braces - INVALID
import agenticscript.stdlib.tools WebSearch

// Wrong module path - INVALID
import invalid.module { WebSearch }

// Empty import list - INVALID
import agenticscript.stdlib.tools { }

// Duplicate imports - WARNING/ERROR
import agenticscript.stdlib.tools { WebSearch, WebSearch }
```

### 2. Tool Assignment & Management

**Valid Tool Assignment:**
```agenticscript
// Basic tool assignment
agent a = spawn Agent{ openai/gpt-4o }
*a->tools = { WebSearch }

// Multiple tools
*a->tools = { WebSearch, FileManager, Calculator }

// Tool composition with agent routing
agent b = spawn Agent{ gemini/gemini-2.5-flash }
agent c = spawn Agent{ bedrock/sonnet-3-7-thinking }
*a->tools = AgentRouting{ b, c }

// Mixed tool types
*a->tools = { WebSearch, AgentRouting{ b, c }, FileManager }

// Tool addition (append to existing)
*a->tools += { Calculator }
*a->tools += AgentRouting{ d, e }
```

**Invalid Tool Assignment (Should Error):**
```agenticscript
// Tool assignment to non-existent agent - ERROR
*nonexistent->tools = { WebSearch }

// Invalid tool name - ERROR
*a->tools = { InvalidTool }

// Wrong syntax - ERROR
*a->tools WebSearch  // Missing = and braces

// Tool assignment before agent creation - ERROR
*a->tools = { WebSearch }
agent a = spawn Agent{ openai/gpt-4o }
```

### 3. Inter-Agent Communication

**Valid Communication Patterns:**
```agenticscript
# Basic ask/tell operations
agent researcher = spawn Agent{ openai/gpt-4o }
agent analyst = spawn Agent{ claude/sonnet }

# Synchronous communication with response
response = researcher.ask("Research quantum computing trends")
print(response)

# Asynchronous messaging
analyst.tell("Process this data: [1, 2, 3, 4, 5]")

# Communication with timeout
response = researcher.ask("Complex query", timeout=30)

// Conditional communication
if researcher.status == "idle" {
    task_result = researcher.ask("What are the latest AI developments?")
    analyst.tell(f"New research data: {task_result}")
}

// Tool-based communication
*researcher->tools = { WebSearch }
if researcher.has_tool(WebSearch) {
    search_result = researcher.execute_tool(WebSearch, "AI news 2024")
    analyst.tell(f"Search results: {search_result}")
}
```

**Invalid Communication (Should Error):**
```agenticscript
// Communication with non-existent agent - ERROR
response = nonexistent.ask("question")

# Invalid method call - ERROR
response = researcher.invalid_method("question")

# Missing arguments - ERROR
response = researcher.ask()  # ask requires message

// Tool execution without tool - ERROR
result = researcher.execute_tool(WebSearch, "query")  # WebSearch not assigned
```

### 4. Control Flow (If/Else)

**Valid Control Flow:**
```agenticscript
# Basic if statement
if agent.status == "idle" {
    agent.tell("Start processing")
}

# If-else
if agent.has_tool(WebSearch) {
    result = agent.execute_tool(WebSearch, "query")
} else {
    print("Agent lacks web search capability")
}

# Nested conditions
if agent.status == "active" {
    if agent.has_tool(WebSearch) {
        search_result = agent.execute_tool(WebSearch, "data")
        print(f"Search completed: {search_result}")
    } else {
        print("No search tool available")
    }
}

# Multiple conditions
if agent.status == "idle" and agent.has_tool(Calculator) {
    result = agent.execute_tool(Calculator, "2 + 2")
    print(f"Calculation: {result}")
}
```

**Invalid Control Flow (Should Error):**
```agenticscript
# Missing braces - ERROR
if agent.status == "idle"
    print("idle")

# Invalid comparison - ERROR
if agent.status = "idle" {  # Should be ==
    print("idle")
}

# Incomplete if statement - ERROR
if {
    print("missing condition")
}
```

## Rich Sample Programs

### Sample 1: Basic Agent Coordination
```agenticscript
// Import required tools
import agenticscript.stdlib.tools { WebSearch, AgentRouting }

// Create specialized agents
agent researcher = spawn Agent{ openai/gpt-4o }
agent summarizer = spawn Agent{ claude/sonnet }
agent coordinator = spawn Agent{ gemini/gemini-pro }

// Configure tools and routing
*researcher->tools = { WebSearch }
*coordinator->tools = AgentRouting{ researcher, summarizer }

// Set agent purposes
*researcher->goal = "Conduct web research on given topics"
*summarizer->goal = "Create concise summaries from research data"
*coordinator->goal = "Manage research workflow"

// Execute research workflow
topic = "Latest developments in quantum computing"

if researcher.has_tool(WebSearch) {
    // Perform research
    research_data = researcher.execute_tool(WebSearch, topic)
    print(f"Research completed on: {topic}")

    // Send data for summarization
    summary_request = f"Summarize this research: {research_data}"
    summary = summarizer.ask(summary_request)

    // Report results
    coordinator.tell(f"Research summary: {summary}")
    print(f"Final summary: {summary}")
} else {
    print("Error: Researcher lacks web search capability")
}

// Check system status
print(f"Researcher status: {researcher.status}")
print(f"Summarizer status: {summarizer.status}")
print(f"Coordinator status: {coordinator.status}")
```

### Sample 2: Multi-Agent Tool Composition
```agenticscript
import agenticscript.stdlib.tools { WebSearch, FileManager, Calculator, AgentRouting }

// Create agent network
agent data_collector = spawn Agent{ openai/gpt-4o }
agent data_processor = spawn Agent{ claude/sonnet }
agent data_analyzer = spawn Agent{ gemini/gemini-pro }
agent orchestrator = spawn Agent{ bedrock/sonnet-3-7-thinking }

// Assign specialized tools
*data_collector->tools = { WebSearch, FileManager }
*data_processor->tools = { Calculator, FileManager }
*data_analyzer->tools = { Calculator }
*orchestrator->tools = AgentRouting{ data_collector, data_processor, data_analyzer }

// Set agent roles
*data_collector->goal = "Collect data from various sources"
*data_processor->goal = "Process and clean collected data"
*data_analyzer->goal = "Analyze processed data for insights"
*orchestrator->goal = "Coordinate the entire data pipeline"

// Execute data pipeline
dataset_query = "Financial market data for Q4 2024"

// Step 1: Data Collection
if data_collector.has_tool(WebSearch) and data_collector.has_tool(FileManager) {
    raw_data = data_collector.execute_tool(WebSearch, dataset_query)
    data_collector.execute_tool(FileManager, f"save:{raw_data}")
    data_processor.tell(f"Data ready for processing: {raw_data}")
}

// Step 2: Data Processing
processing_complete = data_processor.ask("Process the financial data")
if processing_complete == "success" {
    processed_data = data_processor.execute_tool(Calculator, "statistical_analysis")
    data_analyzer.tell(f"Process complete, analyze: {processed_data}")
}

// Step 3: Analysis
analysis_result = data_analyzer.ask("Perform trend analysis on processed data")
calculation_result = data_analyzer.execute_tool(Calculator, "trend_calculation")

// Final coordination
orchestrator.tell(f"Pipeline complete. Analysis: {analysis_result}")
print(f"Data pipeline result: {calculation_result}")
```

### Sample 3: Error Handling & Agent Recovery
```agenticscript
import agenticscript.stdlib.tools { WebSearch, AgentRouting }

// Create agents with backup routing
agent primary = spawn Agent{ openai/gpt-4o }
agent backup = spawn Agent{ claude/sonnet }
agent monitor = spawn Agent{ gemini/gemini-pro }

# Configure monitoring system
*primary->tools = { WebSearch }
*backup->tools = { WebSearch }
*monitor->tools = AgentRouting{ primary, backup }

// Test primary agent functionality
query = "Test connectivity and search capability"

if primary.status == "idle" {
    // Try primary agent first
    if primary.has_tool(WebSearch) {
        result = primary.execute_tool(WebSearch, query)
        print(f"Primary agent result: {result}")
    } else {
        print("Primary agent lacks search capability")

        // Fallback to backup agent
        if backup.has_tool(WebSearch) {
            result = backup.execute_tool(WebSearch, query)
            print(f"Backup agent result: {result}")
            monitor.tell("Primary agent failed, backup used successfully")
        } else {
            print("Both agents lack search capability")
            monitor.tell("Critical: No agents available for search")
        }
    }
} else {
    print(f"Primary agent not available, status: {primary.status}")

    // Use backup immediately
    backup_result = backup.ask(query)
    print(f"Backup handling request: {backup_result}")
}

# System health check
print("=== System Status ===")
print(f"Primary: {primary.status}")
print(f"Backup: {backup.status}")
print(f"Monitor: {monitor.status}")
```

### Sample 4: Complex Tool Interactions
```agenticscript
import agenticscript.stdlib.tools { WebSearch, FileManager, Calculator, AgentRouting }

// Multi-tool agent for complex tasks
agent research_assistant = spawn Agent{ openai/gpt-4o }
agent computation_engine = spawn Agent{ claude/sonnet }
agent data_manager = spawn Agent{ gemini/gemini-pro }

// Assign multiple tools to each agent
*research_assistant->tools = { WebSearch, FileManager }
*computation_engine->tools = { Calculator, FileManager }
*data_manager->tools = { FileManager, AgentRouting{ research_assistant, computation_engine } }

// Complex workflow with tool chaining
research_topic = "Machine learning model performance metrics"

// Phase 1: Research and data collection
if research_assistant.has_tool(WebSearch) {
    research_data = research_assistant.execute_tool(WebSearch, research_topic)

    // Save research data
    if research_assistant.has_tool(FileManager) {
        research_assistant.execute_tool(FileManager, f"save_research:{research_data}")
        print("Research data saved successfully")
    }

    // Request computation
    computation_engine.tell(f"Calculate metrics from: {research_data}")
}

// Phase 2: Computational analysis
if computation_engine.has_tool(Calculator) {
    metrics = computation_engine.execute_tool(Calculator, "ml_performance_analysis")
    print(f"Computed metrics: {metrics}")

    // Save computational results
    if computation_engine.has_tool(FileManager) {
        computation_engine.execute_tool(FileManager, f"save_metrics:{metrics}")
    }
}

// Phase 3: Data management and coordination
summary_request = "Compile research and computational results"
final_report = data_manager.ask(summary_request)

// Tool verification and status
print("=== Tool Status Report ===")
print(f"Research Assistant Tools: {research_assistant.tools}")
print(f"Computation Engine Tools: {computation_engine.tools}")
print(f"Data Manager Tools: {data_manager.tools}")
print(f"Final Report: {final_report}")
```

## Implementation Breakdown by Week

### Week 1: Grammar & Module System
**New Grammar Rules:**
- Import statements with tool/agent specification
- If/else control structures
- Tool assignment operators (`=`, `+=`)
- Method calls with tool execution
- Boolean operators for conditions

**AST Node Additions:**
- `ImportStatement(module_path, imports)`
- `IfStatement(condition, then_block, else_block)`
- `ToolAssignment(agent, tools, operator)`
- `ToolExecution(agent, tool, arguments)`
- `BooleanExpression(left, operator, right)`

**Deliverables:**
- Updated `grammar.lark` with import and control flow syntax
- New AST node classes in `ast_nodes.py`
- Enhanced parser transformer in `parser.py`
- Basic module system in `src/agenticscript/stdlib/`
- Tests for new parser functionality

### Week 2: Tool System & Communication
**Runtime Components:**
- `ToolRegistry` class for managing available tools
- `MessageBus` for inter-agent communication using Python queues
- Enhanced `AgentVal` with threading, tool management, message handling
- Mock tool implementations (`WebSearchTool`, `AgentRoutingTool`, etc.)

**Agent Methods:**
- `ask(message, timeout=None)` - synchronous communication
- `tell(message)` - asynchronous messaging
- `has_tool(tool_name)` - tool availability check
- `execute_tool(tool_name, *args)` - tool execution

**Deliverables:**
- Tool registry system in `src/agenticscript/runtime/tool_registry.py`
- Message bus implementation in `src/agenticscript/runtime/message_bus.py`
- Enhanced Agent class with threading in `src/agenticscript/runtime/agent.py`
- Standard library tools in `src/agenticscript/stdlib/tools.py`
- Comprehensive interpreter updates for new functionality
- Tests for agent communication and tool system

### Week 3: Integration & Enhanced Debugging
**Enhanced Debug Commands:**
- `debug messages` - message flow visualization
- `debug tools` - tool registry and usage statistics
- `debug routes` - agent routing information
- `debug performance` - timing and throughput metrics

**Enhanced Debug Features:**
```bash
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
```

**Deliverables:**
- Enhanced debug commands in `debugger/repl.py`
- Complete Phase 2 feature integration
- Comprehensive test suite covering all new functionality
- Updated documentation and notes
- Performance benchmarks and optimization
- Phase 2 completion commit

## New File Structure (Phase 2 Additions)

```
src/agenticscript/
├── runtime/
│   ├── __init__.py
│   ├── agent.py              # Threading-based Agent class
│   ├── message_bus.py        # Inter-agent communication
│   ├── tool_registry.py      # Plugin system for tools
│   └── local_backend.py      # Local simulation backend
├── stdlib/
│   ├── __init__.py
│   ├── tools.py              # WebSearch, AgentRouting, etc.
│   └── agents.py             # Standard agent types (future)
tests/
├── test_modules.py           # Module system tests
├── test_tools.py             # Tool registry and assignment tests
├── test_communication.py     # Agent communication tests
└── test_integration.py       # End-to-end Phase 2 tests
```

## Testing Strategy

**Module System Tests:**
- Import statement parsing and resolution
- Module loading and error handling
- Tool import functionality

**Communication Tests:**
- Agent.ask() and .tell() methods
- Message bus functionality
- Threading safety and performance

**Tool System Tests:**
- Tool registry operations
- Tool assignment and execution
- Mock tool implementations

**Integration Tests:**
- Complete workflows combining all Phase 2 features
- REPL functionality with new commands
- Error handling and edge cases

## Risk Mitigation

**Threading Complexity:**
- Start with simple thread-per-agent model
- Use Python queues for thread-safe communication
- Comprehensive testing of concurrent operations

**Module System Complexity:**
- Keep import resolution simple for MVP
- Mock external dependencies initially
- Focus on syntax and basic functionality

**Performance Concerns:**
- Profile message passing performance
- Optimize only after functionality is complete
- Use simple data structures initially

## Success Criteria

1. **All Valid Examples Execute Successfully** - Every code sample in this plan runs without errors
2. **Invalid Examples Fail Gracefully** - Error conditions produce clear, helpful error messages
3. **Enhanced REPL Functionality** - New debug commands provide rich, formatted output
4. **Performance Benchmarks** - Threading and messaging perform adequately for 10+ concurrent agents
5. **Comprehensive Test Coverage** - >90% code coverage for all new functionality

This comprehensive plan ensures Phase 2 delivers robust agent communication and tool management while maintaining the "keep it simple" philosophy.