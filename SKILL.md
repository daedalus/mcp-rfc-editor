# MCP RFC Editor

MCP server for editing RFC TXT documents.

## When to use this skill

Use this skill when you need to:
- Load and parse RFC documents
- Download RFCs by ID
- Create new RFC documents
- Edit sections, title, abstract

## Tools

- `load_rfc` - Load RFC TXT file
- `download_rfc` - Download RFC from rfc-editor
- `create_rfc` - Create new empty RFC
- `get_document` - Get current document
- `save_rfc` - Save to TXT format
- `set_title`, `set_abstract` - Set metadata
- `add_section`, `update_section`, `delete_section`, `list_sections` - Section ops
- `set_copyright`, `set_authors` - Set authors/copyright
- `to_dict` - Convert to dictionary

## Install

```bash
pip install mcp-rfc-editor
```