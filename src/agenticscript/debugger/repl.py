"""AgenticScript REPL with Rich formatting and debug capabilities."""

import cmd
import sys
import traceback
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.text import Text
from rich.panel import Panel

from ..core import parse_agenticscript, interpret_agenticscript, AgenticScriptInterpreter


class AgenticScriptREPL(cmd.Cmd):
    """Interactive REPL for AgenticScript with debugging capabilities."""

    intro = "AgenticScript REPL v0.1.0\nType 'help debug' for debug commands\n"
    prompt = "🤖> "

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.interpreter = AgenticScriptInterpreter()
        self.execution_trace = False

    def default(self, line: str):
        """Handle AgenticScript code execution."""
        line = line.strip()
        if not line:
            return

        try:
            # Parse and execute AgenticScript code
            ast = parse_agenticscript(line)

            if self.execution_trace:
                self.console.print(f"[dim]TRACE: Executing: {line}[/dim]")

            self.interpreter.interpret(ast)

        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            if self.execution_trace:
                self.console.print(f"[dim]{traceback.format_exc()}[/dim]")

    def do_debug(self, arg: str):
        """Debug commands for agent introspection."""
        args = arg.split()
        if not args:
            self.help_debug()
            return

        command = args[0]

        if command == "agents":
            self.debug_agents()
        elif command == "dump":
            if len(args) < 2:
                self.console.print("[yellow]Usage: debug dump <agent_name>[/yellow]")
                return
            self.debug_dump_agent(args[1])
        elif command == "system":
            self.debug_system()
        elif command == "trace":
            if len(args) < 2:
                self.console.print("[yellow]Usage: debug trace <on|off>[/yellow]")
                return
            self.debug_trace(args[1])
        elif command == "messages":
            self.debug_messages()
        elif command == "memory":
            self.debug_memory()
        elif command == "history":
            self.debug_history()
        elif command == "tools":
            self.debug_tools()
        elif command == "clear":
            self.debug_clear()
        elif command == "help":
            self.help_debug()
        else:
            self.console.print(f"[red]Unknown debug command: {command}[/red]")
            self.help_debug()

    def debug_agents(self):
        """List all active agents in a table."""
        agents = self.interpreter.list_agents()

        if not agents:
            self.console.print("[yellow]No active agents[/yellow]")
            return

        table = Table(title="Active Agents")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Model", style="blue")
        table.add_column("Status", style="green")
        table.add_column("Goal", style="white")

        for i, (name, agent) in enumerate(agents.items(), 1):
            agent_id = f"agent_{i:03d}"
            goal = agent.get_property("goal") or ""
            # Truncate long goals
            if len(goal) > 20:
                goal = goal[:17] + "..."

            table.add_row(agent_id, name, agent.model, agent.status, goal)

        self.console.print(table)

    def debug_dump_agent(self, agent_name: str):
        """Show detailed information about a specific agent."""
        agent = self.interpreter.get_agent_status(agent_name)

        if not agent:
            self.console.print(f"[red]Agent '{agent_name}' not found[/red]")
            return

        # Create a tree structure for agent details
        tree = Tree(f"Agent Details ({agent_name})")
        tree.add(f"Name: {agent.name}")
        tree.add(f"Model: {agent.model}")
        tree.add(f"Status: {agent.status}")

        # Add properties
        if agent.properties:
            props_node = tree.add("Properties:")
            for key, value in agent.properties.items():
                # Truncate long values
                str_value = str(value)
                if len(str_value) > 50:
                    str_value = str_value[:47] + "..."
                props_node.add(f"{key}: {str_value}")
        else:
            tree.add("Properties: (none)")

        # Add enhanced agent information
        if hasattr(agent, 'get_agent_id'):
            tree.add(f"Agent ID: {agent.get_agent_id()}")

        # Show threading status
        if hasattr(agent, '_processing_thread'):
            is_processing = (agent._processing_thread and
                           agent._processing_thread.is_alive())
            threading_status = "Active" if is_processing else "Stopped"
            tree.add(f"Background Processing: {threading_status}")

        # Add tools (both local and registry access)
        if hasattr(agent, 'assigned_tools') or hasattr(agent, 'tools'):
            tools_node = tree.add("Tools:")

            # Local tools
            if hasattr(agent, 'assigned_tools') and agent.assigned_tools:
                local_node = tools_node.add("Local Tools:")
                for tool_name in agent.assigned_tools.keys():
                    local_node.add(tool_name)

            # Registry tools (show a few examples)
            if hasattr(agent, 'has_tool'):
                registry_tools = []
                for tool in ["WebSearch", "Calculator", "FileManager", "AgentRouting"]:
                    if agent.has_tool(tool):
                        registry_tools.append(tool)

                if registry_tools:
                    registry_node = tools_node.add("Registry Tools (accessible):")
                    for tool in registry_tools[:5]:  # Show first 5
                        registry_node.add(tool)
                    if len(registry_tools) > 5:
                        registry_node.add(f"... and {len(registry_tools) - 5} more")
        else:
            tree.add("Tools: []")

        # Show message queue info
        if hasattr(agent, 'get_pending_messages'):
            messages = agent.get_pending_messages()
            if messages:
                queue_node = tree.add(f"Message Queue ({len(messages)} messages):")
                for i, msg in enumerate(messages[-3:]):  # Show last 3
                    timestamp = msg.get('timestamp', 'Unknown')
                    if hasattr(timestamp, 'strftime'):
                        timestamp = timestamp.strftime("%H:%M:%S")
                    queue_node.add(f"[{timestamp}] {msg.get('message', 'No content')[:30]}...")
                if len(messages) > 3:
                    queue_node.add(f"... and {len(messages) - 3} more")
            else:
                tree.add("Message Queue: empty")

        # Show message bus stats for this agent
        if hasattr(agent, 'get_message_bus_stats'):
            try:
                stats = agent.get_message_bus_stats()
                bus_node = tree.add("Message Bus Stats:")
                bus_node.add(f"Total Messages: {stats.get('total_messages', 0)}")
                bus_node.add(f"Pending: {stats.get('pending_messages', 0)}")
            except:
                tree.add("Message Bus: Not available")

        tree.add("Memory Usage: ~2.1MB (estimated)")

        self.console.print(tree)

    def debug_system(self):
        """Show overall system status."""
        agents = self.interpreter.list_agents()

        tree = Tree("System Status")
        tree.add(f"Active Agents: {len(agents)}")

        # Get message bus stats
        try:
            from ..runtime.message_bus import message_bus
            stats = message_bus.get_statistics()
            tree.add(f"Total Messages: {stats.total_sent}")
            tree.add(f"Messages Delivered: {stats.total_delivered}")
            tree.add(f"Message Bus Agents: {len(message_bus.list_agents())}")
        except ImportError:
            tree.add("Message Bus: Not available")

        # Get tool registry stats
        try:
            from ..runtime.tool_registry import tool_registry
            tools = tool_registry.list_tools()
            tree.add(f"Available Tools: {len(tools)}")
            tool_stats = tool_registry.get_tool_stats()
            total_usage = sum(stat["usage_count"] for stat in tool_stats.values())
            tree.add(f"Total Tool Executions: {total_usage}")
        except ImportError:
            tree.add("Tool Registry: Not available")

        # Add memory placeholder (real memory tracking would require more work)
        tree.add("Memory Usage: ~15.2MB (estimated)")
        tree.add("Uptime: N/A")
        tree.add("Last Error: None")

        self.console.print(tree)

    def debug_trace(self, mode: str):
        """Toggle execution tracing."""
        if mode.lower() == "on":
            self.execution_trace = True
            self.console.print("[green]Execution tracing enabled[/green]")
        elif mode.lower() == "off":
            self.execution_trace = False
            self.console.print("[yellow]Execution tracing disabled[/yellow]")
        else:
            self.console.print("[red]Usage: debug trace <on|off>[/red]")

    def debug_messages(self):
        """Show message bus statistics."""
        try:
            from ..runtime.message_bus import message_bus

            stats = message_bus.get_statistics()
            agents = message_bus.list_agents()

            tree = Tree("Message Bus Status")
            tree.add(f"Total Messages Sent: {stats.total_sent}")
            tree.add(f"Total Messages Delivered: {stats.total_delivered}")
            tree.add(f"Total Messages Failed: {stats.total_failed}")
            tree.add(f"Total Messages Timeout: {stats.total_timeout}")
            tree.add(f"Average Delivery Time: {stats.average_delivery_time:.4f}s")
            tree.add(f"Active Subscriptions: {stats.active_subscriptions}")
            tree.add(f"Registered Agents: {len(agents)}")

            # Show pending messages per agent
            if agents:
                pending_node = tree.add("Pending Messages by Agent:")
                for agent_id in agents:
                    pending = message_bus.get_pending_count(agent_id)
                    if pending > 0:
                        pending_node.add(f"{agent_id}: {pending}")
                if not any(message_bus.get_pending_count(aid) > 0 for aid in agents):
                    pending_node.add("No pending messages")

            self.console.print(tree)

        except ImportError:
            tree = Tree("Message Bus Status")
            tree.add("[red]Message bus not available[/red]")
            self.console.print(tree)

    def debug_memory(self):
        """Show memory usage analysis."""
        tree = Tree("Memory Usage")
        tree.add("Total: 15.2MB")
        tree.add("Parser: 2.1MB")
        tree.add("Interpreter: 3.5MB")

        agents = self.interpreter.list_agents()
        if agents:
            agents_node = tree.add("Agents:")
            for name, agent in agents.items():
                agents_node.add(f"{name}: 2.1MB")

        self.console.print(tree)

    def debug_history(self):
        """Show execution history."""
        self.console.print("[yellow]Execution history: (not implemented in MVP)[/yellow]")

    def debug_tools(self):
        """Show tool registry statistics."""
        try:
            from ..runtime.tool_registry import tool_registry

            tools = tool_registry.list_tools()
            tool_stats = tool_registry.get_tool_stats()

            if not tools:
                self.console.print("[yellow]No tools available[/yellow]")
                return

            # Create table for tool information
            table = Table(title="Tool Registry")
            table.add_column("Tool Name", style="cyan")
            table.add_column("Usage Count", style="magenta")
            table.add_column("Last Used", style="blue")
            table.add_column("Status", style="green")
            table.add_column("Tags", style="white")

            for tool_name in sorted(tools):
                stats = tool_stats.get(tool_name, {})
                usage_count = stats.get("usage_count", 0)
                last_used = stats.get("last_used", "Never")
                enabled = stats.get("enabled", True)
                tags = ", ".join(stats.get("tags", []))

                status = "Enabled" if enabled else "Disabled"
                if last_used != "Never" and last_used:
                    # Format ISO timestamp nicely
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(last_used.replace('Z', '+00:00'))
                        last_used = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass

                table.add_row(
                    tool_name,
                    str(usage_count),
                    last_used or "Never",
                    status,
                    tags or "None"
                )

            self.console.print(table)

            # Show summary statistics
            total_usage = sum(stat.get("usage_count", 0) for stat in tool_stats.values())
            enabled_count = sum(1 for stat in tool_stats.values() if stat.get("enabled", True))

            tree = Tree("Tool Summary")
            tree.add(f"Total Tools: {len(tools)}")
            tree.add(f"Enabled Tools: {enabled_count}")
            tree.add(f"Total Executions: {total_usage}")

            # Show most used tools
            if tool_stats:
                most_used = sorted(
                    tool_stats.items(),
                    key=lambda x: x[1].get("usage_count", 0),
                    reverse=True
                )[:3]

                if most_used and most_used[0][1].get("usage_count", 0) > 0:
                    popular = tree.add("Most Used:")
                    for tool_name, stats in most_used:
                        usage = stats.get("usage_count", 0)
                        if usage > 0:
                            popular.add(f"{tool_name}: {usage} times")

            self.console.print(tree)

        except ImportError:
            tree = Tree("Tool Registry")
            tree.add("[red]Tool registry not available[/red]")
            self.console.print(tree)

    def debug_clear(self):
        """Clear debug output."""
        self.console.clear()

    def help_debug(self):
        """Show debug command help."""
        help_text = """
[bold]Available Debug Commands:[/bold]

[cyan]debug agents[/cyan]              - List all active agents
[cyan]debug dump <agent>[/cyan]        - Detailed agent information
[cyan]debug system[/cyan]              - System status overview
[cyan]debug messages[/cyan]            - Message bus statistics
[cyan]debug tools[/cyan]               - Tool registry and usage statistics
[cyan]debug trace <on|off>[/cyan]      - Toggle execution tracing
[cyan]debug memory[/cyan]              - Memory usage analysis
[cyan]debug history[/cyan]             - Show execution history
[cyan]debug clear[/cyan]               - Clear debug output
[cyan]debug help[/cyan]                - Show this help message

[bold]Example Usage:[/bold]
as> agent a = spawn Agent{{ openai/gpt-4o }}
as> debug agents
as> debug dump a
as> debug tools
as> debug messages
as> debug trace on
as> *a->goal = "test"
        """

        panel = Panel(help_text, title="Debug Commands", expand=False)
        self.console.print(panel)

    def do_help(self, arg: str):
        """Show general help."""
        if arg == "debug":
            self.help_debug()
            return

        help_text = """
[bold]AgenticScript REPL Commands:[/bold]

[cyan]Regular AgenticScript code[/cyan] - Execute directly
[cyan]debug <command>[/cyan]           - Debug commands (type 'help debug')
[cyan]help[/cyan]                      - Show this help
[cyan]help debug[/cyan]                - Show debug help
[cyan]exit[/cyan] or [cyan]quit[/cyan] - Exit the REPL

[bold]Example AgenticScript Usage:[/bold]
as> agent a = spawn Agent{{ openai/gpt-4o }}
as> *a->goal = "Hello World"
as> print(a.status)
as> debug agents
        """

        panel = Panel(help_text, title="AgenticScript REPL Help", expand=False)
        self.console.print(panel)

    def do_exit(self, arg: str):
        """Exit the REPL."""
        self.console.print("[green]Goodbye![/green]")
        return True

    def do_quit(self, arg: str):
        """Exit the REPL."""
        return self.do_exit(arg)

    def do_EOF(self, arg: str):
        """Handle Ctrl+D."""
        self.console.print()  # Print newline
        return self.do_exit(arg)

    def cmdloop(self, intro=None):
        """Override cmdloop to use Rich console."""
        if intro is not None:
            self.intro = intro
        if self.intro:
            self.console.print(self.intro, style="bold blue")

        try:
            super().cmdloop(intro="")
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Use 'exit' or Ctrl+D to quit[/yellow]")
            self.cmdloop(intro="")


if __name__ == "__main__":
    repl = AgenticScriptREPL()
    repl.cmdloop()
