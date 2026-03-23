# SPEC.md — mcp-rfc-editor

## Purpose
An MCP (Model Context Protocol) server that provides tools for editing RFC TXT documents using the rfc-editor Python library. This server exposes RFC document manipulation capabilities to AI clients via the MCP protocol.

## Scope

### In Scope
- Load and parse RFC TXT files
- Download RFCs from the internet by ID
- Create new RFC documents from scratch
- Modify existing RFC documents (title, abstract, sections, authors, etc.)
- Save RFC documents back to TXT format
- List all sections in a document
- Get/delete specific sections by number or title
- Add new sections
- Session-based context for document persistence

### Not Scope
- PDF generation
- XML validation
- Format conversion (v2 to v3)
- ABNF validation

## Public API / Interface

### MCP Tools

1. **load_rfc**
   - `filepath: string` (required) - Path to RFC TXT file
   - Returns: RFCDocument structure with all fields + Session ID

2. **download_rfc**
   - `rfc_id: string|integer` (required) - RFC number (e.g., "791" or 791)
   - `filepath: string` (optional) - Path to save the file before parsing
   - Returns: RFCDocument structure with all fields + Session ID

3. **create_rfc**
   - `rfc_number: string` (optional) - RFC number
   - `title: string` (optional) - Document title
   - Returns: Empty RFCDocument structure + Session ID

4. **get_document**
   - `session_id: string` (optional) - Session ID from load/create/download
   - Returns: RFCDocument from session context

5. **save_rfc**
   - `filepath: string` (required) - Output file path
   - `document: object` (optional) - RFCDocument to save
   - `session_id: string` (optional) - Session ID to save from
   - Returns: Success message

### Session-Aware Tools
All document modification tools accept either:
- `document: object` - Full RFCDocument object (legacy mode)
- `session_id: string` - Session ID to retrieve document from session

Tools: set_title, set_abstract, add_section, update_section, delete_section, list_sections, set_copyright, set_authors, set_acknowledgements, set_contributors, set_authors_address, set_status_of_memo, set_toc, set_section_by_title, to_dict

## Data Formats

### RFCDocument structure
```python
{
    rfc_number: str,
    category: str,
    title: str,
    abstract: str,
    authors: List[RFCAuthor],
    status_of_memo: str,
    copyright_notice: str,
    toc: str,
    sections: List[RFCSection],
    acknowledgements: str,
    contributors: str,
    index: str,
    authors_address: str,
    raw_content: str
}
```

### RFCAuthor structure
```python
{
    name: str,
    organization: str,
    email: str,
    address: str
}
```

### RFCSection structure
```python
{
    number: str,
    title: str,
    content: str
}
```

## Edge Cases
1. Loading a non-existent file should raise an error
2. Deleting a non-existent section should raise an error
3. Updating a section that doesn't exist should raise an error
4. Empty document should be allowed
5. Section numbers should support dot notation (e.g., "1.2.3")
6. Unicode content should be handled properly
7. Large files (>1MB) should work without issues
8. Downloading an invalid RFC number should raise an error
9. Network failure during download should raise an error
10. Invalid RFC ID format should raise an error
11. Using an invalid session_id should return appropriate error
12. No document in session when using session_id should return error
13. Session should persist document changes across tool calls

## Performance & Constraints
- Python 3.11+
- MCP SDK for server implementation
- rfc-editor library for document manipulation
