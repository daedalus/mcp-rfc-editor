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

- `load_rfc` - Load and parse an RFC TXT file (creates session)
- `download_rfc` - Download an RFC from rfc-editor by ID (creates session)
- `create_rfc` - Create a new empty RFC document (creates session)
- `get_document` - Get the current document from session context
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

## Session-Based Workflow

The server maintains session context so you don't need to pass the full document object on every call:

```python
# 1. Download an RFC - returns Session ID
result = download_rfc(rfc_id="791")
# Returns: {document..., "Session ID": "abc-123"}

# 2. Use session ID to get title (no document needed)
get_title(session_id="abc-123")

# 3. Modify and changes are persisted
set_title(session_id="abc-123", title="New Title")
```

Alternatively, you can always pass the full `document` object directly (legacy mode).

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
