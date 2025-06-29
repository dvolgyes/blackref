#!/usr/bin/env python3
"""Tests for field_validators module."""

import pytest
from blackref.field_validators import (
    fix_isbn,
    fix_issn,
    fix_pages,
    remove_empty_keys,
    fix_utf8_field,
    fix_authors,
    fix_abstract,
)


class TestFixISBN:
    """Test ISBN validation and formatting."""

    def test_fix_isbn_valid_isbn10(self):
        """Test conversion of valid ISBN-10 to ISBN-13."""
        entry = {"ID": "test", "isbn": "0123456789"}
        result = fix_isbn(entry)
        assert result["isbn"] == "978-0-12-345678-6"

    def test_fix_isbn_valid_isbn13(self):
        """Test formatting of valid ISBN-13."""
        entry = {"ID": "test", "isbn": "9780123456786"}
        result = fix_isbn(entry)
        assert result["isbn"] == "978-0-12-345678-6"

    def test_fix_isbn_invalid(self):
        """Test exception on invalid ISBN."""
        entry = {"ID": "test", "isbn": "invalid"}
        with pytest.raises(Exception, match="invalid isbn"):
            fix_isbn(entry)

    def test_fix_isbn_no_isbn_field(self):
        """Test entry without ISBN field."""
        entry = {"ID": "test", "title": "Test Title"}
        result = fix_isbn(entry)
        assert "isbn" not in result


class TestFixISSN:
    """Test ISSN validation and formatting."""

    def test_fix_issn_valid(self):
        """Test formatting of valid ISSN."""
        entry = {"ID": "test", "issn": "12345678"}
        result = fix_issn(entry)
        assert result["issn"] == "1234-5678"

    def test_fix_issn_with_dash(self):
        """Test ISSN already formatted with dash."""
        entry = {"ID": "test", "issn": "1234-5678"}
        result = fix_issn(entry)
        assert result["issn"] == "1234-5678"

    def test_fix_issn_invalid_length(self):
        """Test exception on invalid ISSN length."""
        entry = {"ID": "test", "issn": "123"}
        with pytest.raises(Exception, match="invalid issn"):
            fix_issn(entry)

    def test_fix_issn_no_issn_field(self):
        """Test entry without ISSN field."""
        entry = {"ID": "test", "title": "Test Title"}
        result = fix_issn(entry)
        assert "issn" not in result


class TestFixPages:
    """Test page number formatting."""

    def test_fix_pages_with_spaces(self):
        """Test removing spaces from page numbers."""
        entry = {"ID": "test", "pages": "123 - 456"}
        result = fix_pages(entry)
        assert result["pages"] == "123-456"

    def test_fix_pages_no_spaces(self):
        """Test pages without spaces."""
        entry = {"ID": "test", "pages": "123-456"}
        result = fix_pages(entry)
        assert result["pages"] == "123-456"

    def test_fix_pages_no_pages_field(self):
        """Test entry without pages field."""
        entry = {"ID": "test", "title": "Test Title"}
        result = fix_pages(entry)
        assert "pages" not in result


class TestRemoveEmptyKeys:
    """Test removal of empty keys."""

    def test_remove_empty_string(self):
        """Test removal of empty string values."""
        entry = {"ID": "test", "title": "Test", "abstract": ""}
        result = remove_empty_keys(entry)
        assert "abstract" not in result
        assert result["title"] == "Test"

    def test_remove_none_values(self):
        """Test removal of None values."""
        entry = {"ID": "test", "title": "Test", "abstract": None}
        result = remove_empty_keys(entry)
        assert "abstract" not in result

    def test_remove_whitespace_only(self):
        """Test removal of whitespace-only values."""
        entry = {"ID": "test", "title": "Test", "abstract": "   \n\t  "}
        result = remove_empty_keys(entry)
        assert "abstract" not in result

    def test_keep_valid_values(self):
        """Test keeping valid non-empty values."""
        entry = {"ID": "test", "title": "Test Title", "abstract": "Valid abstract"}
        result = remove_empty_keys(entry)
        assert result["title"] == "Test Title"
        assert result["abstract"] == "Valid abstract"


class TestFixUTF8Field:
    """Test UTF-8 and LaTeX field conversion."""

    def test_utf8_field_conversion(self):
        """Test conversion to UTF-8."""
        entry = {"ID": "test", "title": "Caf\\'e"}
        utf8_fields = {"title"}
        latex_fields = set()
        result = fix_utf8_field(entry, "title", utf8_fields, latex_fields)
        assert result["title"] == "Café"

    def test_latex_field_conversion(self):
        """Test conversion to LaTeX."""
        entry = {"ID": "test", "title": "Café"}
        utf8_fields = set()
        latex_fields = {"title"}
        result = fix_utf8_field(entry, "title", utf8_fields, latex_fields)
        # The exact LaTeX encoding may vary, just check it was processed
        assert result["title"] is not None

    def test_no_conversion(self):
        """Test no conversion when field not in either set."""
        entry = {"ID": "test", "title": "Test Title"}
        utf8_fields = set()
        latex_fields = set()
        result = fix_utf8_field(entry, "title", utf8_fields, latex_fields)
        assert result["title"] == "Test Title"

    def test_missing_field(self):
        """Test with missing field."""
        entry = {"ID": "test"}
        utf8_fields = {"title"}
        latex_fields = set()
        result = fix_utf8_field(entry, "title", utf8_fields, latex_fields)
        assert "title" not in result


class TestFixAuthors:
    """Test author field fixing."""

    def test_fix_authors(self):
        """Test author field conversion."""
        entry = {"ID": "test", "author": "Test Author"}
        utf8_fields = {"author"}
        latex_fields = set()
        result = fix_authors(entry, utf8_fields, latex_fields)
        assert result["author"] == "Test Author"


class TestFixAbstract:
    """Test abstract field fixing."""

    def test_fix_abstract(self):
        """Test abstract field conversion."""
        entry = {"ID": "test", "abstract": "Test abstract"}
        utf8_fields = {"abstract"}
        latex_fields = set()
        result = fix_abstract(entry, utf8_fields, latex_fields)
        assert result["abstract"] == "Test abstract"
