"""MCP Server for editing RFC documents."""

import uuid
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from rfc_editor import RFCAuthor, RFCDocument, RFCEditor, RFCSection

app = Server("mcp-rfc-editor")

_sessions: dict[str, RFCDocument] = {}


def _document_to_dict(doc: RFCDocument) -> dict[str, Any]:
    return {
        "rfc_number": doc.rfc_number,
        "category": doc.category,
        "title": doc.title,
        "abstract": doc.abstract,
        "authors": [a.to_dict() for a in doc.authors],
        "status_of_memo": doc.status_of_memo,
        "copyright_notice": doc.copyright_notice,
        "toc": doc.toc,
        "sections": [s.to_dict() for s in doc.sections],
        "acknowledgements": doc.acknowledgements,
        "contributors": doc.contributors,
        "index": doc.index,
        "authors_address": doc.authors_address,
        "raw_content": doc.raw_content,
    }


def _dict_to_document(data: dict[str, Any]) -> RFCDocument:
    authors = [RFCAuthor(**a) for a in data.get("authors", [])]
    sections = [RFCSection(**s) for s in data.get("sections", [])]
    return RFCDocument(
        rfc_number=data.get("rfc_number", ""),
        category=data.get("category", ""),
        title=data.get("title", ""),
        abstract=data.get("abstract", ""),
        authors=authors,
        status_of_memo=data.get("status_of_memo", ""),
        copyright_notice=data.get("copyright_notice", ""),
        toc=data.get("toc", ""),
        sections=sections,
        acknowledgements=data.get("acknowledgements", ""),
        contributors=data.get("contributors", ""),
        index=data.get("index", ""),
        authors_address=data.get("authors_address", ""),
        raw_content=data.get("raw_content", ""),
    )


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="load_rfc",
            description="Load an RFC TXT file and parse its sections",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to RFC TXT file",
                    }
                },
                "required": ["filepath"],
            },
        ),
        Tool(
            name="download_rfc",
            description="Download an RFC by number from rfc-editor and parse it",
            inputSchema={
                "type": "object",
                "properties": {
                    "rfc_id": {
                        "type": "string",
                        "description": "RFC number (e.g., '791' or 791)",
                    },
                    "filepath": {
                        "type": "string",
                        "description": "Optional path to save the file before parsing",
                    },
                },
                "required": ["rfc_id"],
            },
        ),
        Tool(
            name="create_rfc",
            description="Create a new empty RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "rfc_number": {"type": "string", "description": "RFC number"},
                    "title": {"type": "string", "description": "Document title"},
                },
            },
        ),
        Tool(
            name="get_document",
            description="Get the current active RFC document from session context",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="save_rfc",
            description="Save an RFC document to a TXT file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Output file path"},
                    "document": {
                        "type": "object",
                        "description": "RFCDocument to save",
                    },
                },
                "required": ["filepath", "document"],
            },
        ),
        Tool(
            name="get_title",
            description="Get the title of an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"}
                },
                "required": ["document"],
            },
        ),
        Tool(
            name="get_abstract",
            description="Get the abstract of an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"}
                },
                "required": ["document"],
            },
        ),
        Tool(
            name="get_copyright",
            description="Get the copyright notice of an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"}
                },
                "required": ["document"],
            },
        ),
        Tool(
            name="get_status_of_memo",
            description="Get the status of this memo section",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"}
                },
                "required": ["document"],
            },
        ),
        Tool(
            name="get_toc",
            description="Get the table of contents",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"}
                },
                "required": ["document"],
            },
        ),
        Tool(
            name="get_acknowledgements",
            description="Get the acknowledgements of an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"}
                },
                "required": ["document"],
            },
        ),
        Tool(
            name="get_contributors",
            description="Get the contributors of an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"}
                },
                "required": ["document"],
            },
        ),
        Tool(
            name="get_authors_address",
            description="Get the authors address section of an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"}
                },
                "required": ["document"],
            },
        ),
        Tool(
            name="get_section_by_title",
            description="Get a section by its title",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"},
                    "title": {"type": "string", "description": "Section title"},
                },
                "required": ["document", "title"],
            },
        ),
        Tool(
            name="set_title",
            description="Set the title of an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"},
                    "title": {"type": "string", "description": "New title"},
                },
                "required": ["document", "title"],
            },
        ),
        Tool(
            name="set_abstract",
            description="Set the abstract of an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"},
                    "abstract": {"type": "string", "description": "Abstract text"},
                },
                "required": ["document", "abstract"],
            },
        ),
        Tool(
            name="add_section",
            description="Add a new section to an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"},
                    "number": {
                        "type": "string",
                        "description": "Section number (e.g., '1', '2.1')",
                    },
                    "title": {"type": "string", "description": "Section title"},
                    "content": {"type": "string", "description": "Section content"},
                },
                "required": ["document", "number", "title", "content"],
            },
        ),
        Tool(
            name="update_section",
            description="Update an existing section in an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"},
                    "number": {"type": "string", "description": "Section number"},
                    "title": {"type": "string", "description": "New title (optional)"},
                    "content": {
                        "type": "string",
                        "description": "New content (optional)",
                    },
                },
                "required": ["document", "number"],
            },
        ),
        Tool(
            name="delete_section",
            description="Delete a section from an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"},
                    "number": {
                        "type": "string",
                        "description": "Section number to delete",
                    },
                },
                "required": ["document", "number"],
            },
        ),
        Tool(
            name="list_sections",
            description="List all sections in an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"}
                },
                "required": ["document"],
            },
        ),
        Tool(
            name="set_copyright",
            description="Set the copyright notice of an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"},
                    "year": {"type": "integer", "description": "Copyright year"},
                    "holders": {"type": "string", "description": "Copyright holders"},
                },
                "required": ["document", "year", "holders"],
            },
        ),
        Tool(
            name="set_authors",
            description="Set the authors of an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"},
                    "authors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "organization": {"type": "string"},
                                "email": {"type": "string"},
                                "address": {"type": "string"},
                            },
                        },
                    },
                },
                "required": ["document", "authors"],
            },
        ),
        Tool(
            name="set_acknowledgements",
            description="Set the acknowledgements of an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"},
                    "content": {
                        "type": "string",
                        "description": "Acknowledgements content",
                    },
                },
                "required": ["document", "content"],
            },
        ),
        Tool(
            name="set_contributors",
            description="Set the contributors of an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"},
                    "content": {
                        "type": "string",
                        "description": "Contributors content",
                    },
                },
                "required": ["document", "content"],
            },
        ),
        Tool(
            name="set_authors_address",
            description="Set the authors address section of an RFC document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"},
                    "address": {"type": "string", "description": "Authors address"},
                },
                "required": ["document", "address"],
            },
        ),
        Tool(
            name="set_status_of_memo",
            description="Set the status of this memo section",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"},
                    "status": {"type": "string", "description": "Status text"},
                },
                "required": ["document", "status"],
            },
        ),
        Tool(
            name="set_toc",
            description="Set the table of contents",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"},
                    "toc": {"type": "string", "description": "Table of contents"},
                },
                "required": ["document", "toc"],
            },
        ),
        Tool(
            name="set_section_by_title",
            description="Update a section by its title",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"},
                    "title": {"type": "string", "description": "Section title"},
                    "content": {"type": "string", "description": "New content"},
                },
                "required": ["document", "title", "content"],
            },
        ),
        Tool(
            name="to_dict",
            description="Convert an RFC document to a dictionary",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {"type": "object", "description": "RFCDocument"}
                },
                "required": ["document"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    session_id = arguments.pop("session_id", None) if arguments else None

    doc = None
    if session_id and session_id in _sessions:
        doc = _sessions[session_id]
    elif "document" in arguments and arguments["document"]:
        doc = _dict_to_document(arguments["document"])

    if name == "load_rfc":
        editor = RFCEditor()
        result = editor.load(Path(arguments["filepath"]))
        session_id = str(uuid.uuid4())
        _sessions[session_id] = result
        return [
            TextContent(
                type="text",
                text=str(_document_to_dict(result)) + f"\n\nSession ID: {session_id}",
            )
        ]

    elif name == "download_rfc":
        editor = RFCEditor()
        filepath = arguments.get("filepath")
        result = editor.download(
            arguments["rfc_id"], Path(filepath) if filepath else None
        )
        session_id = str(uuid.uuid4())
        _sessions[session_id] = result
        return [
            TextContent(
                type="text",
                text=str(_document_to_dict(result)) + f"\n\nSession ID: {session_id}",
            )
        ]

    elif name == "create_rfc":
        result = RFCDocument(
            rfc_number=arguments.get("rfc_number", ""),
            title=arguments.get("title", ""),
        )
        session_id = str(uuid.uuid4())
        _sessions[session_id] = result
        return [
            TextContent(
                type="text",
                text=str(_document_to_dict(result)) + f"\n\nSession ID: {session_id}",
            )
        ]

    elif name == "get_document":
        if session_id and session_id in _sessions:
            return [
                TextContent(
                    type="text", text=str(_document_to_dict(_sessions[session_id]))
                )
            ]
        return [
            TextContent(
                type="text", text="No active session. Load or create a document first."
            )
        ]

    elif name == "save_rfc":
        editor = RFCEditor()
        editor.document = _dict_to_document(arguments["document"])
        editor.save(Path(arguments["filepath"]))
        if session_id and session_id in _sessions:
            _sessions[session_id] = editor.document
        return [
            TextContent(
                type="text",
                text=f"Saved to {arguments['filepath']}"
                + (f" (Session: {session_id})" if session_id else ""),
            )
        ]

    elif name == "get_title":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        return [TextContent(type="text", text=str(editor.get_title()))]

    elif name == "get_abstract":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        return [TextContent(type="text", text=str(editor.get_abstract()))]

    elif name == "get_copyright":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        return [TextContent(type="text", text=str(editor.get_copyright()))]

    elif name == "get_status_of_memo":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        return [TextContent(type="text", text=str(editor.get_status_of_memo()))]

    elif name == "get_toc":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        return [TextContent(type="text", text=str(editor.get_toc()))]

    elif name == "get_acknowledgements":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        return [TextContent(type="text", text=str(editor.get_acknowledgements()))]

    elif name == "get_contributors":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        return [TextContent(type="text", text=str(editor.get_contributors()))]

    elif name == "get_authors_address":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        return [TextContent(type="text", text=str(editor.get_authors_address()))]

    elif name == "get_section_by_title":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        section = editor.get_section_by_title(arguments["title"])
        return [
            TextContent(type="text", text=str(section.to_dict() if section else None))
        ]

    elif name == "set_title":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        editor.set_title(arguments["title"])
        if session_id and session_id in _sessions:
            _sessions[session_id] = editor.document
        return [
            TextContent(
                type="text",
                text=str(_document_to_dict(editor.document))
                + (f"\n\nSession ID: {session_id}" if session_id else ""),
            )
        ]

    elif name == "set_abstract":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        editor.set_abstract(arguments["abstract"])
        if session_id and session_id in _sessions:
            _sessions[session_id] = editor.document
        return [
            TextContent(
                type="text",
                text=str(_document_to_dict(editor.document))
                + (f"\n\nSession ID: {session_id}" if session_id else ""),
            )
        ]

    elif name == "add_section":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        editor.add_section(
            arguments["number"], arguments["title"], arguments["content"]
        )
        if session_id and session_id in _sessions:
            _sessions[session_id] = editor.document
        return [
            TextContent(
                type="text",
                text=str(_document_to_dict(editor.document))
                + (f"\n\nSession ID: {session_id}" if session_id else ""),
            )
        ]

    elif name == "update_section":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        editor.update_section(
            arguments["number"], arguments.get("title"), arguments.get("content")
        )
        if session_id and session_id in _sessions:
            _sessions[session_id] = editor.document
        return [
            TextContent(
                type="text",
                text=str(_document_to_dict(editor.document))
                + (f"\n\nSession ID: {session_id}" if session_id else ""),
            )
        ]

    elif name == "delete_section":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        editor.delete_section(arguments["number"])
        if session_id and session_id in _sessions:
            _sessions[session_id] = editor.document
        return [
            TextContent(
                type="text",
                text=str(_document_to_dict(editor.document))
                + (f"\n\nSession ID: {session_id}" if session_id else ""),
            )
        ]

    elif name == "list_sections":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        return [TextContent(type="text", text=str([s.to_dict() for s in doc.sections]))]

    elif name == "set_copyright":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        editor.set_copyright(arguments["year"], arguments["holders"])
        if session_id and session_id in _sessions:
            _sessions[session_id] = editor.document
        return [
            TextContent(
                type="text",
                text=str(_document_to_dict(editor.document))
                + (f"\n\nSession ID: {session_id}" if session_id else ""),
            )
        ]

    elif name == "set_authors":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        doc.authors = [RFCAuthor(**a) for a in arguments["authors"]]
        if session_id and session_id in _sessions:
            _sessions[session_id] = doc
        return [
            TextContent(
                type="text",
                text=str(_document_to_dict(doc))
                + (f"\n\nSession ID: {session_id}" if session_id else ""),
            )
        ]

    elif name == "set_acknowledgements":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        editor.set_acknowledgements(arguments["content"])
        if session_id and session_id in _sessions:
            _sessions[session_id] = editor.document
        return [
            TextContent(
                type="text",
                text=str(_document_to_dict(editor.document))
                + (f"\n\nSession ID: {session_id}" if session_id else ""),
            )
        ]

    elif name == "set_contributors":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        editor.set_contributors(arguments["content"])
        if session_id and session_id in _sessions:
            _sessions[session_id] = editor.document
        return [
            TextContent(
                type="text",
                text=str(_document_to_dict(editor.document))
                + (f"\n\nSession ID: {session_id}" if session_id else ""),
            )
        ]

    elif name == "set_authors_address":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        editor.set_authors_address(arguments["address"])
        if session_id and session_id in _sessions:
            _sessions[session_id] = editor.document
        return [
            TextContent(
                type="text",
                text=str(_document_to_dict(editor.document))
                + (f"\n\nSession ID: {session_id}" if session_id else ""),
            )
        ]

    elif name == "set_status_of_memo":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        editor.set_status_of_memo(arguments["status"])
        if session_id and session_id in _sessions:
            _sessions[session_id] = editor.document
        return [
            TextContent(
                type="text",
                text=str(_document_to_dict(editor.document))
                + (f"\n\nSession ID: {session_id}" if session_id else ""),
            )
        ]

    elif name == "set_toc":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        editor.set_toc(arguments["toc"])
        if session_id and session_id in _sessions:
            _sessions[session_id] = editor.document
        return [
            TextContent(
                type="text",
                text=str(_document_to_dict(editor.document))
                + (f"\n\nSession ID: {session_id}" if session_id else ""),
            )
        ]

    elif name == "set_section_by_title":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        editor = RFCEditor()
        editor.document = doc
        editor.set_section_by_title(arguments["title"], arguments["content"])
        if session_id and session_id in _sessions:
            _sessions[session_id] = editor.document
        return [
            TextContent(
                type="text",
                text=str(_document_to_dict(editor.document))
                + (f"\n\nSession ID: {session_id}" if session_id else ""),
            )
        ]

    elif name == "to_dict":
        if not doc:
            return [
                TextContent(
                    type="text",
                    text="No document in session. Provide session_id or document.",
                )
            ]
        return [TextContent(type="text", text=str(_document_to_dict(doc)))]

    return [TextContent(type="text", text="Unknown tool")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def run():
    import asyncio

    asyncio.run(main())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
