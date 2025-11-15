"""Standard library for AgenticScript."""

# Module registry for import resolution
STDLIB_MODULES = {
    "agenticscript.stdlib.tools": {
        "WebSearch": "agenticscript.stdlib.tools.WebSearchTool",
        "AgentRouting": "agenticscript.stdlib.tools.AgentRoutingTool",
        "FileManager": "agenticscript.stdlib.tools.FileManagerTool",
        "Calculator": "agenticscript.stdlib.tools.CalculatorTool",
    },
    "agenticscript.stdlib.agents": {
        "SupervisorAgent": "agenticscript.stdlib.agents.SupervisorAgent",
    }
}

def resolve_import(module_path: str, import_name: str):
    """Resolve an import to its implementation class."""
    if module_path in STDLIB_MODULES:
        if import_name in STDLIB_MODULES[module_path]:
            return STDLIB_MODULES[module_path][import_name]

    raise ImportError(f"Cannot import {import_name} from {module_path}")

__all__ = ["STDLIB_MODULES", "resolve_import"]