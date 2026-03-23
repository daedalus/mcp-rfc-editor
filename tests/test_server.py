from unittest.mock import patch

import pytest
from rfc_editor import RFCAuthor, RFCDocument, RFCSection

from mcp_rfc_editor.server import (
    _dict_to_document,
    _document_to_dict,
)


class TestDocumentConversion:
    def test_document_to_dict_basic(self):
        doc = RFCDocument(rfc_number="1234", title="Test Title")
        result = _document_to_dict(doc)
        assert result["rfc_number"] == "1234"
        assert result["title"] == "Test Title"

    def test_document_to_dict_with_authors(self):
        doc = RFCDocument(
            authors=[RFCAuthor(name="John Doe", email="john@example.com")]
        )
        result = _document_to_dict(doc)
        assert len(result["authors"]) == 1
        assert result["authors"][0]["name"] == "John Doe"

    def test_document_to_dict_with_sections(self):
        doc = RFCDocument(
            sections=[RFCSection(number="1", title="Intro", content="Hello")]
        )
        result = _document_to_dict(doc)
        assert len(result["sections"]) == 1
        assert result["sections"][0]["number"] == "1"

    def test_dict_to_document_basic(self):
        data = {"rfc_number": "5678", "title": "New Title", "authors": []}
        result = _dict_to_document(data)
        assert result.rfc_number == "5678"
        assert result.title == "New Title"

    def test_dict_to_document_with_authors(self):
        data = {
            "rfc_number": "1",
            "title": "Test",
            "authors": [{"name": "Jane Doe", "email": "jane@example.com"}],
        }
        result = _dict_to_document(data)
        assert len(result.authors) == 1
        assert result.authors[0].name == "Jane Doe"

    def test_roundtrip_document(self):
        original = RFCDocument(
            rfc_number="9999",
            title="Roundtrip Test",
            abstract="Testing roundtrip",
            authors=[RFCAuthor(name="Test Author", organization="Test Org")],
            sections=[RFCSection(number="1", title="Section One", content="Content")],
        )
        as_dict = _document_to_dict(original)
        restored = _dict_to_document(as_dict)
        assert restored.rfc_number == original.rfc_number
        assert restored.title == original.title
        assert len(restored.authors) == len(original.authors)
        assert len(restored.sections) == len(original.sections)


class TestDownloadRfc:
    def test_download_rfc_by_id(self):

        from mcp_rfc_editor import server
        from mcp_rfc_editor.server import call_tool

        mock_doc = RFCDocument(rfc_number="791", title="Internet Protocol")
        with patch.object(server, "RFCEditor") as MockEditor:
            mock_instance = MockEditor.return_value
            mock_instance.download.return_value = mock_doc
            import asyncio

            result = asyncio.run(call_tool("download_rfc", {"rfc_id": "791"}))
            assert len(result) == 1
            assert "rfc_number" in result[0].text
            assert "791" in result[0].text

    def test_download_rfc_with_filepath(self):
        from mcp_rfc_editor import server

        mock_doc = RFCDocument(rfc_number="791", title="Internet Protocol")
        with patch.object(server, "RFCEditor") as MockEditor:
            mock_instance = MockEditor.return_value
            mock_instance.download.return_value = mock_doc
            import asyncio

            from mcp_rfc_editor.server import call_tool

            result = asyncio.run(
                call_tool(
                    "download_rfc", {"rfc_id": "791", "filepath": "/tmp/rfc791.txt"}
                )
            )
            assert len(result) == 1
            assert "rfc_number" in result[0].text

    def test_download_rfc_invalid_id(self):
        from mcp_rfc_editor import server

        with patch.object(server, "RFCEditor") as MockEditor:
            mock_instance = MockEditor.return_value
            mock_instance.download.side_effect = ValueError("Invalid RFC number")
            import asyncio

            from mcp_rfc_editor.server import call_tool

            with pytest.raises(ValueError, match="Invalid RFC number"):
                asyncio.run(call_tool("download_rfc", {"rfc_id": "invalid"}))

    def test_download_rfc_network_error(self):
        import requests

        from mcp_rfc_editor import server

        with patch.object(server, "RFCEditor") as MockEditor:
            mock_instance = MockEditor.return_value
            mock_instance.download.side_effect = requests.RequestException(
                "Network error"
            )
            import asyncio

            from mcp_rfc_editor.server import call_tool

            with pytest.raises(requests.RequestException, match="Network error"):
                asyncio.run(call_tool("download_rfc", {"rfc_id": "9999"}))
