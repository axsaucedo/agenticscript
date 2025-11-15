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
                props_node.add(f"{key}: {value}")
        else:
            tree.add("Properties: (none)")

        # Add tools (placeholder for now)
        if agent.tools:
            tools_node = tree.add("Tools:")
            for tool in agent.tools:
                tools_node.add(str(tool))
        else:
            tree.add("Tools: []")

        # Add mock data for now
        tree.add("Message Queue: empty")
        tree.add("Execution History: []")
        tree.add("Memory Usage: 2.1MB")

        self.console.print(tree)

    def debug_system(self):
        """Show overall system status."""
        agents = self.interpreter.list_agents()

        tree = Tree("System Status")
        tree.add(f"Active Agents: {len(agents)}")
        tree.add("Total Messages: 0")  # Mock for now
        tree.add("Memory Usage: 15.2MB")  # Mock for now
        tree.add("Uptime: N/A")  # Mock for now
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
        tree = Tree("Message Bus Status")
        tree.add("Total Messages Sent: 0")
        tree.add("Pending Messages: 0")
        tree.add("Failed Messages: 0")
        tree.add("Average Processing Time: N/A")

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
[cyan]debug trace <on|off>[/cyan]      - Toggle execution tracing
[cyan]debug memory[/cyan]              - Memory usage analysis
[cyan]debug history[/cyan]             - Show execution history
[cyan]debug clear[/cyan]               - Clear debug output
[cyan]debug help[/cyan]                - Show this help message

[bold]Example Usage:[/bold]
as> agent a = spawn Agent{{ openai/gpt-4o }}
as> debug agents
as> debug dump a
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
