"""Comprehensive integration tests for Phase 2 features.

Tests the full integration of:
- Lark grammar extensions (imports, tools, control flow)
- AST nodes and parser transformer
- Module system and stdlib
- Tool registry with plugin pattern
- Agent communication methods
- Message bus system
- Enhanced Agent class with threading
- Standard library tools with message bus integration
- Enhanced debug commands
- Message flow visualization and statistics
"""

import sys
import os
import time
import threading
import io
from contextlib import redirect_stdout
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agenticscript.core.parser import parse_agenticscript
from agenticscript.core.interpreter import AgenticScriptInterpreter
from agenticscript.debugger.repl import AgenticScriptREPL
from agenticscript.runtime.message_bus import message_bus
from agenticscript.runtime.tool_registry import tool_registry
from agenticscript.core.module_system import module_system


def test_end_to_end_agent_workflow():
    """Test complete end-to-end agent workflow with all Phase 2 features."""

    # Complex AgenticScript code using all major features
    code = '''
import agenticscript.stdlib.tools { WebSearch, AgentRouting }
import agenticscript.stdlib.agents { SupervisorAgent }

agent coordinator = spawn Agent{ openai/gpt-4o }
agent researcher = spawn Agent{ claude/sonnet }
agent analyzer = spawn Agent{ gemini/pro }

*coordinator->goal = "Coordinate research and analysis tasks"
*researcher->goal = "Research information using web search"
*analyzer->goal = "Analyze research data"

*coordinator->tools = { AgentRouting{ researcher, analyzer } }
*researcher->tools = { WebSearch }

if coordinator.has_tool("AgentRouting") {
    print("Coordinator has routing capability")
}

if researcher.has_tool("WebSearch") {
    search_result = researcher.execute_tool("WebSearch", "artificial intelligence trends")
    print("Research result:")
    print(search_result)
}

coordination_response = coordinator.ask("What is your current status?")
print("Coordinator status:")
print(coordination_response)

researcher.tell("Start research on AI trends")
analyzer.tell("Prepare for data analysis")
'''

    # Test parsing
    try:
        ast = parse_agenticscript(code)
        assert ast is not None
    except Exception as e:
        assert False, f"Parsing failed: {e}"

    # Test interpretation
    interpreter = AgenticScriptInterpreter()

    # Capture output
    f = io.StringIO()
    with redirect_stdout(f):
        try:
            interpreter.interpret(ast)
        except Exception as e:
            assert False, f"Interpretation failed: {e}"

    output = f.getvalue()

    # Verify execution results
    assert "Agent 'coordinator' spawned successfully" in output
    assert "Agent 'researcher' spawned successfully" in output
    assert "Agent 'analyzer' spawned successfully" in output

    assert "Coordinator has routing capability" in output
    assert "Research result:" in output
    assert "Mock search results" in output
    assert "Coordinator status:" in output
    assert "Hello from coordinator!" in output

    # Verify agents were created with enhanced features
    coordinator = interpreter.get_agent_status("coordinator")
    researcher = interpreter.get_agent_status("researcher")
    analyzer = interpreter.get_agent_status("analyzer")

    assert coordinator is not None
    assert researcher is not None
    assert analyzer is not None

    # Verify agent properties
    assert coordinator.get_property("goal") == "Coordinate research and analysis tasks"
    assert researcher.get_property("goal") == "Research information using web search"
    assert analyzer.get_property("goal") == "Analyze research data"

    # Verify enhanced agent features
    assert hasattr(coordinator, 'get_agent_id')
    assert hasattr(researcher, '_message_bus')
    assert hasattr(analyzer, '_tool_registry')

    # Verify tools were assigned correctly
    assert coordinator.has_tool("AgentRouting")
    assert researcher.has_tool("WebSearch")

    # Verify message queues have messages
    researcher_messages = researcher.get_pending_messages()
    analyzer_messages = analyzer.get_pending_messages()

    assert len(researcher_messages) > 0
    assert len(analyzer_messages) > 0

    # Check message content
    research_msg = next((m for m in researcher_messages if "research on AI" in m["message"]), None)
    analysis_msg = next((m for m in analyzer_messages if "data analysis" in m["message"]), None)

    assert research_msg is not None
    assert analysis_msg is not None


