"""AgenticScript - An agentic-first programming language."""

__version__ = "0.1.0"

def main() -> None:
    """Main entry point for AgenticScript CLI."""
    from .debugger.repl import AgenticScriptREPL

    repl = AgenticScriptREPL()
    repl.cmdloop()
