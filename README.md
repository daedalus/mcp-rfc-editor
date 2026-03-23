# mcp-rfc-editor

An MCP (Model Context Protocol) server for editing RFC TXT documents using the `rfc-editor` Python library.

## Installation

```bash
pip install mcp-rfc-editor
```

## Usage

### CLI

```bash
python -m mcp_rfc_editor
```

### Programmatic

```python
from mcp_rfc_editor import main
main()
```

## MCP Tools

The server exposes the following tools:

- `load_rfc` - Load and parse an RFC TXT file
- `create_rfc` - Create a new empty RFC document
- `save_rfc` - Save an RFC document to TXT format
- `set_title` - Set the document title
- `set_abstract` - Set the document abstract
- `add_section` - Add a new section
- `update_section` - Update an existing section
- `delete_section` - Delete a section
- `list_sections` - List all sections in the document
- `set_copyright` - Set copyright notice
- `set_authors` - Set document authors
- `to_dict` - Convert document to dictionary

## Development

### Requirements

- Python 3.11+
- mcp
- rfc-editor

### Setup

```bash
pip install -e ".[dev]"
```

### Testing

```bash
pytest tests/
```

### Linting

```bash
black src/ tests/
ruff check src/ tests/
```