def test_multi_agent_communication_integration():
    """Test complex multi-agent communication using message bus."""

    # Create a scenario with multiple agents communicating
    code = '''
agent sender = spawn Agent{ openai/gpt-4o }
agent receiver1 = spawn Agent{ claude/sonnet }
agent receiver2 = spawn Agent{ gemini/pro }

*sender->goal = "Send messages to other agents"
*receiver1->goal = "Receive and process messages"
*receiver2->goal = "Receive and respond to requests"
'''

    interpreter = AgenticScriptInterpreter()
    ast = parse_agenticscript(code)

    f = io.StringIO()
    with redirect_stdout(f):
        interpreter.interpret(ast)

    # Get agents
    sender = interpreter.get_agent_status("sender")
    receiver1 = interpreter.get_agent_status("receiver1")
    receiver2 = interpreter.get_agent_status("receiver2")

    # Test agent communication methods
    response1 = sender.ask("Hello from sender")
    assert "Hello from sender!" in response1

    sender.tell("Async message to sender")
    receiver1.tell("Message for receiver1")
    receiver2.tell("Message for receiver2")

    # Verify messages were queued
    sender_msgs = sender.get_pending_messages()
    receiver1_msgs = receiver1.get_pending_messages()
    receiver2_msgs = receiver2.get_pending_messages()

    assert len(sender_msgs) > 0
    assert len(receiver1_msgs) > 0
    assert len(receiver2_msgs) > 0

    # Test message bus integration
    stats = message_bus.get_statistics()
    assert stats.total_sent > 0

    # Test agent routing tool integration
    routing_tool = tool_registry.get_tool_instance("AgentRouting")
    if routing_tool:
        # Test routing to specific agent
        result = routing_tool.execute("Routed message", "sender", sender.get_agent_id())
        assert "Message routed to agent" in result


def test_tool_registry_and_agent_integration():
    """Test tool registry integration with agents and module system."""

    # Clear registry and re-register tools
    original_tools = tool_registry.list_tools()

    # Test tool availability
    assert "WebSearch" in original_tools
    assert "Calculator" in original_tools
    assert "AgentRouting" in original_tools

    # Create agent and test tool integration
    code = '''
agent tool_user = spawn Agent{ openai/gpt-4o }
*tool_user->goal = "Test tool integration"
'''

    interpreter = AgenticScriptInterpreter()
    ast = parse_agenticscript(code)
    interpreter.interpret(ast)

    agent = interpreter.get_agent_status("tool_user")
    assert agent is not None

    # Test registry tools through agent
    assert agent.has_tool("WebSearch")
    assert agent.has_tool("Calculator")
    assert agent.has_tool("FileManager")

    # Test tool execution through agent
    web_result = agent.execute_tool("WebSearch", "integration test")
    calc_result = agent.execute_tool("Calculator", "2 + 2")

    assert "Mock search results for: integration test" in web_result
    assert "Mock calculation result for: 2 + 2" in calc_result

    # Verify tool statistics were updated
    tool_stats = tool_registry.get_tool_stats()
    web_stats = tool_stats.get("WebSearch", {})
    calc_stats = tool_stats.get("Calculator", {})

    assert web_stats.get("usage_count", 0) > 0
    assert calc_stats.get("usage_count", 0) > 0

    # Test local tool assignment
    from agenticscript.stdlib.tools import WebSearchTool
    local_tool = WebSearchTool()
    agent.assign_tool("LocalWebSearch", local_tool)

    assert agent.has_tool("LocalWebSearch")
    local_result = agent.execute_tool("LocalWebSearch", "local test")
    assert "Mock search results for: local test" in local_result


