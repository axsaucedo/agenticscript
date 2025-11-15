"""Tree-walking interpreter for AgenticScript."""

from typing import Any, Dict, Optional
from . import ast_nodes as ast


class AgenticScriptValue:
    """Base class for runtime values in AgenticScript."""
    pass


class StringVal(AgenticScriptValue):
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'StringVal("{self.value}")'


class NumberVal(AgenticScriptValue):
    def __init__(self, value: float | int):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'NumberVal({self.value})'


class BooleanVal(AgenticScriptValue):
    def __init__(self, value: bool):
        self.value = value

    def __str__(self):
        return "true" if self.value else "false"

    def __repr__(self):
        return f'BooleanVal({self.value})'


class AgentVal(AgenticScriptValue):
    """Runtime representation of an AgenticScript agent."""

    def __init__(self, name: str, model: str, **config):
        self.name = name
        self.model = model
        self.status = "idle"  # idle, active, error
        self.properties = {}
        self.tools = []
        self.assigned_tools = {}  # tool_name -> tool_instance mapping
        self.message_queue = []  # simple queue for async messages

        # Apply configuration
        for key, value in config.items():
            self.properties[key] = value

    def get_property(self, name: str) -> Any:
        """Get agent property value."""
        if name == "status":
            return self.status
        elif name == "model":
            return self.model
        elif name == "name":
            return self.name
        elif name == "tools":
            return list(self.assigned_tools.keys())
        else:
            return self.properties.get(name)

    def set_property(self, name: str, value: Any):
        """Set agent property value."""
        if name in ("status", "model", "name"):
            # These are read-only system properties for now
            raise RuntimeError(f"Cannot modify system property '{name}'")
        else:
            self.properties[name] = value

    def ask(self, message: str, timeout: float = None) -> str:
        """Send a synchronous message to this agent and wait for response.

        Args:
            message: Message to send
            timeout: Optional timeout in seconds

        Returns:
            Response string from the agent
        """
        # Mock implementation for Phase 2
        # In a real implementation, this would route through the message bus
        import time
        time.sleep(0.01)  # Simulate processing time

        # Update status during processing
        old_status = self.status
        self.status = "processing"

        # Mock response based on message content
        if "error" in message.lower():
            response = f"Error handling: {message}"
        elif "status" in message.lower():
            response = f"Agent {self.name} status: {old_status}"
        elif "hello" in message.lower():
            response = f"Hello from {self.name}!"
        else:
            response = f"Agent {self.name} processed: {message}"

        # Restore status
        self.status = old_status
        return response

    def tell(self, message: str) -> None:
        """Send an asynchronous message to this agent.

        Args:
            message: Message to send
        """
        # Mock implementation - just add to message queue
        import datetime
        self.message_queue.append({
            "message": message,
            "timestamp": datetime.datetime.now(),
            "sender": "system"  # Will be updated when message bus is implemented
        })

    def has_tool(self, tool_name: str) -> bool:
        """Check if this agent has access to a specific tool.

        Args:
            tool_name: Name of the tool to check

        Returns:
            True if agent has the tool, False otherwise
        """
        return tool_name in self.assigned_tools

    def execute_tool(self, tool_name: str, *args, **kwargs) -> Any:
        """Execute a tool with given arguments.

        Args:
            tool_name: Name of the tool to execute
            *args: Positional arguments for tool execution
            **kwargs: Keyword arguments for tool execution

        Returns:
            Tool execution result

        Raises:
            RuntimeError: If tool is not available to this agent
        """
        if not self.has_tool(tool_name):
            raise RuntimeError(f"Agent {self.name} does not have access to tool '{tool_name}'")

        tool_instance = self.assigned_tools[tool_name]

        # Update agent status during tool execution
        old_status = self.status
        self.status = "using_tool"

        try:
            result = tool_instance.execute(*args, **kwargs)
            return result
        finally:
            self.status = old_status

    def assign_tool(self, tool_name: str, tool_instance: Any) -> None:
        """Assign a tool instance to this agent.

        Args:
            tool_name: Name of the tool
            tool_instance: Tool instance to assign
        """
        self.assigned_tools[tool_name] = tool_instance

    def remove_tool(self, tool_name: str) -> bool:
        """Remove a tool from this agent.

        Args:
            tool_name: Name of the tool to remove

        Returns:
            True if tool was removed, False if tool wasn't assigned
        """
        if tool_name in self.assigned_tools:
            del self.assigned_tools[tool_name]
            return True
        return False

    def get_pending_messages(self) -> list:
        """Get all pending messages in the agent's queue.

        Returns:
            List of pending messages
        """
        return self.message_queue.copy()

    def clear_messages(self) -> int:
        """Clear all pending messages.

        Returns:
            Number of messages cleared
        """
        count = len(self.message_queue)
        self.message_queue.clear()
        return count

    def __str__(self):
        return f"Agent({self.name}, {self.model}, {self.status})"

    def __repr__(self):
        return f'AgentVal(name="{self.name}", model="{self.model}", status="{self.status}")'


