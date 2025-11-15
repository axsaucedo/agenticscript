"""Tests for enhanced AgentVal class with threading and tool management."""

import sys
import os
import time
import threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agenticscript.core.interpreter import AgentVal
from agenticscript.runtime.tool_registry import tool_registry
from agenticscript.runtime.message_bus import message_bus
from agenticscript.stdlib.tools import WebSearchTool


def test_enhanced_agent_creation():
    """Test enhanced agent creation with runtime integration."""
    agent = AgentVal("enhanced_agent", "gpt-4o")

    # Test basic properties
    assert agent.name == "enhanced_agent"
    assert agent.model == "gpt-4o"
    assert agent.status == "idle"

    # Test runtime integration
    assert agent.get_agent_id().startswith("enhanced_agent_")
    assert hasattr(agent, '_tool_registry')
    assert hasattr(agent, '_message_bus')
    assert hasattr(agent, '_lock')

    # Test message bus registration
    agents = message_bus.list_agents()
    assert agent.get_agent_id() in agents

    # Cleanup
    agent.cleanup()


def test_agent_tool_registry_integration():
    """Test agent integration with tool registry."""
    agent = AgentVal("tool_test_agent", "gpt-4o")

    try:
        # Test has_tool with global registry
        assert agent.has_tool("WebSearch")  # Should be available from stdlib
        assert not agent.has_tool("NonExistentTool")

        # Test tool registration
        success = agent.register_with_tool_registry("WebSearch")
        assert success

        # Test tool execution through registry
        result = agent.execute_tool("WebSearch", "test query")
        assert "Mock search results for: test query" in result

        # Test registry-based execution
        result2 = agent.execute_tool("Calculator", "2 + 2")
        assert "Mock calculation result for: 2 + 2" in result2

    finally:
        agent.cleanup()


def test_agent_message_bus_integration():
    """Test agent integration with message bus."""
    agent1 = AgentVal("sender_agent", "gpt-4o")
    agent2 = AgentVal("receiver_agent", "gpt-4o")

    try:
        # Test tell method with message bus
        agent1.tell("Hello from tell!")

        # Check message was sent through bus
        pending = message_bus.get_pending_count(agent1.get_agent_id())
        assert pending > 0

        # Test ask method logs interaction
        response = agent1.ask("Hello from ask!")
        assert "Hello from sender_agent!" in response

        # Check message bus statistics
        stats = agent1.get_message_bus_stats()
        assert "agent_id" in stats
        assert "total_messages" in stats
        assert stats["agent_id"] == agent1.get_agent_id()

    finally:
        agent1.cleanup()
        agent2.cleanup()


def test_agent_background_processing():
    """Test agent background message processing."""
    agent = AgentVal("bg_agent", "gpt-4o")

    try:
        # Start background processing
        assert agent.start_background_processing()
        assert not agent.start_background_processing()  # Should fail if already running

        # Send a message through message bus
        message_id = message_bus.send_message(
            sender="test_sender",
            recipient=agent.get_agent_id(),
            content="Background test message",
            message_type="tell"
        )
        assert message_id is not None

        # Wait a bit for background processing
        time.sleep(0.2)

        # Check if message was processed
        messages = agent.get_pending_messages()
        processed_message = next(
            (msg for msg in messages if msg["message"] == "Background test message"),
            None
        )
        assert processed_message is not None

        # Stop background processing
        assert agent.stop_background_processing()
        assert not agent.stop_background_processing()  # Should fail if not running

    finally:
        agent.cleanup()


def test_agent_threading_features():
    """Test agent threading features (background processing, thread safety)."""
    agent = AgentVal("thread_agent", "gpt-4o")

    try:
        # Test that background processing can start and stop
        assert agent.start_background_processing()
        assert not agent.start_background_processing()  # Should fail if already running

        # Test basic threading safety by accessing properties concurrently
        def concurrent_access():
            for i in range(10):
                _ = agent.status
                _ = agent.get_agent_id()
                _ = agent.has_tool("WebSearch")
                time.sleep(0.001)

        # Start multiple threads accessing agent concurrently
        threads = [threading.Thread(target=concurrent_access) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Stop background processing
        assert agent.stop_background_processing()
        assert not agent.stop_background_processing()  # Should fail if not running

    finally:
        agent.cleanup()


def test_agent_threading_safety():
    """Test agent thread safety with concurrent operations."""
    agent = AgentVal("thread_agent", "gpt-4o")

    try:
        results = []
        errors = []

        def worker_task(task_id):
            try:
                # Perform various operations concurrently
                response = agent.ask(f"Task {task_id}")
                results.append(response)

                agent.tell(f"Tell message {task_id}")

                if agent.has_tool("WebSearch"):
                    tool_result = agent.execute_tool("WebSearch", f"query {task_id}")
                    results.append(tool_result)

            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_task, args=(i,))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) >= 5  # At least one result per thread

    finally:
        agent.cleanup()


