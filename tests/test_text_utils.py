#!/usr/bin/env python3
"""Tests for text_utils module."""

from blackref.text_utils import fix_paragraphs, fix_wrap


class TestFixParagraphs:
    """Test paragraph formatting for structured abstracts."""

    def test_fix_paragraphs_background(self):
        """Test paragraph formatting with BACKGROUND keyword."""
        text = "Some text BACKGROUND This is background"
        result = fix_paragraphs(text)
        assert "\n\nBACKGROUND" in result

    def test_fix_paragraphs_background_lowercase(self):
        """Test paragraph formatting with background keyword."""
        text = "Some text Background This is background"
        result = fix_paragraphs(text)
        assert "\n\nBackground" in result

    def test_fix_paragraphs_methods(self):
        """Test paragraph formatting with METHODS keyword."""
        text = "Some text METHODS This is methods"
        result = fix_paragraphs(text)
        assert "\n\nMETHODS" in result

    def test_fix_paragraphs_results(self):
        """Test paragraph formatting with RESULTS keyword."""
        text = "Some text RESULTS This is results"
        result = fix_paragraphs(text)
        assert "\n\nRESULTS" in result

    def test_fix_paragraphs_conclusion(self):
        """Test paragraph formatting with CONCLUSION keyword."""
        text = "Some text CONCLUSION This is conclusion"
        result = fix_paragraphs(text)
        assert "\n\nCONCLUSION" in result

    def test_fix_paragraphs_no_keywords(self):
        """Test paragraph formatting without keywords."""
        text = "Some regular text without keywords"
        result = fix_paragraphs(text)
        assert result == text


class TestFixWrap:
    """Test text wrapping and formatting."""

    def test_fix_wrap_simple_text(self):
        """Test wrapping of simple text."""
        text = "This is a simple text"
        result = fix_wrap(text, "title", indent=10)
        assert result == "This is a simple text"

    def test_fix_wrap_removes_extra_whitespace(self):
        """Test removal of extra whitespace."""
        text = "This   is   a   text   with   extra   spaces"
        result = fix_wrap(text, "title", indent=10)
        assert result == "This is a text with extra spaces"

    def test_fix_wrap_abstract_long(self):
        """Test wrapping of long abstract."""
        text = "This is a very long abstract text that should be wrapped across multiple lines to test the wrapping functionality."
        result = fix_wrap(text, "abstract", indent=10, line_length=80)
        assert "\n" in result

    def test_fix_wrap_title_long(self):
        """Test wrapping of long title."""
        text = "This is a very long title that should be wrapped across multiple lines to test the wrapping functionality."
        result = fix_wrap(text, "title", indent=10, line_length=80)
        assert "\n" in result

    def test_fix_wrap_author_single(self):
        """Test formatting of single author."""
        text = "John Doe"
        result = fix_wrap(text, "author", indent=10)
        assert result == "John Doe"

    def test_fix_wrap_author_multiple(self):
        """Test formatting of multiple authors."""
        text = "John Doe and Jane Smith and Bob Johnson"
        result = fix_wrap(text, "author", indent=10)
        assert "and" in result
        assert "\n" in result

    def test_fix_wrap_editor_multiple(self):
        """Test formatting of multiple editors."""
        text = "John Doe and Jane Smith"
        result = fix_wrap(text, "editor", indent=10)
        assert "and" in result
        assert "\n" in result

    def test_fix_wrap_keywords_semicolon(self):
        """Test formatting of keywords with semicolons."""
        text = "keyword1; keyword2; keyword3"
        result = fix_wrap(text, "keywords", indent=10)
        assert "keyword1, keyword2, keyword3" in result

    def test_fix_wrap_keywords_comma(self):
        """Test formatting of keywords with commas."""
        text = "keyword1, keyword2, keyword3"
        result = fix_wrap(text, "keywords", indent=10)
        assert "keyword1, keyword2, keyword3" in result

    def test_fix_wrap_keywords_underscore(self):
        """Test formatting of keywords with underscores."""
        text = "keyword_1, keyword_2"
        result = fix_wrap(text, "keyword", indent=10)
        assert "keyword 1, keyword 2" in result

    def test_fix_wrap_keywords_long(self):
        """Test wrapping of long keyword list."""
        text = "keyword1, keyword2, keyword3, keyword4, keyword5, keyword6, keyword7, keyword8, keyword9, keyword10"
        result = fix_wrap(text, "keywords", indent=10, line_length=80)
        assert "\n" in result

    def test_fix_wrap_other_field(self):
        """Test formatting of other fields."""
        text = "Some other field content"
        result = fix_wrap(text, "journal", indent=10)
        assert result == "Some other field content"
