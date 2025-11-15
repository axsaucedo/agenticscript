"""Tree-walking interpreter for AgenticScript."""

from typing import Any, Dict, Optional
from . import ast_nodes as ast
from .module_system import module_system


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
        import threading
        from ..runtime.tool_registry import tool_registry
        from ..runtime.message_bus import message_bus

        self.name = name
        self.model = model
        self.status = "idle"  # idle, active, processing, using_tool, error
        self.properties = {}
        self.tools = []
        self.assigned_tools = {}  # tool_name -> tool_instance mapping
        self.message_queue = []  # simple queue for async messages (backup)

        # Threading support
        self._lock = threading.RLock()
        self._processing_thread = None
        self._stop_processing = threading.Event()

        # Runtime integration
        self._tool_registry = tool_registry
        self._message_bus = message_bus
        self._agent_id = f"{name}_{id(self):x}"  # Unique agent ID

        # Register with message bus
        self._message_bus.register_agent(self._agent_id)

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
        import time
        import threading

        with self._lock:
            # Update status during processing
            old_status = self.status
            self.status = "processing"

        try:
            # Simulate processing in a separate thread for realism
            def process_message():
                time.sleep(0.01)  # Simulate processing time

            # Process message based on content (mock AI response)
            if "error" in message.lower():
                response = f"Error handling: {message}"
            elif "status" in message.lower():
                response = f"Agent {self.name} status: {old_status}"
            elif "hello" in message.lower():
                response = f"Hello from {self.name}!"
            elif "busy" in message.lower():
                # Simulate longer processing
                time.sleep(0.05)
                response = f"Agent {self.name} was busy but processed: {message}"
            else:
                response = f"Agent {self.name} processed: {message}"

            # Log the interaction through message bus (for debugging/history)
            self._message_bus.send_message(
                sender="system",
                recipient=self._agent_id,
                content=f"ASK: {message}",
                message_type="ask_request"
            )

            self._message_bus.send_message(
                sender=self._agent_id,
                recipient="system",
                content=f"RESPONSE: {response}",
                message_type="ask_response"
            )

            return response

        finally:
            with self._lock:
                self.status = old_status

    def tell(self, message: str) -> None:
        """Send an asynchronous message to this agent.

        Args:
            message: Message to send
        """
        # Send through message bus for proper async handling
        message_id = self._message_bus.send_message(
            sender="system",
            recipient=self._agent_id,
            content=message,
            message_type="tell"
        )

        # Also keep in local queue as backup
        import datetime
        self.message_queue.append({
            "message": message,
            "timestamp": datetime.datetime.now(),
            "sender": "system",
            "message_id": message_id
        })

    def has_tool(self, tool_name: str) -> bool:
        """Check if this agent has access to a specific tool.

        Args:
            tool_name: Name of the tool to check

        Returns:
            True if agent has the tool, False otherwise
        """
        with self._lock:
            # Check both local assignment and global registry
            return (tool_name in self.assigned_tools or
                    self._tool_registry.is_tool_available(tool_name))

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

        with self._lock:
            # Update agent status during tool execution
            old_status = self.status
            self.status = "using_tool"

        try:
            # Try local tool first, then registry
            if tool_name in self.assigned_tools:
                tool_instance = self.assigned_tools[tool_name]
                result = tool_instance.execute(*args, **kwargs)
            else:
                # Use tool registry for execution
                result = self._tool_registry.execute_tool(tool_name, *args, **kwargs)

            # Log tool usage through message bus
            self._message_bus.send_message(
                sender=self._agent_id,
                recipient="system",
                content=f"TOOL_EXECUTION: {tool_name} -> {result}",
                message_type="tool_usage"
            )

            return result

        finally:
            with self._lock:
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
        with self._lock:
            count = len(self.message_queue)
            self.message_queue.clear()
            return count

    def start_background_processing(self) -> bool:
        """Start background message processing thread.

        Returns:
            True if started successfully, False if already running
        """
        import threading

        with self._lock:
            if self._processing_thread and self._processing_thread.is_alive():
                return False

            self._stop_processing.clear()
            self._processing_thread = threading.Thread(
                target=self._background_processor,
                name=f"Agent-{self.name}-Processor",
                daemon=True
            )
            self._processing_thread.start()
            return True

    def stop_background_processing(self) -> bool:
        """Stop background message processing thread.

        Returns:
            True if stopped successfully, False if not running
        """
        with self._lock:
            if not self._processing_thread or not self._processing_thread.is_alive():
                return False

            self._stop_processing.set()
            self._processing_thread.join(timeout=1.0)
            return True

    def _background_processor(self):
        """Background thread for processing messages."""
        import time

        while not self._stop_processing.is_set():
            try:
                # Check for messages from message bus
                message = self._message_bus.receive_message(self._agent_id, timeout=0.1)
                if message:
                    self._process_background_message(message)

                # Small delay to prevent busy waiting
                time.sleep(0.01)

            except Exception:
                # Continue processing even if there are errors
                pass

    def _process_background_message(self, message):
        """Process a message received in background.

        Args:
            message: Message object from message bus
        """
        with self._lock:
            # Update status temporarily
            old_status = self.status
            self.status = "processing"

        try:
            # Simple message processing logic
            if message.message_type == "tell":
                # Add to local queue for tracking
                import datetime
                self.message_queue.append({
                    "message": message.content,
                    "timestamp": datetime.datetime.now(),
                    "sender": message.sender,
                    "message_id": message.id
                })

            elif message.message_type == "ping":
                # Respond to ping messages
                self._message_bus.send_message(
                    sender=self._agent_id,
                    recipient=message.sender,
                    content=f"pong from {self.name}",
                    message_type="pong",
                    response_to=message.id
                )

        finally:
            with self._lock:
                self.status = old_status

    def get_agent_id(self) -> str:
        """Get the unique agent ID used by the message bus.

        Returns:
            Agent ID string
        """
        return self._agent_id

    def get_message_bus_stats(self) -> dict:
        """Get message bus statistics for this agent.

        Returns:
            Dictionary with agent's message statistics
        """
        stats = self._message_bus.get_statistics()
        agent_history = self._message_bus.get_agent_message_history(self._agent_id)

        return {
            "agent_id": self._agent_id,
            "total_messages": len(agent_history),
            "pending_messages": self._message_bus.get_pending_count(self._agent_id),
            "global_stats": {
                "total_sent": stats.total_sent,
                "total_delivered": stats.total_delivered,
                "average_delivery_time": stats.average_delivery_time
            }
        }

    def register_with_tool_registry(self, tool_name: str) -> bool:
        """Register this agent to use a specific tool from the global registry.

        Args:
            tool_name: Name of the tool to register for

        Returns:
            True if registration successful
        """
        with self._lock:
            if self._tool_registry.is_tool_available(tool_name):
                # Mark as having access to this tool
                if tool_name not in self.assigned_tools:
                    # Get instance from registry for local caching
                    tool_instance = self._tool_registry.get_tool_instance(tool_name)
                    if tool_instance:
                        self.assigned_tools[tool_name] = tool_instance
                return True
            return False

    def cleanup(self):
        """Cleanup agent resources (threading, message bus registration)."""
        # Stop background processing
        self.stop_background_processing()

        # Unregister from message bus
        with self._lock:
            self._message_bus.unregister_agent(self._agent_id)

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except Exception:
            # Ignore cleanup errors during destruction
            pass

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
        self.variables: Dict[str, AgenticScriptValue] = {}
        self.agents: Dict[str, AgentVal] = {}

    def interpret(self, program: ast.Program) -> None:
        """Interpret an AgenticScript program."""
        for statement in program.statements:
            self.execute_statement(statement)

    def execute_statement(self, stmt: ast.StatementType) -> None:
        """Execute a single statement."""
        if isinstance(stmt, ast.ImportStatement):
            self.execute_import_statement(stmt)
        elif isinstance(stmt, ast.AgentDeclaration):
            self.execute_agent_declaration(stmt)
        elif isinstance(stmt, ast.PropertyAssignment):
            self.execute_property_assignment(stmt)
        elif isinstance(stmt, ast.ToolAssignment):
            self.execute_tool_assignment(stmt)
        elif isinstance(stmt, ast.AssignmentStatement):
            self.execute_assignment_statement(stmt)
        elif isinstance(stmt, ast.IfStatement):
            self.execute_if_statement(stmt)
        elif isinstance(stmt, ast.PrintStatement):
            self.execute_print_statement(stmt)
        elif isinstance(stmt, ast.ExpressionStatement):
            self.evaluate_expression(stmt.expression)
        else:
            raise InterpreterError(f"Unknown statement type: {type(stmt)}")

    def execute_import_statement(self, stmt: ast.ImportStatement) -> None:
        """Execute import statement: import module { items }"""
        # Extract the actual lists from the AST nodes
        module_path = stmt.module_path.path
        import_list = stmt.import_list.imports

        # Do the import through the module system
        imports = module_system.import_module(module_path, import_list)
        # Add imported items to globals so they can be referenced
        for item_name, item_value in imports.items():
            self.globals[item_name] = item_value

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

    def execute_tool_assignment(self, stmt: ast.ToolAssignment) -> None:
        """Execute tool assignment: *agent->tools = { tools }"""
        agent_name = stmt.agent_name

        if agent_name not in self.agents:
            raise InterpreterError(f"Agent '{agent_name}' not found")

        agent = self.agents[agent_name]

        # Process the tool list
        for tool_spec in stmt.tool_list.tools:
            if isinstance(tool_spec, ast.ToolSpec):
                # Simple tool name - register with tool registry
                tool_name = tool_spec.name
                agent.register_with_tool_registry(tool_name)
            elif isinstance(tool_spec, ast.AgentRouting):
                # AgentRouting tool with specific agents
                from ..stdlib.tools import AgentRoutingTool
                routing_tool = AgentRoutingTool(tool_spec.agent_list)
                agent.assign_tool(tool_spec.tool_name, routing_tool)

        print(f"Tools assigned to agent '{agent_name}'")

    def execute_assignment_statement(self, stmt: ast.AssignmentStatement) -> None:
        """Execute variable assignment: variable = expression"""
        value = self.evaluate_expression(stmt.value)
        self.variables[stmt.variable_name] = value

    def execute_if_statement(self, stmt: ast.IfStatement) -> None:
        """Execute if statement: if condition { statements }"""
        condition_value = self.evaluate_expression(stmt.condition)

        # Convert to Python boolean
        if isinstance(condition_value, BooleanVal):
            should_execute = condition_value.value
        else:
            # Truthy evaluation for other types
            should_execute = bool(condition_value)

        if should_execute:
            # Execute then statements
            for statement in stmt.then_statements:
                self.execute_statement(statement)
        elif stmt.else_statements:
            # Execute else statements if condition is false
            for statement in stmt.else_statements:
                self.execute_statement(statement)

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
            if expr.name in self.variables:
                return self.variables[expr.name]
            elif expr.name in self.globals:
                return self.globals[expr.name]
            else:
                raise InterpreterError(f"Undefined variable: {expr.name}")
        elif isinstance(expr, ast.PropertyAccess):
            return self.evaluate_property_access(expr)
        elif isinstance(expr, ast.MethodCall):
            return self.evaluate_method_call(expr)
        elif isinstance(expr, ast.BooleanExpression):
            return self.evaluate_boolean_expression(expr)
        else:
            raise InterpreterError(f"Unknown expression type: {type(expr)}")

    def evaluate_boolean_expression(self, expr: ast.BooleanExpression) -> BooleanVal:
        """Evaluate boolean expressions like ==, !=, <, >, etc"""
        left_val = self.evaluate_expression(expr.left)

        # If no operator, this is a unary truthiness check
        if expr.operator is None or expr.right is None:
            left_py = self._to_python_value(left_val)
            return BooleanVal(bool(left_py))

        # Binary comparison
        right_val = self.evaluate_expression(expr.right)

        # Convert values to Python types for comparison
        left_py = self._to_python_value(left_val)
        right_py = self._to_python_value(right_val)

        if expr.operator == "==":
            result = left_py == right_py
        elif expr.operator == "!=":
            result = left_py != right_py
        elif expr.operator == "<":
            result = left_py < right_py
        elif expr.operator == ">":
            result = left_py > right_py
        elif expr.operator == "<=":
            result = left_py <= right_py
        elif expr.operator == ">=":
            result = left_py >= right_py
        else:
            raise InterpreterError(f"Unknown boolean operator: {expr.operator}")

        return BooleanVal(result)

    def _to_python_value(self, val: AgenticScriptValue) -> Any:
        """Convert AgenticScript value to Python value for operations"""
        if isinstance(val, StringVal):
            return val.value
        elif isinstance(val, NumberVal):
            return val.value
        elif isinstance(val, BooleanVal):
            return val.value
        else:
            return val

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