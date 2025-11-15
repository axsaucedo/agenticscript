# AgenticScript Development Notes

## Project Setup - 2024-01-15

### Initial UV Project Structure
- Created UV project with Python >=3.12 requirement
- Dependencies added:
  - lark[regex]>=1.1.7 for parsing
  - rich>=13.0.0 for terminal formatting
  - dataclasses-json>=0.6 for JSON serialization
- Dev dependencies: pytest, pytest-cov, ruff
- Ruff configured for Python 3.12 with line length 88

### Directory Structure Created
```
agenticscript/
├── src/agenticscript/
│   ├── core/           # Parser, lexer, AST, interpreter
│   ├── runtime/        # Agent management, message bus, backend
│   ├── stdlib/         # Standard library (agents, tools, patterns)
│   └── debugger/       # REPL and debug commands
├── tests/              # Test suite
├── examples/           # Example AgenticScript programs
└── docs/ai/           # AI-generated documentation and notes
```

### Key Design Decisions
1. **Python 3.12+**: Modern Python features, updated to match system requirements
2. **Lark Parser**: EBNF grammar, excellent error reporting, pure Python
3. **Tree-walking Interpreter**: Direct AST execution, easier debugging
4. **Threading for Agents**: Simpler concurrency model for MVP
5. **Rich REPL**: Terminal-native debugging without web UI complexity
6. **UV Package Management**: Fast dependency resolution and project management

### File Organization Update
- All Claude-generated files stored in docs/ai/
- Initial plan stored in docs/ai/PLAN-INITIAL.md
- Development notes in docs/ai/NOTES.md (this file)

### Next Steps
- Design Lark grammar for basic AgenticScript syntax
- Create AST node definitions using Python dataclasses
- Implement basic tree-walking interpreter
- Create Agent class with threading support