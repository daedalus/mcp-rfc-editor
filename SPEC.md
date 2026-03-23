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

### Not Scope
- PDF generation
- XML validation
- Format conversion (v2 to v3)
- ABNF validation

## Public API / Interface

### MCP Tools

1. **load_rfc**
   - `filepath: string` (required) - Path to RFC TXT file
   - Returns: RFCDocument structure with all fields

2. **download_rfc**
   - `rfc_id: string|integer` (required) - RFC number (e.g., "791" or 791)
   - `filepath: string` (optional) - Path to save the file before parsing
   - Returns: RFCDocument structure with all fields

3. **create_rfc**
   - `rfc_number: string` (optional) - RFC number
   - `title: string` (optional) - Document title
   - Returns: Empty RFCDocument structure

3. **save_rfc**
   - `filepath: string` (required) - Output file path
   - `document: object` (required) - RFCDocument to save
   - Returns: Success message

4. **set_title**
   - `document: object` (required) - RFCDocument
   - `title: string` (required) - New title
   - Returns: Updated document

5. **set_abstract**
   - `document: object` (required) - RFCDocument
   - `abstract: string` (required) - Abstract text
   - Returns: Updated document

6. **add_section**
   - `document: object` (required) - RFCDocument
   - `number: string` (required) - Section number (e.g., "1", "2.1")
   - `title: string` (required) - Section title
   - `content: string` (required) - Section content
   - Returns: Updated document

7. **update_section**
   - `document: object` (required) - RFCDocument
   - `number: string` (required) - Section number
   - `title: string` (optional) - New title
   - `content: string` (optional) - New content
   - Returns: Updated document

8. **delete_section**
   - `document: object` (required) - RFCDocument
   - `number: string` (required) - Section number to delete
   - Returns: Updated document

9. **list_sections**
   - `document: object` (required) - RFCDocument
   - Returns: Array of section objects with number, title, content

10. **set_copyright**
    - `document: object` (required) - RFCDocument
    - `year: integer` (required) - Copyright year
    - `holders: string` (required) - Copyright holders
    - Returns: Updated document

11. **set_authors**
    - `document: object` (required) - RFCDocument
    - `authors: array` (required) - Array of {name, organization, email, address}
    - Returns: Updated document

12. **to_dict**
    - `document: object` (required) - RFCDocument
    - Returns: Dictionary representation of document

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

## Performance & Constraints
- Python 3.11+
- MCP SDK for server implementation
- rfc-editor library for document manipulation
