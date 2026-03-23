"""MCP Server for editing RFC documents."""

from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from rfc_editor import RFCAuthor, RFCDocument, RFCEditor, RFCSection

app = Server("mcp-rfc-editor")


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
    doc = None
    if "document" in arguments and arguments["document"]:
        doc = _dict_to_document(arguments["document"])

    if name == "load_rfc":
        editor = RFCEditor()
        result = editor.load(Path(arguments["filepath"]))
        return [TextContent(type="text", text=str(_document_to_dict(result)))]

    elif name == "download_rfc":
        editor = RFCEditor()
        filepath = arguments.get("filepath")
        result = editor.download(
            arguments["rfc_id"], Path(filepath) if filepath else None
        )
        return [TextContent(type="text", text=str(_document_to_dict(result)))]

    elif name == "create_rfc":
        result = RFCDocument(
            rfc_number=arguments.get("rfc_number", ""),
            title=arguments.get("title", ""),
        )
        return [TextContent(type="text", text=str(_document_to_dict(result)))]

    elif name == "save_rfc":
        editor = RFCEditor()
        editor.document = _dict_to_document(arguments["document"])
        editor.save(Path(arguments["filepath"]))
        return [TextContent(type="text", text=f"Saved to {arguments['filepath']}")]

    elif name == "get_title":
        editor = RFCEditor()
        editor.document = doc
        return [TextContent(type="text", text=str(editor.get_title()))]

    elif name == "get_abstract":
        editor = RFCEditor()
        editor.document = doc
        return [TextContent(type="text", text=str(editor.get_abstract()))]

    elif name == "get_copyright":
        editor = RFCEditor()
        editor.document = doc
        return [TextContent(type="text", text=str(editor.get_copyright()))]

    elif name == "get_status_of_memo":
        editor = RFCEditor()
        editor.document = doc
        return [TextContent(type="text", text=str(editor.get_status_of_memo()))]

    elif name == "get_toc":
        editor = RFCEditor()
        editor.document = doc
        return [TextContent(type="text", text=str(editor.get_toc()))]

    elif name == "get_acknowledgements":
        editor = RFCEditor()
        editor.document = doc
        return [TextContent(type="text", text=str(editor.get_acknowledgements()))]

    elif name == "get_contributors":
        editor = RFCEditor()
        editor.document = doc
        return [TextContent(type="text", text=str(editor.get_contributors()))]

    elif name == "get_authors_address":
        editor = RFCEditor()
        editor.document = doc
        return [TextContent(type="text", text=str(editor.get_authors_address()))]

    elif name == "get_section_by_title":
        editor = RFCEditor()
        editor.document = doc
        section = editor.get_section_by_title(arguments["title"])
        return [
            TextContent(type="text", text=str(section.to_dict() if section else None))
        ]

    elif name == "set_title":
        editor = RFCEditor()
        editor.document = doc
        editor.set_title(arguments["title"])
        return [TextContent(type="text", text=str(_document_to_dict(editor.document)))]

    elif name == "set_abstract":
        editor = RFCEditor()
        editor.document = doc
        editor.set_abstract(arguments["abstract"])
        return [TextContent(type="text", text=str(_document_to_dict(editor.document)))]

    elif name == "add_section":
        editor = RFCEditor()
        editor.document = doc
        editor.add_section(
            arguments["number"], arguments["title"], arguments["content"]
        )
        return [TextContent(type="text", text=str(_document_to_dict(editor.document)))]

    elif name == "update_section":
        editor = RFCEditor()
        editor.document = doc
        editor.update_section(
            arguments["number"], arguments.get("title"), arguments.get("content")
        )
        return [TextContent(type="text", text=str(_document_to_dict(editor.document)))]

    elif name == "delete_section":
        editor = RFCEditor()
        editor.document = doc
        editor.delete_section(arguments["number"])
        return [TextContent(type="text", text=str(_document_to_dict(editor.document)))]

    elif name == "list_sections":
        return [TextContent(type="text", text=str([s.to_dict() for s in doc.sections]))]

    elif name == "set_copyright":
        editor = RFCEditor()
        editor.document = doc
        editor.set_copyright(arguments["year"], arguments["holders"])
        return [TextContent(type="text", text=str(_document_to_dict(editor.document)))]

    elif name == "set_authors":
        doc.authors = [RFCAuthor(**a) for a in arguments["authors"]]
        return [TextContent(type="text", text=str(_document_to_dict(doc)))]

    elif name == "set_acknowledgements":
        editor = RFCEditor()
        editor.document = doc
        editor.set_acknowledgements(arguments["content"])
        return [TextContent(type="text", text=str(_document_to_dict(editor.document)))]

    elif name == "set_contributors":
        editor = RFCEditor()
        editor.document = doc
        editor.set_contributors(arguments["content"])
        return [TextContent(type="text", text=str(_document_to_dict(editor.document)))]

    elif name == "set_authors_address":
        editor = RFCEditor()
        editor.document = doc
        editor.set_authors_address(arguments["address"])
        return [TextContent(type="text", text=str(_document_to_dict(editor.document)))]

    elif name == "set_status_of_memo":
        editor = RFCEditor()
        editor.document = doc
        editor.set_status_of_memo(arguments["status"])
        return [TextContent(type="text", text=str(_document_to_dict(editor.document)))]

    elif name == "set_toc":
        editor = RFCEditor()
        editor.document = doc
        editor.set_toc(arguments["toc"])
        return [TextContent(type="text", text=str(_document_to_dict(editor.document)))]

    elif name == "set_section_by_title":
        editor = RFCEditor()
        editor.document = doc
        editor.set_section_by_title(arguments["title"], arguments["content"])
        return [TextContent(type="text", text=str(_document_to_dict(editor.document)))]

    elif name == "to_dict":
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
