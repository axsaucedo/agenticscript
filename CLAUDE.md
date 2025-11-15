# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgenticScript is an agentic-first programming language with distributed runtime capabilities. This is currently in MVP development phase, with Phase 1 (Core Language Infrastructure) and Phase 1.5 (Debug REPL Foundation) completed.

## Important Development Instructions

### Documentation and Planning Requirements
- **Always append to NOTES.md**: Make extensive notes as you go in `docs/ai/NOTES.md` file which you should only ever append new notes to
- **Keep it simple**: Don't over engineer, for the MVP we want to have a non-overengineered but robust foundation to build upon
- **Phase-based commits**: For every phase completed, propose a commit on the repo with brief conventional commit format
- **Phase planning**: Before starting a new phase, put together a plan for each respective phase and document it in `docs/ai/PLAN-PHASE-<number>.md`
- **Update CLAUDE.md**: After every phase completed, review all the relevant `docs/ai/` files and update the CLAUDE.md accordingly to reflect the current state

### Testing Requirements
For every phase, ensure there is a clear testing plan to be added to ensure that the language examples work correctly as expected. If the language features are inconsistent, review them and request input from the user to make decisions as required.

## Development Environment

This project uses **UV** for all package management and development tasks:

- **Environment Setup**: `uv sync --dev` (installs all dependencies including dev tools)
- **Run REPL**: `uv run agenticscript` (launches interactive AgenticScript REPL)
- **Run Tests**: `uv run python tests/test_parser.py` (single test file) or similar
- **Linting**: `uv run ruff check` (code quality checks)
- **Formatting**: `uv run ruff format` (code formatting)

Python 3.12+ is required. All dependencies are managed through pyproject.toml.

## Architecture Overview

### Core Language Implementation (Phase 1 Complete)

The language is implemented as a **tree-walking interpreter** with these key components:

1. **Parser Pipeline**: Lark-based EBNF grammar → AST nodes → Interpreter execution
   - `src/agenticscript/core/grammar.lark`: Defines AgenticScript syntax
   - `src/agenticscript/core/parser.py`: Lark transformer converting parse trees to AST
   - `src/agenticscript/core/ast_nodes.py`: Python dataclass-based AST node definitions

2. **Runtime System**:
   - `src/agenticscript/core/interpreter.py`: Tree-walking interpreter with agent execution
   - Runtime values: `StringVal`, `NumberVal`, `BooleanVal`, `AgentVal`
   - Agents represented as Python objects with properties, status, and mock functionality

### Debug System (Phase 1.5 Complete)

Rich-powered REPL with comprehensive debugging capabilities:

- `src/agenticscript/debugger/repl.py`: Interactive REPL with Rich formatting
- Debug commands: `debug agents`, `debug dump <agent>`, `debug system`, `debug trace on/off`
- Prompt: `🤖>` with colored output, tables, and tree visualizations

### Current Language Support

AgenticScript currently supports:
- Agent spawning: `agent a = spawn Agent{ openai/gpt-4o }`
- Property assignment: `*a->goal = "value"`
- Property access: `a.status`, `a.model`
- Print statements: `print(a.status)`
- Basic expressions and values (strings, numbers, booleans)

## Development Workflow

### Implementation Philosophy

**UV-First Development**
- Use `uv add`, `uv remove` for dependency management
- `uv run` for script execution
- `uv sync` for environment consistency
- `uv build` for distribution

**Simplicity First**
- Choose boring, well-tested technologies
- Prefer Python standard library where possible
- Minimize external dependencies but choose where adding libraries can reduce complexity
- Prioritize readability over performance but avoid unnecessary verbosity; keep things simple

**Terminal-Native Debugging**
- Rich REPL with comprehensive debug commands
- No web UI complexity
- Deep introspection capabilities
- Easy to use during development

### Key Development Patterns

1. **Parser Development**:
   - Modify `grammar.lark` for syntax changes
   - Update `AgenticScriptTransformer` in `parser.py` to handle new AST nodes
   - Add corresponding AST node classes in `ast_nodes.py`

2. **Interpreter Extension**:
   - Add execution logic in `interpreter.py`
   - Create appropriate runtime value classes
   - Update agent behavior in `AgentVal` class

3. **REPL Enhancement**:
   - Add debug commands in `repl.py`
   - Use Rich library for beautiful terminal output
   - Follow existing command patterns (`debug_*` methods)

### Testing Strategy

- Parser tests: `tests/test_parser.py` (verify AST generation)
- Interpreter tests: `tests/test_interpreter.py` (verify execution behavior)
- REPL tests: `tests/test_repl.py` (verify debug commands work)

Run individual tests with: `uv run python tests/test_[component].py`

## Current Development Status

**Completed Phases:**
- ✅ Phase 1: Core Language Infrastructure (3 weeks) - DONE
- ✅ Phase 1.5: Debug REPL Foundation (1 week) - DONE

**Next Phase:**
- 🔄 Phase 2: Agent System & Communication (3 weeks) - NEXT

## Next Development Phase

**Phase 2**: Agent System & Communication (3 weeks) - focuses on:
- Module system and imports
- Tool assignment and execution
- Inter-agent communication patterns
- Threading-based agent implementation

See `docs/ai/PLAN-INITIAL.md` and `docs/ai/NOTES.md` for detailed phase planning and current status.

## Architecture Philosophy

- **UV-First**: All operations use UV for consistency and speed
- **Terminal-Native**: Rich REPL instead of web interfaces
- **Tree-Walking**: Direct AST execution for easier debugging
- **Threading**: Simple concurrency model for agent simulation
- **Mock-First**: Mock implementations before distributed system integration