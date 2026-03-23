import os
import tempfile

import pytest
from rfc_editor import RFCAuthor, RFCDocument, RFCEditor


@pytest.fixture
def sample_rfc_content():
    return """RFC 1234
Category: Standards Track
Title: Example RFC Document

Abstract:
This is an example abstract for testing purposes.

1. Introduction
   This is the introduction section.

2. Main Body
   This is the main body section.
"""


@pytest.fixture
def temp_rfc_file(sample_rfc_content):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(sample_rfc_content)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def editor():
    return RFCEditor()


@pytest.fixture
def sample_document():
    return RFCDocument(
        rfc_number="1234",
        title="Test RFC",
        abstract="Test abstract",
        authors=[
            RFCAuthor(name="John Doe", organization="Test Org", email="john@test.com")
        ],
    )