class InterpreterError(Exception):
    """Exception raised during interpretation."""
    pass


class AgenticScriptInterpreter:
    """Tree-walking interpreter for AgenticScript."""

    def __init__(self):
        self.globals: Dict[str, AgenticScriptValue] = {}
        self.agents: Dict[str, AgentVal] = {}

    def interpret(self, program: ast.Program) -> None:
        """Interpret an AgenticScript program."""
        for statement in program.statements:
            self.execute_statement(statement)

    def execute_statement(self, stmt: ast.StatementType) -> None:
        """Execute a single statement."""
        if isinstance(stmt, ast.AgentDeclaration):
            self.execute_agent_declaration(stmt)
        elif isinstance(stmt, ast.PropertyAssignment):
            self.execute_property_assignment(stmt)
        elif isinstance(stmt, ast.PrintStatement):
            self.execute_print_statement(stmt)
        elif isinstance(stmt, ast.ExpressionStatement):
            self.evaluate_expression(stmt.expression)
        else:
            raise InterpreterError(f"Unknown statement type: {type(stmt)}")

    def execute_agent_declaration(self, stmt: ast.AgentDeclaration) -> None:
        """Execute agent declaration: agent a = spawn Agent{ model }"""
        # Extract model path
        model_path = stmt.constructor.model.path

        # Extract configuration
        config = {}
        for config_pair in stmt.constructor.config:
            key = config_pair.key
            value = self.evaluate_expression(config_pair.value)
            config[key] = value

        # Create agent
        agent = AgentVal(name=stmt.name, model=model_path, **config)

        # Store in both globals and agents registry
        self.globals[stmt.name] = agent
        self.agents[stmt.name] = agent

        print(f"Agent '{stmt.name}' spawned successfully (id: agent_{len(self.agents):03d})")

    def execute_property_assignment(self, stmt: ast.PropertyAssignment) -> None:
        """Execute property assignment: *agent->property = value"""
        agent_name = stmt.agent_name

        if agent_name not in self.agents:
            raise InterpreterError(f"Agent '{agent_name}' not found")

        agent = self.agents[agent_name]
        value = self.evaluate_expression(stmt.value)

        # Convert AgenticScript value to Python value for storage
        if isinstance(value, StringVal):
            py_value = value.value
        elif isinstance(value, NumberVal):
            py_value = value.value
        elif isinstance(value, BooleanVal):
            py_value = value.value
        else:
            py_value = value

        agent.set_property(stmt.property_name, py_value)
        print(f"Property '{stmt.property_name}' set on agent '{agent_name}'")

    def execute_print_statement(self, stmt: ast.PrintStatement) -> None:
        """Execute print statement: print(expression)"""
        value = self.evaluate_expression(stmt.expression)
        print(str(value))

    def evaluate_expression(self, expr: ast.ExpressionType) -> AgenticScriptValue:
        """Evaluate an expression and return its value."""
        if isinstance(expr, ast.StringValue):
            return StringVal(expr.value)
        elif isinstance(expr, ast.NumberValue):
            return NumberVal(expr.value)
        elif isinstance(expr, ast.BooleanValue):
            return BooleanVal(expr.value)
        elif isinstance(expr, ast.Identifier):
            if expr.name in self.globals:
                return self.globals[expr.name]
            else:
                raise InterpreterError(f"Undefined variable: {expr.name}")
        elif isinstance(expr, ast.PropertyAccess):
            return self.evaluate_property_access(expr)
        elif isinstance(expr, ast.MethodCall):
            return self.evaluate_method_call(expr)
        else:
            raise InterpreterError(f"Unknown expression type: {type(expr)}")

    def evaluate_property_access(self, expr: ast.PropertyAccess) -> AgenticScriptValue:
        """Evaluate property access: object.property"""
        obj_name = expr.object
        prop_name = expr.property

        if obj_name not in self.globals:
            raise InterpreterError(f"Undefined variable: {obj_name}")

        obj = self.globals[obj_name]

        if isinstance(obj, AgentVal):
            prop_value = obj.get_property(prop_name)

            # Convert Python value to AgenticScript value
            if isinstance(prop_value, str):
                return StringVal(prop_value)
            elif isinstance(prop_value, (int, float)):
                return NumberVal(prop_value)
            elif isinstance(prop_value, bool):
                return BooleanVal(prop_value)
            else:
                # Return as-is for complex objects
                return prop_value
        else:
            raise InterpreterError(f"Object '{obj_name}' does not support property access")

    def evaluate_method_call(self, expr: ast.MethodCall) -> AgenticScriptValue:
        """Evaluate method call: object.method(args)"""
        obj_name = expr.object
        method_name = expr.method

        if obj_name not in self.globals:
            raise InterpreterError(f"Undefined variable: {obj_name}")

        obj = self.globals[obj_name]

        if isinstance(obj, AgentVal):
            # Evaluate arguments
            args = [self.evaluate_expression(arg) for arg in expr.arguments]

            if method_name == "ask":
                # Synchronous communication
                if len(args) < 1:
                    raise InterpreterError("ask() requires at least 1 argument: message")

                message = args[0].value
                timeout = args[1].value if len(args) > 1 else None

                response = obj.ask(message, timeout)
                return StringVal(response)

            elif method_name == "tell":
                # Asynchronous messaging
                if len(args) < 1:
                    raise InterpreterError("tell() requires 1 argument: message")

                message = args[0].value
                obj.tell(message)
                return StringVal("message sent")

            elif method_name == "has_tool":
                # Tool availability check
                if len(args) < 1:
                    raise InterpreterError("has_tool() requires 1 argument: tool_name")

                tool_name = args[0].value
                has_tool = obj.has_tool(tool_name)
                return BooleanVal(has_tool)

            elif method_name == "execute_tool":
                # Tool execution
                if len(args) < 1:
                    raise InterpreterError("execute_tool() requires at least 1 argument: tool_name")

                tool_name = args[0].value
                tool_args = [arg.value for arg in args[1:]]

                try:
                    result = obj.execute_tool(tool_name, *tool_args)
                    return StringVal(str(result))
                except RuntimeError as e:
                    raise InterpreterError(str(e))

            else:
                raise InterpreterError(f"Unknown method '{method_name}' on agent")
        else:
            raise InterpreterError(f"Object '{obj_name}' does not support method calls")

    def get_agent_status(self, agent_name: str) -> Optional[AgentVal]:
        """Get agent status for debugging."""
        return self.agents.get(agent_name)

    def list_agents(self) -> Dict[str, AgentVal]:
        """List all active agents."""
        return self.agents.copy()


# Convenience function
def interpret_agenticscript(program: ast.Program) -> AgenticScriptInterpreter:
    """Interpret an AgenticScript program and return the interpreter instance."""
    interpreter = AgenticScriptInterpreter()
    interpreter.interpret(program)
    return interpreter