def test_agent_status_changes():
    """Test agent status changes during operations."""
    agent = AgentVal("status_agent", "gpt-4o")

    try:
        # Initial status
        assert agent.status == "idle"

        # Test status during ask
        def check_status_during_ask():
            response = agent.ask("busy message")
            return response

        response = check_status_during_ask()
        assert "was busy but processed" in response
        assert agent.status == "idle"  # Should return to idle

        # Test status during tool execution
        if agent.has_tool("WebSearch"):
            original_status = agent.status
            result = agent.execute_tool("WebSearch", "test")
            assert agent.status == original_status  # Should restore status

    finally:
        agent.cleanup()


def test_agent_cleanup():
    """Test agent cleanup functionality."""
    agent = AgentVal("cleanup_agent", "gpt-4o")
    agent_id = agent.get_agent_id()

    # Start background processing
    agent.start_background_processing()

    # Verify agent is registered
    assert agent_id in message_bus.list_agents()

    # Cleanup
    agent.cleanup()

    # Verify cleanup
    assert agent_id not in message_bus.list_agents()


def test_agent_tool_assignment_with_registry():
    """Test agent tool assignment working with registry."""
    agent = AgentVal("assignment_agent", "gpt-4o")

    try:
        # Test local tool assignment
        web_tool = WebSearchTool()
        agent.assign_tool("LocalWebSearch", web_tool)

        # Should have both local and registry tools
        assert agent.has_tool("LocalWebSearch")  # Local
        assert agent.has_tool("WebSearch")       # Registry

        # Test execution of both
        local_result = agent.execute_tool("LocalWebSearch", "local query")
        registry_result = agent.execute_tool("WebSearch", "registry query")

        assert "Mock search results for: local query" in local_result
        assert "Mock search results for: registry query" in registry_result

    finally:
        agent.cleanup()


def test_agent_error_handling():
    """Test agent error handling in various scenarios."""
    agent = AgentVal("error_agent", "gpt-4o")

    try:
        # Test tool execution error
        try:
            agent.assigned_tools.clear()  # Remove all local tools
            # This should still work through registry
            result = agent.execute_tool("WebSearch", "test")
            assert result is not None
        except Exception as e:
            assert False, f"Should not raise error for registry tool: {e}"

        # Test non-existent tool
        try:
            agent.execute_tool("NonExistentTool", "test")
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "does not have access to tool" in str(e)

    finally:
        agent.cleanup()


def test_multiple_agents_interaction():
    """Test interaction between multiple enhanced agents."""
    agent1 = AgentVal("multi_agent1", "gpt-4o")
    agent2 = AgentVal("multi_agent2", "gpt-4o")

    try:
        # Start background processing for both
        agent1.start_background_processing()
        agent2.start_background_processing()

        # Send message from agent1 to agent2
        message_id = message_bus.send_message(
            sender=agent1.get_agent_id(),
            recipient=agent2.get_agent_id(),
            content="Hello from agent1",
            message_type="tell"
        )

        # Wait for processing
        time.sleep(0.2)

        # Check agent2 received the message
        messages = agent2.get_pending_messages()
        received = any(msg["message"] == "Hello from agent1" for msg in messages)
        assert received

        # Check message bus history
        history = message_bus.get_message_history()
        sent_message = next(
            (msg for msg in history if msg.id == message_id),
            None
        )
        assert sent_message is not None
        assert sent_message.sender == agent1.get_agent_id()
        assert sent_message.recipient == agent2.get_agent_id()

    finally:
        agent1.cleanup()
        agent2.cleanup()


if __name__ == "__main__":
    # Clear any existing state
    message_bus.clear_history()
    # Don't clear tool registry as it removes stdlib tools needed for tests

    test_enhanced_agent_creation()
    print("✓ Enhanced agent creation works")

    test_agent_tool_registry_integration()
    print("✓ Agent tool registry integration works")

    test_agent_message_bus_integration()
    print("✓ Agent message bus integration works")

    test_agent_background_processing()
    print("✓ Agent background processing works")

    test_agent_threading_features()
    print("✓ Agent threading features work")

    test_agent_threading_safety()
    print("✓ Agent threading safety works")

    test_agent_status_changes()
    print("✓ Agent status changes work")

    test_agent_cleanup()
    print("✓ Agent cleanup works")

    test_agent_tool_assignment_with_registry()
    print("✓ Agent tool assignment with registry works")

    test_agent_error_handling()
    print("✓ Agent error handling works")

    test_multiple_agents_interaction()
    print("✓ Multiple agents interaction works")

    print("All enhanced agent tests passed!")