def test_threading_and_background_processing():
    """Test agent threading capabilities and background processing."""

    code = '''
agent threaded_agent = spawn Agent{ openai/gpt-4o }
*threaded_agent->goal = "Test threading capabilities"
'''

    interpreter = AgenticScriptInterpreter()
    ast = parse_agenticscript(code)
    interpreter.interpret(ast)

    agent = interpreter.get_agent_status("threaded_agent")
    assert agent is not None

    # Test background processing start/stop
    assert agent.start_background_processing()
    time.sleep(0.1)  # Let background processing start

    # Send message through message bus to agent
    message_id = message_bus.send_message(
        sender="test_system",
        recipient=agent.get_agent_id(),
        content="Background test message",
        message_type="tell"
    )
    assert message_id is not None

    # Give time for background processing
    time.sleep(0.2)

    # Check if message was processed
    messages = agent.get_pending_messages()
    processed = any(m["message"] == "Background test message" for m in messages)

    # Stop background processing
    assert agent.stop_background_processing()

    # Test concurrent operations
    results = []
    errors = []

    def concurrent_task(task_id):
        try:
            response = agent.ask(f"Concurrent task {task_id}")
            results.append(response)
        except Exception as e:
            errors.append(e)

    # Start multiple concurrent operations
    threads = []
    for i in range(3):
        thread = threading.Thread(target=concurrent_task, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for completion
    for thread in threads:
        thread.join()

    # Verify concurrent operations succeeded
    assert len(errors) == 0, f"Concurrent operations failed: {errors}"
    assert len(results) == 3

    # Cleanup
    agent.cleanup()


def test_debug_commands_integration():
    """Test enhanced debug commands with full system integration."""

    # Create a complex scenario
    code = '''
import agenticscript.stdlib.tools { WebSearch, Calculator }

agent debug_agent1 = spawn Agent{ openai/gpt-4o }
agent debug_agent2 = spawn Agent{ claude/sonnet }

*debug_agent1->goal = "Debug test agent 1"
*debug_agent2->goal = "Debug test agent 2"

*debug_agent1->tools = { WebSearch }
*debug_agent2->tools = { Calculator }

print(debug_agent1.ask("Status check"))
debug_agent2.tell("Debug message")

result1 = debug_agent1.execute_tool("WebSearch", "debug test")
result2 = debug_agent2.execute_tool("Calculator", "debug calculation")
'''

    interpreter = AgenticScriptInterpreter()
    repl = AgenticScriptREPL()
    repl.interpreter = interpreter  # Use same interpreter

    ast = parse_agenticscript(code)

    f = io.StringIO()
    with redirect_stdout(f):
        interpreter.interpret(ast)

    # Test all debug commands
    debug_outputs = []

    debug_commands = [
        repl.debug_agents,
        repl.debug_system,
        repl.debug_messages,
        repl.debug_tools,
        repl.debug_flow,
        repl.debug_stats
    ]

    for debug_cmd in debug_commands:
        f = io.StringIO()
        with redirect_stdout(f):
            debug_cmd()
        debug_outputs.append(f.getvalue())

    # Verify debug commands show expected information
    agents_output = debug_outputs[0]
    assert "debug_agent1" in agents_output
    assert "debug_agent2" in agents_output
    assert "openai/gpt-4o" in agents_output

    system_output = debug_outputs[1]
    assert "Active Agents: 2" in system_output
    assert "Available Tools:" in system_output

    messages_output = debug_outputs[2]
    assert "Message Bus Status" in messages_output
    assert "Total Messages Sent:" in messages_output

    tools_output = debug_outputs[3]
    assert "Tool Registry" in tools_output
    assert "WebSearch" in tools_output
    assert "Calculator" in tools_output

    flow_output = debug_outputs[4]
    assert "Message Flow Analysis" in flow_output or "No message history" in flow_output

    stats_output = debug_outputs[5]
    assert "System Statistics" in stats_output
    assert "Tool Usage Patterns:" in stats_output

    # Test debug dump on specific agent
    f = io.StringIO()
    with redirect_stdout(f):
        repl.debug_dump_agent("debug_agent1")

    dump_output = f.getvalue()
    assert "Agent Details (debug_agent1)" in dump_output
    assert "debug_agent1" in dump_output
    assert "openai/gpt-4o" in dump_output
    assert "goal: Debug test agent 1" in dump_output


def test_import_and_module_system_integration():
    """Test import statements and module system integration."""

    code = '''
import agenticscript.stdlib.tools { WebSearch, Calculator, AgentRouting }
import agenticscript.stdlib.agents { SupervisorAgent }

agent importer = spawn Agent{ openai/gpt-4o }
*importer->goal = "Test import functionality"
*importer->tools = { WebSearch, Calculator }

if importer.has_tool("WebSearch") {
    web_result = importer.execute_tool("WebSearch", "import test")
    print("Import test result:")
    print(web_result)
}

if importer.has_tool("Calculator") {
    calc_result = importer.execute_tool("Calculator", "import calc test")
    print("Import calc result:")
    print(calc_result)
}
'''

    # Test module system can resolve imports
    imports = module_system.import_module(
        ["agenticscript", "stdlib", "tools"],
        ["WebSearch", "Calculator", "AgentRouting"]
    )

    assert "WebSearch" in imports
    assert "Calculator" in imports
    assert "AgentRouting" in imports

    # Test parsing and interpretation
    interpreter = AgenticScriptInterpreter()
    ast = parse_agenticscript(code)

    f = io.StringIO()
    with redirect_stdout(f):
        interpreter.interpret(ast)

    output = f.getvalue()

    # Verify imports work in execution
    assert "Import test result:" in output
    assert "Mock search results for: import test" in output
    assert "Import calc result:" in output
    assert "Mock calculation result for: import calc test" in output

    # Verify agent has tools from imports
    agent = interpreter.get_agent_status("importer")
    assert agent is not None
    assert agent.has_tool("WebSearch")
    assert agent.has_tool("Calculator")


def test_control_flow_integration():
    """Test control flow (if/else) integration with agent operations."""

    code = '''
agent controller = spawn Agent{ openai/gpt-4o }
*controller->goal = "Test control flow"

if controller.status == "idle" {
    print("Agent is idle, ready for tasks")
    controller.tell("Starting tasks")
}

if controller.has_tool("WebSearch") {
    print("Agent has web search capability")
} else {
    print("Agent lacks web search capability")
}

status_response = controller.ask("What is your status?")
if "idle" in status_response {
    print("Agent confirms idle status")
}
'''

    interpreter = AgenticScriptInterpreter()
    ast = parse_agenticscript(code)

    f = io.StringIO()
    with redirect_stdout(f):
        interpreter.interpret(ast)

    output = f.getvalue()

    # Verify control flow executed correctly
    assert "Agent is idle, ready for tasks" in output
    assert "Agent has web search capability" in output  # Should have registry tools
    assert "Agent confirms idle status" in output

    # Verify agent received tell message
    agent = interpreter.get_agent_status("controller")
    messages = agent.get_pending_messages()
    assert any(m["message"] == "Starting tasks" for m in messages)


def test_performance_and_reliability():
    """Test system performance and reliability under load."""

    # Create multiple agents
    agents_code = '''
agent perf1 = spawn Agent{ openai/gpt-4o }
agent perf2 = spawn Agent{ claude/sonnet }
agent perf3 = spawn Agent{ gemini/pro }
agent perf4 = spawn Agent{ openai/gpt-3.5 }

*perf1->goal = "Performance test 1"
*perf2->goal = "Performance test 2"
*perf3->goal = "Performance test 3"
*perf4->goal = "Performance test 4"
'''

    interpreter = AgenticScriptInterpreter()
    ast = parse_agenticscript(agents_code)
    interpreter.interpret(ast)

    agents = [
        interpreter.get_agent_status("perf1"),
        interpreter.get_agent_status("perf2"),
        interpreter.get_agent_status("perf3"),
        interpreter.get_agent_status("perf4")
    ]

    # Test concurrent operations
    results = []
    start_time = time.time()

    def agent_operations(agent, agent_id):
        try:
            # Multiple operations per agent
            for i in range(5):
                response = agent.ask(f"Operation {i}")
                agent.tell(f"Tell message {i}")
                if agent.has_tool("WebSearch"):
                    tool_result = agent.execute_tool("WebSearch", f"query {i}")
                    results.append((agent_id, i, len(tool_result)))
        except Exception as e:
            results.append(("error", agent_id, str(e)))

    # Start concurrent operations
    threads = []
    for i, agent in enumerate(agents):
        if agent:
            thread = threading.Thread(target=agent_operations, args=(agent, i))
            threads.append(thread)
            thread.start()

    # Wait for completion
    for thread in threads:
        thread.join()

    end_time = time.time()
    duration = end_time - start_time

    # Verify performance
    assert duration < 10.0, f"Operations took too long: {duration:.2f}s"

    # Check for errors
    errors = [r for r in results if r[0] == "error"]
    assert len(errors) == 0, f"Errors occurred: {errors}"

    # Verify all operations completed
    successful_ops = [r for r in results if r[0] != "error"]
    assert len(successful_ops) >= 16, f"Expected at least 16 operations, got {len(successful_ops)}"

    # Test message bus performance
    bus_stats = message_bus.get_statistics()
    assert bus_stats.total_sent > 0
    assert bus_stats.average_delivery_time >= 0

    # Test tool registry performance
    tool_stats = tool_registry.get_tool_stats()
    total_usage = sum(stat.get("usage_count", 0) for stat in tool_stats.values())
    assert total_usage > 0

    # Cleanup
    for agent in agents:
        if agent:
            agent.cleanup()


if __name__ == "__main__":
    # Clear state before tests
    message_bus.clear_history()

    print("Running comprehensive Phase 2 integration tests...")

    test_end_to_end_agent_workflow()
    print("✓ End-to-end agent workflow integration")

    test_multi_agent_communication_integration()
    print("✓ Multi-agent communication integration")

    test_tool_registry_and_agent_integration()
    print("✓ Tool registry and agent integration")

    test_threading_and_background_processing()
    print("✓ Threading and background processing integration")

    test_debug_commands_integration()
    print("✓ Debug commands integration")

    test_import_and_module_system_integration()
    print("✓ Import and module system integration")

    test_control_flow_integration()
    print("✓ Control flow integration")

    test_performance_and_reliability()
    print("✓ Performance and reliability testing")

    print("\n🎉 All Phase 2 integration tests passed!")
    print("✅ AgenticScript Phase 2 implementation is fully functional!")