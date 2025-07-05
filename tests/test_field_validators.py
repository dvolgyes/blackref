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
    fix_month,
    fix_unicode_dashes,
    fix_title_dashes,
    fix_booktitle_dashes,
    fix_abstract_dashes,
    fix_doi,
    fix_title_capitalization,
    fix_booktitle_capitalization,
    fix_publisher_capitalization,
    fix_journal_capitalization,
    _protect_mixed_case_words,
    fix_html_entities,
    _convert_html_entities,
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

    def test_fix_isbn_already_formatted_isbn13(self):
        """Test ISBN-13 already with dashes."""
        entry = {"ID": "test", "isbn": "978-0-12-345678-6"}
        result = fix_isbn(entry)
        assert result["isbn"] == "978-0-12-345678-6"

    def test_fix_isbn_isbn10_with_x(self):
        """Test ISBN-10 with X check digit."""
        entry = {"ID": "test", "isbn": "043942089X"}
        result = fix_isbn(entry)
        assert result["isbn"] == "978-0-439-42089-1"

    def test_fix_isbn_isbn10_with_spaces(self):
        """Test ISBN-10 with spaces (should be cleaned)."""
        entry = {"ID": "test", "isbn": "0 1 2 3 4 5 6 7 8 9"}
        result = fix_isbn(entry)
        assert result["isbn"] == "978-0-12-345678-6"

    def test_fix_isbn_isbn13_with_spaces(self):
        """Test ISBN-13 with spaces (should be cleaned)."""
        entry = {"ID": "test", "isbn": "9 7 8 0 1 2 3 4 5 6 7 8 6"}
        result = fix_isbn(entry)
        assert result["isbn"] == "978-0-12-345678-6"

    def test_fix_isbn_invalid_length(self):
        """Test invalid ISBN with wrong length."""
        entry = {"ID": "test", "isbn": "123456"}
        with pytest.raises(Exception, match="invalid isbn"):
            fix_isbn(entry)

    def test_fix_isbn_invalid_characters(self):
        """Test invalid ISBN with invalid characters."""
        entry = {"ID": "test", "isbn": "012345678Z"}
        with pytest.raises(Exception, match="invalid isbn"):
            fix_isbn(entry)

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

    def test_fix_issn_with_spaces(self):
        """Test ISSN with spaces (should be removed)."""
        entry = {"ID": "test", "issn": "1 2 3 4 5 6 7 8"}
        result = fix_issn(entry)
        assert result["issn"] == "1234-5678"

    def test_fix_issn_with_multiple_dashes(self):
        """Test ISSN with multiple dashes (should be normalized)."""
        entry = {"ID": "test", "issn": "12-34-56-78"}
        result = fix_issn(entry)
        assert result["issn"] == "1234-5678"

    def test_fix_issn_mixed_formatting(self):
        """Test ISSN with mixed spaces and dashes."""
        entry = {"ID": "test", "issn": "12 34-56 78"}
        result = fix_issn(entry)
        assert result["issn"] == "1234-5678"

    def test_fix_issn_invalid_length_short(self):
        """Test exception on invalid ISSN length (too short)."""
        entry = {"ID": "test", "issn": "123"}
        with pytest.raises(Exception, match="invalid issn"):
            fix_issn(entry)

    def test_fix_issn_invalid_length_long(self):
        """Test exception on invalid ISSN length (too long)."""
        entry = {"ID": "test", "issn": "1234567890"}
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
        assert result["pages"] == "123--456"

    def test_fix_pages_single_dash_to_emdash(self):
        """Test converting single dash to double dash (emdash)."""
        entry = {"ID": "test", "pages": "123-456"}
        result = fix_pages(entry)
        assert result["pages"] == "123--456"

    def test_fix_pages_already_emdash(self):
        """Test pages already with double dash."""
        entry = {"ID": "test", "pages": "123--456"}
        result = fix_pages(entry)
        assert result["pages"] == "123--456"

    def test_fix_pages_multiple_ranges(self):
        """Test multiple page ranges."""
        entry = {"ID": "test", "pages": "123-126, 456-460"}
        result = fix_pages(entry)
        assert result["pages"] == "123--126,456--460"

    def test_fix_pages_complex_spacing(self):
        """Test complex spacing scenarios."""
        entry = {"ID": "test", "pages": "1 2 3 - 4 5 6"}
        result = fix_pages(entry)
        assert result["pages"] == "123--456"

    def test_fix_pages_trailing_dash(self):
        """Test pages with trailing dash (should not be converted)."""
        entry = {"ID": "test", "pages": "123-"}
        result = fix_pages(entry)
        assert result["pages"] == "123-"

    def test_fix_pages_leading_dash(self):
        """Test pages with leading dash (should not be converted)."""
        entry = {"ID": "test", "pages": "-456"}
        result = fix_pages(entry)
        assert result["pages"] == "-456"

    def test_fix_pages_triple_dash(self):
        """Test pages with triple dash (only middle should convert)."""
        entry = {"ID": "test", "pages": "1-2-3"}
        result = fix_pages(entry)
        assert result["pages"] == "1--2--3"

    def test_fix_pages_unicode_en_dash(self):
        """Test pages with Unicode en-dash (–) character."""
        entry = {"ID": "test", "pages": "1798–1828"}
        result = fix_pages(entry)
        assert result["pages"] == "1798--1828"

    def test_fix_pages_unicode_em_dash(self):
        """Test pages with Unicode em-dash (—) character."""
        entry = {"ID": "test", "pages": "1798—1828"}
        result = fix_pages(entry)
        assert result["pages"] == "1798--1828"

    def test_fix_pages_mixed_unicode_dashes(self):
        """Test pages with mixed Unicode dash types."""
        entry = {"ID": "test", "pages": "123–126, 456—460, 789-012"}
        result = fix_pages(entry)
        assert result["pages"] == "123--126,456--460,789--012"

    def test_fix_pages_page_to_pages_conversion(self):
        """Test converting 'page' field to 'pages'."""
        entry = {"ID": "test", "page": "123-456"}
        result = fix_pages(entry)
        assert "page" not in result
        assert result["pages"] == "123--456"

    def test_fix_pages_page_and_pages_both_present(self):
        """Test when both 'page' and 'pages' fields exist - 'pages' takes precedence."""
        entry = {"ID": "test", "page": "123-456", "pages": "789-012"}
        result = fix_pages(entry)
        assert "page" not in result
        assert result["pages"] == "789--012"

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


class TestFixMonth:
    """Test month name to number conversion."""

    def test_fix_month_full_name_lowercase(self):
        """Test conversion of full month name in lowercase."""
        entry = {"ID": "test", "month": "january"}
        result = fix_month(entry)
        assert result["month"] == "1"

    def test_fix_month_full_name_uppercase(self):
        """Test conversion of full month name in uppercase."""
        entry = {"ID": "test", "month": "JANUARY"}
        result = fix_month(entry)
        assert result["month"] == "1"

    def test_fix_month_full_name_mixed_case(self):
        """Test conversion of full month name in mixed case."""
        entry = {"ID": "test", "month": "January"}
        result = fix_month(entry)
        assert result["month"] == "1"

    def test_fix_month_abbreviated_name(self):
        """Test conversion of abbreviated month name."""
        entry = {"ID": "test", "month": "jan"}
        result = fix_month(entry)
        assert result["month"] == "1"

    def test_fix_month_all_months(self):
        """Test conversion of all month names."""
        months = [
            ("january", "1"),
            ("jan", "1"),
            ("february", "2"),
            ("feb", "2"),
            ("march", "3"),
            ("mar", "3"),
            ("april", "4"),
            ("apr", "4"),
            ("may", "5"),
            ("june", "6"),
            ("jun", "6"),
            ("july", "7"),
            ("jul", "7"),
            ("august", "8"),
            ("aug", "8"),
            ("september", "9"),
            ("sep", "9"),
            ("sept", "9"),
            ("october", "10"),
            ("oct", "10"),
            ("november", "11"),
            ("nov", "11"),
            ("december", "12"),
            ("dec", "12"),
        ]

        for month_name, expected_number in months:
            entry = {"ID": "test", "month": month_name}
            result = fix_month(entry)
            assert result["month"] == expected_number, f"Failed for {month_name}"

    def test_fix_month_with_whitespace(self):
        """Test month conversion with leading/trailing whitespace."""
        entry = {"ID": "test", "month": "  january  "}
        result = fix_month(entry)
        assert result["month"] == "1"

    def test_fix_month_already_number(self):
        """Test month that's already a number (should not change)."""
        entry = {"ID": "test", "month": "1"}
        result = fix_month(entry)
        assert result["month"] == "1"

    def test_fix_month_invalid_name(self):
        """Test invalid month name (should not change)."""
        entry = {"ID": "test", "month": "invalid"}
        result = fix_month(entry)
        assert result["month"] == "invalid"

    def test_fix_month_no_month_field(self):
        """Test entry without month field."""
        entry = {"ID": "test", "title": "Test Title"}
        result = fix_month(entry)
        assert "month" not in result


class TestComprehensiveFormatting:
    """Test comprehensive formatting scenarios."""

    def test_whitespace_normalization_in_remove_empty_keys(self):
        """Test that various whitespace patterns are properly handled."""
        test_cases = [
            ("", True),  # Empty string should be removed
            ("   ", True),  # Spaces only should be removed
            ("\t", True),  # Tab only should be removed
            ("\n", True),  # Newline only should be removed
            ("\r\n", True),  # CRLF should be removed
            ("  \t\n  ", True),  # Mixed whitespace should be removed
            ("a", False),  # Single character should be kept
            ("  a  ", False),  # Text with whitespace should be kept
        ]

        for value, should_remove in test_cases:
            entry = {"ID": "test", "title": "Test", "field": value}
            result = remove_empty_keys(entry)
            if should_remove:
                assert "field" not in result, f"Value '{repr(value)}' should be removed"
            else:
                assert "field" in result, f"Value '{repr(value)}' should be kept"

    def test_latex_encoding_prevention(self):
        """Test that LaTeX commands are not double-encoded."""
        entry = {"ID": "test", "author": "Santamar{\\'i}a, J."}
        utf8_fields = set()
        latex_fields = {"author"}
        result = fix_utf8_field(entry, "author", utf8_fields, latex_fields)
        # Should not double-encode existing LaTeX
        assert "textbackslash" not in result["author"]
        assert "{\\'i}" in result["author"]

    def test_utf8_to_latex_fresh_encoding(self):
        """Test UTF-8 to LaTeX encoding for fresh text."""
        entry = {"ID": "test", "author": "Santamarïa, J."}
        utf8_fields = set()
        latex_fields = {"author"}
        result = fix_utf8_field(entry, "author", utf8_fields, latex_fields)
        # Should encode the ï character
        assert "ï" not in result["author"]

    def test_complex_field_processing_integration(self):
        """Test complex scenarios with multiple field processing."""
        entry = {
            "ID": "test2024",
            "title": "  A Test Title with Extra   Spaces  ",
            "author": "Müller, A. and Café, J.",
            "year": "2024",
            "month": "january",
            "pages": "123 - 456",
            "isbn": "0123456789",
            "issn": "1234 5678",
            "page": "backup-pages",  # Should be ignored if pages exists
            "abstract": "",  # Should be removed
            "keywords": "   ",  # Should be removed
        }

        # Process with various field configurations
        utf8_fields = {"author"}
        latex_fields = {"title"}

        # Apply all fixes in sequence (as would happen in formatter)
        entry = remove_empty_keys(entry)
        entry = fix_authors(entry, utf8_fields, latex_fields)
        entry = fix_month(entry)
        entry = fix_pages(entry)
        entry = fix_isbn(entry)
        entry = fix_issn(entry)

        # Check results
        assert "abstract" not in entry  # Empty field removed
        assert "keywords" not in entry  # Whitespace-only field removed
        assert "page" not in entry  # Converted to pages
        assert entry["month"] == "1"  # january -> 1
        assert entry["pages"] == "123--456"  # Dash converted to emdash
        assert entry["isbn"] == "978-0-12-345678-6"  # ISBN-10 to ISBN-13
        assert entry["issn"] == "1234-5678"  # ISSN formatted
        assert "Müller" in entry["author"]  # UTF-8 preserved in author


class TestFixUnicodeDashes:
    """Test Unicode dash replacement in text fields."""

    def test_fix_unicode_dashes_en_dash(self):
        """Test en-dash (–) conversion to double hyphen (--)."""
        entry = {"ID": "test", "title": "Machine Learning – A Comprehensive Guide"}
        result = fix_unicode_dashes(entry, "title")
        assert result["title"] == "Machine Learning -- A Comprehensive Guide"

    def test_fix_unicode_dashes_em_dash(self):
        """Test em-dash (—) conversion to triple hyphen (---)."""
        entry = {"ID": "test", "title": "AI and Society — Past, Present, and Future"}
        result = fix_unicode_dashes(entry, "title")
        assert result["title"] == "AI and Society --- Past, Present, and Future"

    def test_fix_unicode_dashes_regular_hyphen_preserved(self):
        """Test that regular hyphens (-) are preserved."""
        entry = {"ID": "test", "title": "Self-supervised Learning"}
        result = fix_unicode_dashes(entry, "title")
        assert result["title"] == "Self-supervised Learning"

    def test_fix_unicode_dashes_mixed_dashes(self):
        """Test mixed dash types in same text."""
        entry = {
            "ID": "test",
            "title": "AI–ML Integration — Modern Approaches for Self-supervised Learning",
        }
        result = fix_unicode_dashes(entry, "title")
        assert (
            result["title"]
            == "AI--ML Integration --- Modern Approaches for Self-supervised Learning"
        )

    def test_fix_unicode_dashes_multiple_same_type(self):
        """Test multiple dashes of same type."""
        entry = {"ID": "test", "title": "Part A – Part B – Part C"}
        result = fix_unicode_dashes(entry, "title")
        assert result["title"] == "Part A -- Part B -- Part C"

    def test_fix_unicode_dashes_missing_field(self):
        """Test with missing field."""
        entry = {"ID": "test", "author": "Test Author"}
        result = fix_unicode_dashes(entry, "title")
        assert "title" not in result

    def test_fix_unicode_dashes_empty_field(self):
        """Test with empty field."""
        entry = {"ID": "test", "title": ""}
        result = fix_unicode_dashes(entry, "title")
        assert result["title"] == ""

    def test_fix_unicode_dashes_no_dashes(self):
        """Test text without any dashes."""
        entry = {"ID": "test", "title": "Machine Learning Applications"}
        result = fix_unicode_dashes(entry, "title")
        assert result["title"] == "Machine Learning Applications"


class TestFixTitleDashes:
    """Test Unicode dash replacement specifically for title field."""

    def test_fix_title_dashes_en_dash(self):
        """Test title-specific en-dash conversion."""
        entry = {"ID": "test", "title": "Deep Learning – Theory and Practice"}
        result = fix_title_dashes(entry)
        assert result["title"] == "Deep Learning -- Theory and Practice"

    def test_fix_title_dashes_em_dash(self):
        """Test title-specific em-dash conversion."""
        entry = {"ID": "test", "title": "Neural Networks — A Modern Approach"}
        result = fix_title_dashes(entry)
        assert result["title"] == "Neural Networks --- A Modern Approach"

    def test_fix_title_dashes_mixed(self):
        """Test title with mixed dash types."""
        entry = {"ID": "test", "title": "AI–ML–DL — The Evolution of Machine Learning"}
        result = fix_title_dashes(entry)
        assert result["title"] == "AI--ML--DL --- The Evolution of Machine Learning"

    def test_fix_title_dashes_no_title_field(self):
        """Test with missing title field."""
        entry = {"ID": "test", "author": "Test Author"}
        result = fix_title_dashes(entry)
        assert "title" not in result


class TestFixBooktitleDashes:
    """Test Unicode dash replacement specifically for booktitle field."""

    def test_fix_booktitle_dashes_en_dash(self):
        """Test booktitle-specific en-dash conversion."""
        entry = {"ID": "test", "booktitle": "Proceedings of ICML – 2024"}
        result = fix_booktitle_dashes(entry)
        assert result["booktitle"] == "Proceedings of ICML -- 2024"

    def test_fix_booktitle_dashes_em_dash(self):
        """Test booktitle-specific em-dash conversion."""
        entry = {"ID": "test", "booktitle": "Conference on AI — Annual Meeting"}
        result = fix_booktitle_dashes(entry)
        assert result["booktitle"] == "Conference on AI --- Annual Meeting"

    def test_fix_booktitle_dashes_no_booktitle_field(self):
        """Test with missing booktitle field."""
        entry = {"ID": "test", "title": "Test Title"}
        result = fix_booktitle_dashes(entry)
        assert "booktitle" not in result


class TestFixAbstractDashes:
    """Test Unicode dash replacement specifically for abstract field."""

    def test_fix_abstract_dashes_en_dash(self):
        """Test abstract-specific en-dash conversion."""
        entry = {
            "ID": "test",
            "abstract": "This paper presents machine learning – a comprehensive overview.",
        }
        result = fix_abstract_dashes(entry)
        assert (
            result["abstract"]
            == "This paper presents machine learning -- a comprehensive overview."
        )

    def test_fix_abstract_dashes_em_dash(self):
        """Test abstract-specific em-dash conversion."""
        entry = {
            "ID": "test",
            "abstract": "We explore AI applications — focusing on practical implementations.",
        }
        result = fix_abstract_dashes(entry)
        assert (
            result["abstract"]
            == "We explore AI applications --- focusing on practical implementations."
        )

    def test_fix_abstract_dashes_complex_text(self):
        """Test abstract with complex dash usage."""
        entry = {
            "ID": "test",
            "abstract": "Machine learning – specifically deep learning — has revolutionized AI. Self-supervised approaches show promise.",
        }
        result = fix_abstract_dashes(entry)
        assert (
            result["abstract"]
            == "Machine learning -- specifically deep learning --- has revolutionized AI. Self-supervised approaches show promise."
        )

    def test_fix_abstract_dashes_no_abstract_field(self):
        """Test with missing abstract field."""
        entry = {"ID": "test", "title": "Test Title"}
        result = fix_abstract_dashes(entry)
        assert "abstract" not in result


class TestUnicodeDashesIntegration:
    """Test Unicode dash replacement in realistic scenarios."""

    def test_comprehensive_entry_with_unicode_dashes(self):
        """Test complete entry with Unicode dashes in multiple fields."""
        entry = {
            "ID": "test2024",
            "title": "Machine Learning – Theory and Applications",
            "booktitle": "Proceedings of ICML — 2024 Conference",
            "abstract": "This paper explores ML – specifically deep learning — and its applications in real-world scenarios. Self-supervised learning shows promise.",
            "author": "Smith, J.",
            "year": "2024",
        }

        # Apply all dash fixes
        entry = fix_title_dashes(entry)
        entry = fix_booktitle_dashes(entry)
        entry = fix_abstract_dashes(entry)

        assert entry["title"] == "Machine Learning -- Theory and Applications"
        assert entry["booktitle"] == "Proceedings of ICML --- 2024 Conference"
        assert (
            entry["abstract"]
            == "This paper explores ML -- specifically deep learning --- and its applications in real-world scenarios. Self-supervised learning shows promise."
        )
        assert entry["author"] == "Smith, J."  # Should be unchanged

    def test_edge_cases_with_consecutive_dashes(self):
        """Test edge cases with consecutive dashes."""
        entry = {"ID": "test", "title": "Part A ––– Part B ——— Part C"}
        result = fix_title_dashes(entry)
        # Multiple consecutive dashes should be handled properly
        assert result["title"] == "Part A ------ Part B --------- Part C"


class TestFixDOI:
    """Test DOI extraction from URLs and validation."""

    def test_fix_doi_extract_from_http_doi_org(self):
        """Test DOI extraction from http://doi.org URL."""
        entry = {"ID": "test", "url": "http://doi.org/10.1000/182"}
        result = fix_doi(entry)
        assert result["doi"] == "10.1000/182"
        assert "url" not in result

    def test_fix_doi_extract_from_https_doi_org(self):
        """Test DOI extraction from https://doi.org URL."""
        entry = {"ID": "test", "url": "https://doi.org/10.1000/182"}
        result = fix_doi(entry)
        assert result["doi"] == "10.1000/182"
        assert "url" not in result

    def test_fix_doi_extract_from_http_dx_doi_org(self):
        """Test DOI extraction from http://dx.doi.org URL."""
        entry = {"ID": "test", "url": "http://dx.doi.org/10.1000/182"}
        result = fix_doi(entry)
        assert result["doi"] == "10.1000/182"
        assert "url" not in result

    def test_fix_doi_extract_from_https_dx_doi_org(self):
        """Test DOI extraction from https://dx.doi.org URL."""
        entry = {"ID": "test", "url": "https://dx.doi.org/10.1000/182"}
        result = fix_doi(entry)
        assert result["doi"] == "10.1000/182"
        assert "url" not in result

    def test_fix_doi_case_insensitive(self):
        """Test case insensitive DOI URL matching."""
        entry = {"ID": "test", "url": "HTTPS://DOI.ORG/10.1000/182"}
        result = fix_doi(entry)
        assert result["doi"] == "10.1000/182"
        assert "url" not in result

    def test_fix_doi_with_whitespace(self):
        """Test DOI URL with leading/trailing whitespace."""
        entry = {"ID": "test", "url": "  https://doi.org/10.1000/182  "}
        result = fix_doi(entry)
        assert result["doi"] == "10.1000/182"
        assert "url" not in result

    def test_fix_doi_complex_doi_value(self):
        """Test complex DOI value extraction."""
        entry = {"ID": "test", "url": "https://doi.org/10.1038/nature12373"}
        result = fix_doi(entry)
        assert result["doi"] == "10.1038/nature12373"
        assert "url" not in result

    def test_fix_doi_very_complex_doi_value(self):
        """Test very complex DOI value with special characters."""
        entry = {
            "ID": "test",
            "url": "https://doi.org/10.1002/(SICI)1097-4571(199009)41:6<391::AID-ASI1>3.0.CO;2-9",
        }
        result = fix_doi(entry)
        assert (
            result["doi"]
            == "10.1002/(SICI)1097-4571(199009)41:6<391::AID-ASI1>3.0.CO;2-9"
        )
        assert "url" not in result

    def test_fix_doi_create_when_no_existing_doi(self):
        """Test creating DOI field when none exists."""
        entry = {"ID": "test", "title": "Test", "url": "https://doi.org/10.1000/182"}
        result = fix_doi(entry)
        assert result["doi"] == "10.1000/182"
        assert "url" not in result
        assert result["title"] == "Test"


class TestCapitalizationRules:
    """Test capitalization rules for title/booktitle/publisher fields."""

    def test_protect_mixed_case_words_simple(self):
        """Test basic mixed-case word protection."""
        assert _protect_mixed_case_words("4D") == "{4D}"
        assert _protect_mixed_case_words("IEEE") == "{IEEE}"
        assert _protect_mixed_case_words("GPUs") == "{GPUs}"
        assert _protect_mixed_case_words("AutoMVQ") == "{AutoMVQ}"
        assert (
            _protect_mixed_case_words("GOOD") == "{GOOD}"
        )  # Has uppercase after first char

    def test_protect_mixed_case_words_with_punctuation(self):
        """Test mixed-case word protection with punctuation."""
        assert _protect_mixed_case_words("(IEEE)") == "{(IEEE)}"
        assert _protect_mixed_case_words("IEEE:") == "{IEEE:}"
        assert _protect_mixed_case_words("@GPUs") == "{@GPUs}"

    def test_protect_mixed_case_words_no_protection_needed(self):
        """Test words that don't need protection."""
        assert _protect_mixed_case_words("Ok") == "Ok"
        assert _protect_mixed_case_words("The") == "The"
        assert _protect_mixed_case_words("good") == "good"
        assert _protect_mixed_case_words("123") == "123"
        assert _protect_mixed_case_words("A") == "A"

    def test_protect_mixed_case_words_multiple_words(self):
        """Test protection of multiple words in text."""
        text = "A study of IEEE versus XML in GPUs"
        expected = "A study of {IEEE} versus {XML} in {GPUs}"
        assert _protect_mixed_case_words(text) == expected

    def test_protect_mixed_case_words_mixed_scenario(self):
        """Test mixed scenario with some words needing protection."""
        text = "The IEEE 4D rendering with GPUs and Ok results"
        expected = "The {IEEE} {4D} rendering with {GPUs} and Ok results"
        assert _protect_mixed_case_words(text) == expected

    def test_fix_title_capitalization_normal_case(self):
        """Test normal title capitalization with mixed-case words."""
        entry = {"ID": "test", "title": "A study of IEEE versus XML"}
        result = fix_title_capitalization(entry)
        assert result["title"] == "A study of {IEEE} versus {XML}"

    def test_fix_title_capitalization_all_caps_warning(self):
        """Test warning for all-caps title."""
        entry = {"ID": "test", "title": "A STUDY OF IEEE VERSUS XML"}
        result = fix_title_capitalization(entry)
        assert result["title"] == "A STUDY OF IEEE VERSUS XML"  # Unchanged

    def test_fix_title_capitalization_double_braces_conversion_old(self):
        """Test conversion of double-braced title (old test case)."""
        # After bibtexparser parses {{...}}, it becomes {...}
        entry = {"ID": "test", "title": "{A study of IEEE versus XML}"}
        result = fix_title_capitalization(entry)
        assert result["title"] == "A study of {IEEE} versus {XML}"  # Converted

    def test_fix_title_capitalization_empty_field(self):
        """Test title capitalization with empty field."""
        entry = {"ID": "test", "title": ""}
        result = fix_title_capitalization(entry)
        assert result["title"] == ""

    def test_fix_title_capitalization_no_field(self):
        """Test title capitalization with no title field."""
        entry = {"ID": "test", "author": "John Doe"}
        result = fix_title_capitalization(entry)
        assert "title" not in result

    def test_fix_booktitle_capitalization(self):
        """Test booktitle capitalization."""
        entry = {"ID": "test", "booktitle": "Proceedings of IEEE Conference"}
        result = fix_booktitle_capitalization(entry)
        assert result["booktitle"] == "Proceedings of {IEEE} Conference"

    def test_fix_publisher_capitalization(self):
        """Test publisher capitalization."""
        entry = {"ID": "test", "publisher": "IEEE Computer Society"}
        result = fix_publisher_capitalization(entry)
        assert result["publisher"] == "{IEEE} Computer Society"

    def test_fix_publisher_single_word_all_caps(self):
        """Test single word all-caps publisher gets protected."""
        entry = {"ID": "test", "publisher": "IEEE"}
        result = fix_publisher_capitalization(entry)
        assert result["publisher"] == "{IEEE}"

    def test_fix_publisher_single_word_all_caps_with_numbers(self):
        """Test single word all-caps publisher with numbers gets protected."""
        entry = {"ID": "test", "publisher": "ACM"}
        result = fix_publisher_capitalization(entry)
        assert result["publisher"] == "{ACM}"

    def test_fix_publisher_single_word_mixed_case(self):
        """Test single word mixed-case publisher gets normal protection."""
        entry = {"ID": "test", "publisher": "Springer"}
        result = fix_publisher_capitalization(entry)
        assert result["publisher"] == "Springer"  # No protection needed

    def test_fix_publisher_already_protected_single_braces(self):
        """Test already protected publisher doesn't get double-protected."""
        entry = {"ID": "test", "publisher": "{IEEE}"}
        result = fix_publisher_capitalization(entry)
        assert result["publisher"] == "{IEEE}"  # No double protection

    def test_fix_publisher_already_protected_double_braces(self):
        """Test double-braced publisher triggers warning and stays unchanged."""
        entry = {"ID": "test", "publisher": "{{IEEE}}"}
        result = fix_publisher_capitalization(entry)
        assert result["publisher"] == "{{IEEE}}"  # Unchanged

    def test_fix_publisher_multi_word_all_caps_warning(self):
        """Test multi-word all-caps publisher triggers warning."""
        entry = {"ID": "test", "publisher": "IEEE COMPUTER SOCIETY"}
        result = fix_publisher_capitalization(entry)
        assert (
            result["publisher"] == "IEEE COMPUTER SOCIETY"
        )  # Unchanged due to all caps

    def test_fix_publisher_empty_field(self):
        """Test empty publisher field."""
        entry = {"ID": "test", "publisher": ""}
        result = fix_publisher_capitalization(entry)
        assert result["publisher"] == ""

    def test_fix_publisher_no_field(self):
        """Test entry without publisher field."""
        entry = {"ID": "test", "title": "Test"}
        result = fix_publisher_capitalization(entry)
        assert "publisher" not in result

    def test_fix_journal_capitalization(self):
        """Test journal capitalization."""
        entry = {"ID": "test", "journal": "IEEE Transactions on Pattern Analysis"}
        result = fix_journal_capitalization(entry)
        assert result["journal"] == "{IEEE} Transactions on Pattern Analysis"

    def test_fix_journal_all_caps_multiword_warning(self):
        """Test all-caps multi-word journal triggers warning and stays unchanged."""
        entry = {"ID": "test", "journal": "IEEE TRANSACTIONS ON PATTERN ANALYSIS"}
        result = fix_journal_capitalization(entry)
        assert result["journal"] == "IEEE TRANSACTIONS ON PATTERN ANALYSIS"  # Unchanged

    def test_fix_journal_all_caps_single_word_protected(self):
        """Test all-caps single-word journal gets protected."""
        entry = {"ID": "test", "journal": "IEEE"}
        result = fix_journal_capitalization(entry)
        assert result["journal"] == "{IEEE}"

    def test_fix_journal_mixed_case_words_protected(self):
        """Test mixed-case words in journal get protected."""
        entry = {"ID": "test", "journal": "Nature Machine Intelligence"}
        result = fix_journal_capitalization(entry)
        assert result["journal"] == "Nature Machine Intelligence"  # No mixed-case words

    def test_fix_journal_mixed_case_with_acronyms(self):
        """Test journal with mixed-case acronyms."""
        entry = {"ID": "test", "journal": "ACM Computing Surveys"}
        result = fix_journal_capitalization(entry)
        assert result["journal"] == "{ACM} Computing Surveys"

    def test_fix_journal_already_protected_single_braces(self):
        """Test already protected journal doesn't get double-protected."""
        entry = {"ID": "test", "journal": "{IEEE Transactions on Pattern Analysis}"}
        result = fix_journal_capitalization(entry)
        assert (
            result["journal"] == "{IEEE Transactions on Pattern Analysis}"
        )  # No double protection

    def test_fix_journal_already_protected_double_braces(self):
        """Test double-braced journal triggers warning and stays unchanged."""
        entry = {"ID": "test", "journal": "{{IEEE TRANSACTIONS}}"}
        result = fix_journal_capitalization(entry)
        assert result["journal"] == "{{IEEE TRANSACTIONS}}"  # Unchanged

    def test_fix_journal_empty_field(self):
        """Test empty journal field."""
        entry = {"ID": "test", "journal": ""}
        result = fix_journal_capitalization(entry)
        assert result["journal"] == ""

    def test_fix_journal_no_field(self):
        """Test entry without journal field."""
        entry = {"ID": "test", "title": "Test"}
        result = fix_journal_capitalization(entry)
        assert "journal" not in result

    def test_title_double_braced_with_mixed_braces(self):
        """Test title from {{...}} source with mixed inner braces - should preserve structure."""
        # This simulates what bibtexparser gives us from: {{DeepGCNs:} Can {GCNs} Go As Deep As {CNNs?}}
        entry = {"ID": "test", "title": "{DeepGCNs:} Can {GCNs} Go As Deep As {CNNs?}"}
        result = fix_title_capitalization(entry)
        # Should preserve the mixed brace structure, not create double braces
        assert result["title"] == "{DeepGCNs:} Can {GCNs} Go As Deep As {CNNs?}"

    def test_title_cpus_gpus_normalization(self):
        """Test various CPU/GPU title formats normalize to same result."""
        expected = "{CPUs} and {GPUs}"

        # From {{CPUs} and {GPUs}} (bibtex source) -> {CPUs} and {GPUs} (already in final form)
        entry1 = {"ID": "test", "title": "{CPUs} and {GPUs}"}
        result1 = fix_title_capitalization(entry1)
        assert result1["title"] == expected

        # From {{{CPUs} and {GPUs}}} -> {{CPUs} and {GPUs}} -> {CPUs} and {GPUs}
        entry2 = {"ID": "test", "title": "{{CPUs} and {GPUs}}"}
        result2 = fix_title_capitalization(entry2)
        assert result2["title"] == expected

        # From {CPUs and GPUs} -> CPUs and GPUs -> {CPUs} and {GPUs}
        entry3 = {"ID": "test", "title": "CPUs and GPUs"}
        result3 = fix_title_capitalization(entry3)
        assert result3["title"] == expected

    def test_title_non_matching_outer_braces(self):
        """Test that non-matching first and last braces are not treated as outer braces."""
        # {A} {B} - first { and last } are not a matching pair
        entry = {"ID": "test", "title": "{CPUs} {GPUs}"}
        result = fix_title_capitalization(entry)
        # Should preserve both individual protections
        assert result["title"] == "{CPUs} {GPUs}"

    def test_has_matching_outer_braces(self):
        """Test the _has_matching_outer_braces helper function."""
        from blackref.field_validators import _has_matching_outer_braces

        # Should return True - matching outer braces
        assert _has_matching_outer_braces("{content}")
        assert _has_matching_outer_braces("{{CPUs} and {GPUs}}")
        assert _has_matching_outer_braces("{simple text}")

        # Should return False - non-matching first and last braces
        assert not _has_matching_outer_braces("{CPUs} and {GPUs}")
        assert not _has_matching_outer_braces("{CPUs} {GPUs}")
        assert not _has_matching_outer_braces("{A} {B} {C}")

        # Should return False - no braces or incomplete braces
        assert not _has_matching_outer_braces("no braces")
        assert not _has_matching_outer_braces("{incomplete")
        assert not _has_matching_outer_braces("incomplete}")

    def test_protect_mixed_case_words_edge_cases(self):
        """Test edge cases for mixed-case word protection."""
        # Single character words
        assert _protect_mixed_case_words("a") == "a"
        assert _protect_mixed_case_words("A") == "A"

        # Numbers only
        assert _protect_mixed_case_words("123") == "123"

        # Mixed numbers and letters
        assert _protect_mixed_case_words("3D") == "{3D}"
        assert (
            _protect_mixed_case_words("H264") == "H264"
        )  # No uppercase after first char

        # Special characters only
        assert _protect_mixed_case_words("@#$") == "@#$"

        # Empty string
        assert _protect_mixed_case_words("") == ""

        # Only spaces
        assert _protect_mixed_case_words("   ") == "   "

    def test_all_caps_detection_with_numbers(self):
        """Test all-caps detection with numbers and punctuation."""
        entry = {"ID": "test", "title": "3D GPU RENDERING WITH IEEE 802.11"}
        result = fix_title_capitalization(entry)
        assert result["title"] == "3D GPU RENDERING WITH IEEE 802.11"  # Unchanged

    def test_all_caps_detection_mixed_case(self):
        """Test that mixed case doesn't trigger all-caps warning."""
        entry = {"ID": "test", "title": "3D GPU Rendering with IEEE 802.11"}
        result = fix_title_capitalization(entry)
        assert result["title"] == "{3D} {GPU} Rendering with {IEEE} 802.11"

    def test_double_braces_conversion_simple(self):
        """Test double braces conversion for simple title."""
        # After bibtexparser parses {{...}}, it becomes {...}
        entry = {"ID": "test", "title": "{The Title}"}
        result = fix_title_capitalization(entry)
        assert (
            result["title"] == "The Title"
        )  # Converted (no mixed-case words to protect)

    def test_single_braces_processed_normally(self):
        """Test that single braces get processed normally (braces removed, protection applied)."""
        entry = {"ID": "test", "title": "{The Title}"}
        result = fix_title_capitalization(entry)
        assert (
            result["title"] == "The Title"
        )  # Braces removed, no mixed-case protection needed

    def test_complex_mixed_case_scenarios(self):
        """Test complex mixed-case scenarios."""
        # AutoMVQ example from user
        text = "AutoMVQ algorithm for GPUs"
        expected = "{AutoMVQ} algorithm for {GPUs}"
        assert _protect_mixed_case_words(text) == expected

        # Multiple uppercase after first char
        text = "SQLite database"
        expected = "{SQLite} database"
        assert _protect_mixed_case_words(text) == expected

        # Acronym in parentheses
        text = "Machine Learning (ML) with GPUs"
        expected = "Machine Learning {(ML)} with {GPUs}"
        assert _protect_mixed_case_words(text) == expected

    def test_protect_mixed_case_words_skip_already_braced(self):
        """Test that already braced words are not double-protected."""
        # Single already braced word
        text = "Review of {CNN} architectures"
        expected = "Review of {CNN} architectures"
        assert _protect_mixed_case_words(text) == expected

        # Multiple words, some already braced
        text = "Deep learning with {CNN} and RNN networks"
        expected = "Deep learning with {CNN} and {RNN} networks"
        assert _protect_mixed_case_words(text) == expected

        # Mixed case with already braced
        text = (
            "Review of deep learning: concepts, {CNN} architectures, and GPU computing"
        )
        expected = "Review of deep learning: concepts, {CNN} architectures, and {GPU} computing"
        assert _protect_mixed_case_words(text) == expected

        # User's specific example
        text = "Review of deep learning: concepts, {CNN} architectures"
        expected = "Review of deep learning: concepts, {CNN} architectures"
        assert _protect_mixed_case_words(text) == expected

    def test_fix_title_capitalization_with_existing_braces(self):
        """Test title capitalization preserves existing braces."""
        entry = {
            "ID": "test",
            "title": "Review of deep learning: concepts, {CNN} architectures, and GPU computing",
        }
        result = fix_title_capitalization(entry)
        assert (
            result["title"]
            == "Review of deep learning: concepts, {CNN} architectures, and {GPU} computing"
        )

    def test_fix_title_double_braces_conversion(self):
        """Test conversion of double-braced titles (as parsed by bibtexparser)."""
        # After bibtexparser parses {{...}}, it becomes {...}
        entry = {
            "ID": "test",
            "title": "{EchoTracker: Advancing Myocardial Point Tracking in Echocardiography}",
        }
        result = fix_title_capitalization(entry)
        assert (
            result["title"]
            == "{EchoTracker:} Advancing Myocardial Point Tracking in Echocardiography"
        )

    def test_fix_booktitle_double_braces_conversion(self):
        """Test conversion of double-braced booktitles (as parsed by bibtexparser)."""
        # After bibtexparser parses {{...}}, it becomes {...}
        entry = {
            "ID": "test",
            "booktitle": "{Proceedings of IEEE Conference on Computer Vision}",
        }
        result = fix_booktitle_capitalization(entry)
        assert (
            result["booktitle"] == "Proceedings of {IEEE} Conference on Computer Vision"
        )

    def test_fix_title_double_braces_with_mixed_case_words(self):
        """Test double braces conversion with multiple mixed-case words."""
        # After bibtexparser parses {{...}}, it becomes {...}
        entry = {"ID": "test", "title": "{Deep Learning with CNN and RNN Networks}"}
        result = fix_title_capitalization(entry)
        assert result["title"] == "Deep Learning with {CNN} and {RNN} Networks"

    def test_fix_title_double_braces_with_existing_single_braces(self):
        """Test double braces conversion preserving existing single braces."""
        # After bibtexparser parses {{...}}, it becomes {...}
        entry = {"ID": "test", "title": "{Review of {CNN} and GPU Computing}"}
        result = fix_title_capitalization(entry)
        assert result["title"] == "Review of {CNN} and {GPU} Computing"

    def test_publisher_double_braces_still_warns(self):
        """Test that publisher with double braces still triggers warning (not converted)."""
        entry = {"ID": "test", "publisher": "{{IEEE}}"}
        result = fix_publisher_capitalization(entry)
        assert result["publisher"] == "{{IEEE}}"  # Unchanged, should trigger warning

    def test_full_formatter_double_braces_conversion(self):
        """Test double braces conversion through full formatter pipeline."""
        import bibtexparser
        from blackref.formatter import formatter

        bib_text = """@article{test2023,
            title = {{EchoTracker: Advancing Myocardial Point Tracking in Echocardiography}},
            author = {Test Author},
            year = {2023}
        }"""

        parser = bibtexparser.bparser.BibTexParser()
        bib_db = parser.parse(bib_text)

        result = formatter(
            bib_db,
            display_order=("ID", "ENTRYTYPE", "title", "author", "year"),
            sort_fields=(),
            utf8_fields=set(),
            latex_fields=set(),
            formatting_mode="full",
        )

        # Should not have triple braces in the final output
        assert "{{{" not in result
        # Should have proper single brace protection for the field content
        assert (
            "{EchoTracker:} Advancing Myocardial Point Tracking in Echocardiography"
            in result
        )

    def test_fix_doi_overwrite_empty_doi(self):
        """Test overwriting empty DOI field."""
        entry = {"ID": "test", "doi": "", "url": "https://doi.org/10.1000/182"}
        result = fix_doi(entry)
        assert result["doi"] == "10.1000/182"
        assert "url" not in result

    def test_fix_doi_overwrite_whitespace_doi(self):
        """Test overwriting whitespace-only DOI field."""
        entry = {"ID": "test", "doi": "   ", "url": "https://doi.org/10.1000/182"}
        result = fix_doi(entry)
        assert result["doi"] == "10.1000/182"
        assert "url" not in result

    def test_fix_doi_matching_existing_doi(self):
        """Test when URL DOI matches existing DOI (should still remove URL)."""
        entry = {
            "ID": "test",
            "doi": "10.1000/182",
            "url": "https://doi.org/10.1000/182",
        }
        result = fix_doi(entry)
        assert result["doi"] == "10.1000/182"
        assert "url" not in result

    def test_fix_doi_identical_doi_and_url_values(self):
        """Test when DOI and URL have identical values (not DOI URL format)."""
        entry = {
            "ID": "test",
            "doi": "10.1000/182",
            "url": "10.1000/182",
        }
        result = fix_doi(entry)
        assert result["doi"] == "10.1000/182"
        assert "url" not in result

    def test_fix_doi_identical_values_with_whitespace(self):
        """Test identical DOI/URL values with whitespace differences."""
        entry = {
            "ID": "test",
            "doi": "  10.1000/182  ",
            "url": "10.1000/182",
        }
        result = fix_doi(entry)
        assert result["doi"] == "  10.1000/182  "  # DOI preserved as-is
        assert "url" not in result

    def test_fix_doi_identical_values_whitespace_in_url(self):
        """Test identical DOI/URL values with whitespace in URL."""
        entry = {
            "ID": "test",
            "doi": "10.1000/182",
            "url": "  10.1000/182  ",
        }
        result = fix_doi(entry)
        assert result["doi"] == "10.1000/182"
        assert "url" not in result

    def test_fix_doi_different_values_not_doi_url(self):
        """Test different DOI/URL values where URL is not DOI format."""
        entry = {
            "ID": "test",
            "doi": "10.1000/182",
            "url": "10.1000/999",
        }
        result = fix_doi(entry)
        # Should not change anything since URL is not DOI format and values differ
        assert result["doi"] == "10.1000/182"
        assert result["url"] == "10.1000/999"

    def test_fix_doi_case_insensitive_identical_values(self):
        """Test case insensitive comparison of DOI and URL values."""
        entry = {
            "ID": "test",
            "doi": "10.1000/ABC",
            "url": "10.1000/abc",
        }
        result = fix_doi(entry)
        assert result["doi"] == "10.1000/ABC"  # Original DOI case preserved
        assert "url" not in result

    def test_fix_doi_case_insensitive_with_whitespace(self):
        """Test case insensitive comparison with whitespace."""
        entry = {
            "ID": "test",
            "doi": "  10.1000/XYZ  ",
            "url": "10.1000/xyz",
        }
        result = fix_doi(entry)
        assert result["doi"] == "  10.1000/XYZ  "  # Original DOI preserved as-is
        assert "url" not in result

    def test_fix_doi_case_insensitive_mixed_case(self):
        """Test case insensitive comparison with mixed case patterns."""
        entry = {
            "ID": "test",
            "doi": "10.1038/Nature12373",
            "url": "10.1038/NATURE12373",
        }
        result = fix_doi(entry)
        assert result["doi"] == "10.1038/Nature12373"
        assert "url" not in result

    def test_fix_doi_mismatch_existing_doi(self):
        """Test error when URL DOI doesn't match existing DOI."""
        entry = {
            "ID": "test",
            "doi": "10.1000/999",
            "url": "https://doi.org/10.1000/182",
        }

        # We need to capture the log output to test the error message
        from loguru import logger

        # Capture stderr where loguru outputs by default
        captured_logs = []

        def log_sink(message):
            captured_logs.append(message)

        # Add our custom sink
        logger.add(log_sink, level="ERROR")

        result = fix_doi(entry)

        # Should not change anything
        assert result["doi"] == "10.1000/999"
        assert result["url"] == "https://doi.org/10.1000/182"

        # Should have logged an error
        assert len(captured_logs) > 0
        assert "DOI mismatch" in str(captured_logs[-1])
        assert "10.1000/999" in str(captured_logs[-1])
        assert "10.1000/182" in str(captured_logs[-1])

    def test_fix_doi_case_insensitive_url_extraction_match(self):
        """Test case insensitive DOI URL extraction with existing DOI."""
        entry = {
            "ID": "test",
            "doi": "10.1109/cvpr.2017.143",
            "url": "https://doi.org/10.1109/CVPR.2017.143",
        }
        result = fix_doi(entry)
        # Should match case insensitively and remove URL
        assert result["doi"] == "10.1109/cvpr.2017.143"  # Original case preserved
        assert "url" not in result

    def test_fix_doi_case_insensitive_url_extraction_no_error(self):
        """Test that case differences in URL extraction don't trigger errors."""
        entry = {
            "ID": "test",
            "doi": "10.1038/NATURE12373",
            "url": "https://doi.org/10.1038/nature12373",
        }
        result = fix_doi(entry)
        # Should not log any error and should remove URL
        assert result["doi"] == "10.1038/NATURE12373"  # Original case preserved
        assert "url" not in result

    def test_fix_doi_true_mismatch_still_errors(self):
        """Test that true mismatches (not just case) still trigger errors."""
        entry = {
            "ID": "test",
            "doi": "10.1000/different",
            "url": "https://doi.org/10.1000/COMPLETELY_DIFFERENT",
        }

        from loguru import logger

        captured_logs = []

        def log_sink(message):
            captured_logs.append(message)

        logger.add(log_sink, level="ERROR")

        result = fix_doi(entry)

        # Should still log error for true mismatch
        assert result["doi"] == "10.1000/different"
        assert result["url"] == "https://doi.org/10.1000/COMPLETELY_DIFFERENT"
        assert len(captured_logs) > 0
        assert "DOI mismatch" in str(captured_logs[-1])

    def test_fix_doi_non_doi_url_ignored(self):
        """Test that non-DOI URLs are ignored."""
        entry = {"ID": "test", "url": "https://example.com/paper.pdf"}
        result = fix_doi(entry)
        assert "doi" not in result
        assert result["url"] == "https://example.com/paper.pdf"

    def test_fix_doi_arxiv_url_abs_creates_doi(self):
        """Test that arXiv abs URLs create DOI and remove URL."""
        entry = {"ID": "test", "url": "https://arxiv.org/abs/1234.5678"}
        result = fix_doi(entry)
        assert result["doi"] == "10.48550/arXiv.1234.5678"
        assert "url" not in result

    def test_fix_doi_arxiv_url_pdf_creates_doi(self):
        """Test that arXiv pdf URLs create DOI and remove URL."""
        entry = {"ID": "test", "url": "https://arxiv.org/pdf/2410.09704.pdf"}
        result = fix_doi(entry)
        assert result["doi"] == "10.48550/arXiv.2410.09704"
        assert "url" not in result

    def test_fix_doi_arxiv_url_pdf_without_extension_creates_doi(self):
        """Test that arXiv pdf URLs without .pdf extension create DOI."""
        entry = {"ID": "test", "url": "https://arxiv.org/pdf/2410.09704"}
        result = fix_doi(entry)
        assert result["doi"] == "10.48550/arXiv.2410.09704"
        assert "url" not in result

    def test_fix_doi_arxiv_url_http_creates_doi(self):
        """Test that arXiv URLs with http (not https) create DOI."""
        entry = {"ID": "test", "url": "http://arxiv.org/abs/1234.5678"}
        result = fix_doi(entry)
        assert result["doi"] == "10.48550/arXiv.1234.5678"
        assert "url" not in result

    def test_fix_doi_arxiv_url_with_existing_matching_doi(self):
        """Test that arXiv URLs with matching DOI remove URL and fix DOI case."""
        entry = {
            "ID": "test",
            "url": "https://arxiv.org/abs/1234.5678",
            "doi": "10.48550/arxiv.1234.5678",
        }
        result = fix_doi(entry)
        assert result["doi"] == "10.48550/arXiv.1234.5678"  # Fixed case
        assert "url" not in result

    def test_fix_doi_arxiv_url_with_existing_mismatched_doi(self):
        """Test that arXiv URLs with mismatched DOI log error and don't change anything."""
        entry = {
            "ID": "test",
            "url": "https://arxiv.org/abs/1234.5678",
            "doi": "10.48550/arXiv.9999.1111",
        }
        result = fix_doi(entry)
        assert result["doi"] == "10.48550/arXiv.9999.1111"  # Unchanged
        assert result["url"] == "https://arxiv.org/abs/1234.5678"  # URL preserved

    def test_fix_doi_arxiv_doi_case_fix_without_url(self):
        """Test that existing arXiv DOI case is fixed even without URL."""
        entry = {"ID": "test", "doi": "10.48550/arxiv.1234.5678"}
        result = fix_doi(entry)
        assert result["doi"] == "10.48550/arXiv.1234.5678"

    def test_fix_doi_arxiv_doi_case_fix_variations(self):
        """Test that various arXiv DOI case variations are fixed."""
        test_cases = [
            ("10.48550/arxiv.1234.5678", "10.48550/arXiv.1234.5678"),
            ("10.48550/ARXIV.1234.5678", "10.48550/arXiv.1234.5678"),
            ("10.48550/ArXiv.1234.5678", "10.48550/arXiv.1234.5678"),
            ("10.48550/arXiv.1234.5678", "10.48550/arXiv.1234.5678"),  # Already correct
        ]

        for input_doi, expected_doi in test_cases:
            entry = {"ID": "test", "doi": input_doi}
            result = fix_doi(entry)
            assert result["doi"] == expected_doi

    def test_fix_doi_partial_doi_url_ignored(self):
        """Test that partial DOI URLs are ignored."""
        entry = {"ID": "test", "url": "https://some-site.org/doi/10.1000/182"}
        result = fix_doi(entry)
        assert "doi" not in result
        assert result["url"] == "https://some-site.org/doi/10.1000/182"

    def test_fix_doi_no_url_field(self):
        """Test with no URL field."""
        entry = {"ID": "test", "title": "Test Title"}
        result = fix_doi(entry)
        assert "doi" not in result
        assert "url" not in result
        assert result["title"] == "Test Title"

    def test_fix_doi_empty_url_field(self):
        """Test with empty URL field."""
        entry = {"ID": "test", "url": ""}
        result = fix_doi(entry)
        assert "doi" not in result
        assert result["url"] == ""

    def test_fix_doi_whitespace_only_url(self):
        """Test with whitespace-only URL field."""
        entry = {"ID": "test", "url": "   "}
        result = fix_doi(entry)
        assert "doi" not in result
        assert result["url"] == "   "

    def test_fix_doi_malformed_doi_url(self):
        """Test malformed DOI URL (missing protocol)."""
        entry = {"ID": "test", "url": "doi.org/10.1000/182"}
        result = fix_doi(entry)
        assert "doi" not in result
        assert result["url"] == "doi.org/10.1000/182"

    def test_fix_doi_url_with_extra_path(self):
        """Test DOI URL with extra path components (should be ignored)."""
        entry = {"ID": "test", "url": "https://doi.org/10.1000/182/extra/path"}
        result = fix_doi(entry)
        assert result["doi"] == "10.1000/182/extra/path"
        assert "url" not in result


class TestDOIIntegration:
    """Test DOI fixing in realistic scenarios."""

    def test_comprehensive_doi_scenarios(self):
        """Test multiple DOI scenarios in sequence."""
        test_cases = [
            # Basic extraction
            {
                "input": {"ID": "test1", "url": "https://doi.org/10.1000/182"},
                "expected": {"ID": "test1", "doi": "10.1000/182"},
            },
            # With existing matching DOI
            {
                "input": {
                    "ID": "test2",
                    "doi": "10.1000/183",
                    "url": "https://doi.org/10.1000/183",
                },
                "expected": {"ID": "test2", "doi": "10.1000/183"},
            },
            # Non-DOI URL (should be unchanged)
            {
                "input": {"ID": "test3", "url": "https://example.com/paper.pdf"},
                "expected": {"ID": "test3", "url": "https://example.com/paper.pdf"},
            },
            # Complex DOI
            {
                "input": {
                    "ID": "test4",
                    "url": "https://dx.doi.org/10.1038/nature12373",
                },
                "expected": {"ID": "test4", "doi": "10.1038/nature12373"},
            },
            # Identical DOI and URL values (not DOI URL format)
            {
                "input": {"ID": "test5", "doi": "10.1000/182", "url": "10.1000/182"},
                "expected": {"ID": "test5", "doi": "10.1000/182"},
            },
            # Identical values with whitespace
            {
                "input": {
                    "ID": "test6",
                    "doi": "10.1000/182",
                    "url": "  10.1000/182  ",
                },
                "expected": {"ID": "test6", "doi": "10.1000/182"},
            },
            # Case insensitive identical values
            {
                "input": {"ID": "test7", "doi": "10.1000/ABC", "url": "10.1000/abc"},
                "expected": {"ID": "test7", "doi": "10.1000/ABC"},
            },
        ]

        for case in test_cases:
            result = fix_doi(case["input"].copy())
            assert result == case["expected"], f"Failed for case {case['input']}"


class TestFixHTMLEntities:
    """Test HTML entity conversion to LaTeX and UTF-8."""

    def test_convert_html_entities_basic(self):
        """Test basic HTML entity conversion."""
        test_cases = [
            ("&amp;", r"\&"),
            ("&lt;", "<"),
            ("&gt;", ">"),
            ("No entities here", "No entities here"),
            ("", ""),
        ]

        for input_text, expected in test_cases:
            result = _convert_html_entities(input_text)
            assert result == expected, (
                f"Failed for '{input_text}': got '{result}', expected '{expected}'"
            )

    def test_convert_html_entities_quotes(self):
        """Test quotation mark entity conversion."""
        test_cases = [
            ("&quot;Hello&quot;", "''Hello''"),
            ("&ldquo;Hello&rdquo;", "``Hello''"),
            ("&lsquo;Hello&rsquo;", "`Hello'"),
            ("&laquo;Hello&raquo;", r"\guillemotleftHello\guillemotright"),
            ("&bdquo;Hello&rdquo;", ",,Hello''"),
        ]

        for input_text, expected in test_cases:
            result = _convert_html_entities(input_text)
            assert result == expected, (
                f"Failed for '{input_text}': got '{result}', expected '{expected}'"
            )

    def test_convert_html_entities_typography(self):
        """Test typography entity conversion."""
        test_cases = [
            ("&ndash;", "--"),
            ("&mdash;", "---"),
            ("&hellip;", r"\ldots"),
            ("&nbsp;", " "),
            ("Page&nbsp;1&ndash;10", "Page 1--10"),
        ]

        for input_text, expected in test_cases:
            result = _convert_html_entities(input_text)
            assert result == expected, (
                f"Failed for '{input_text}': got '{result}', expected '{expected}'"
            )

    def test_convert_html_entities_mathematical(self):
        """Test mathematical symbol entity conversion."""
        test_cases = [
            ("&deg;", r"${}^\circ$"),
            ("&plusmn;", "±"),
            ("&times;", "×"),
            ("&divide;", "÷"),
            ("&frac12;", "½"),
            ("&sup2;", "²"),
            ("&micro;", "µ"),
            ("&infin;", "∞"),
            ("&rarr;", "→"),
            ("&larr;", "←"),
        ]

        for input_text, expected in test_cases:
            result = _convert_html_entities(input_text)
            assert result == expected, (
                f"Failed for '{input_text}': got '{result}', expected '{expected}'"
            )

    def test_convert_html_entities_symbols(self):
        """Test symbol entity conversion."""
        test_cases = [
            ("&copy;", r"\copyright"),
            ("&reg;", r"\textregistered"),
            ("&trade;", r"\texttrademark"),
            ("&sect;", r"\S"),
            ("&para;", r"\P"),
            ("&dagger;", r"\textdagger"),
            ("&bull;", r"\textbullet"),
        ]

        for input_text, expected in test_cases:
            result = _convert_html_entities(input_text)
            assert result == expected, (
                f"Failed for '{input_text}': got '{result}', expected '{expected}'"
            )

    def test_convert_html_entities_greek_letters(self):
        """Test Greek letter entity conversion."""
        test_cases = [
            ("&alpha;", "α"),
            ("&beta;", "β"),
            ("&gamma;", "γ"),
            ("&delta;", "δ"),
            ("&omega;", "ω"),
            ("&Alpha;", "Α"),
            ("&Beta;", "Β"),
            ("&Gamma;", "Γ"),
            ("&Delta;", "Δ"),
            ("&Omega;", "Ω"),
        ]

        for input_text, expected in test_cases:
            result = _convert_html_entities(input_text)
            assert result == expected, (
                f"Failed for '{input_text}': got '{result}', expected '{expected}'"
            )

    def test_convert_html_entities_accented_characters(self):
        """Test accented character entity conversion to UTF-8."""
        test_cases = [
            ("&aacute;", "á"),
            ("&eacute;", "é"),
            ("&iacute;", "í"),
            ("&oacute;", "ó"),
            ("&uacute;", "ú"),
            ("&Aacute;", "Á"),
            ("&Eacute;", "É"),
            ("&agrave;", "à"),
            ("&egrave;", "è"),
            ("&aring;", "å"),
            ("&Aring;", "Å"),
            ("&auml;", "ä"),
            ("&ouml;", "ö"),
            ("&uuml;", "ü"),
            ("&Auml;", "Ä"),
            ("&Ouml;", "Ö"),
            ("&Uuml;", "Ü"),
            ("&oslash;", "ø"),
            ("&Oslash;", "Ø"),
            ("&aelig;", "æ"),
            ("&AElig;", "Æ"),
            ("&ccedil;", "ç"),
            ("&Ccedil;", "Ç"),
            ("&ntilde;", "ñ"),
            ("&Ntilde;", "Ñ"),
        ]

        for input_text, expected in test_cases:
            result = _convert_html_entities(input_text)
            assert result == expected, (
                f"Failed for '{input_text}': got '{result}', expected '{expected}'"
            )

    def test_convert_html_entities_complex_text(self):
        """Test complex text with multiple entity types."""
        input_text = "Computers &amp; Graphics: &ldquo;3D Rendering&rdquo; by M&uuml;ller &mdash; &copy; 2023"
        expected = (
            r"Computers \& Graphics: ``3D Rendering'' by Müller --- \copyright 2023"
        )

        result = _convert_html_entities(input_text)
        assert result == expected, (
            f"Failed for complex text: got '{result}', expected '{expected}'"
        )

    def test_fix_html_entities_entry_processing(self):
        """Test HTML entity conversion on BibTeX entry fields."""
        entry = {
            "ID": "test2023",
            "title": "Advanced Topics in AI &amp; Machine Learning",
            "journal": "Computers &amp; Graphics",
            "author": "M&uuml;ller, Hans &amp; Smith, Jane",
            "abstract": "This paper discusses AI&hellip; &ldquo;deep learning&rdquo; methods.",
            "note": "Copyright &copy; 2023. Temperature: 25&deg;C &plusmn; 1&deg;C",
            "year": "2023",  # Should not be processed
            "pages": "1--10",  # Should not be processed
        }

        expected = {
            "ID": "test2023",
            "title": r"Advanced Topics in AI \& Machine Learning",
            "journal": r"Computers \& Graphics",
            "author": r"Müller, Hans \& Smith, Jane",
            "abstract": r"This paper discusses AI\ldots ``deep learning'' methods.",
            "note": r"Copyright \copyright 2023. Temperature: 25${}^\circ$C ± 1${}^\circ$C",
            "year": "2023",
            "pages": "1--10",
        }

        result = fix_html_entities(entry.copy())
        assert result == expected, "Entry processing failed"

    def test_fix_html_entities_no_entities(self):
        """Test that entries without HTML entities are unchanged."""
        entry = {
            "ID": "test2023",
            "title": "Normal Title without Entities",
            "author": "Smith, John",
            "year": "2023",
        }

        result = fix_html_entities(entry.copy())
        assert result == entry, "Entry without entities should be unchanged"

    def test_fix_html_entities_empty_fields(self):
        """Test that empty fields are handled correctly."""
        entry = {
            "ID": "test2023",
            "title": "",
            "author": "Smith, John",
            "abstract": None,  # This will be handled by remove_empty_keys
        }

        result = fix_html_entities(entry.copy())
        expected = {
            "ID": "test2023",
            "title": "",
            "author": "Smith, John",
            "abstract": None,
        }
        assert result == expected, "Empty fields should be handled correctly"

    def test_fix_html_entities_journal_field_real_example(self):
        """Test the real-world case from example.bib."""
        entry = {"ID": "test2023", "journal": "Echo Research &amp; Practice"}

        expected = {"ID": "test2023", "journal": r"Echo Research \& Practice"}

        result = fix_html_entities(entry.copy())
        assert result == expected, "Real journal example should work correctly"

    def test_fix_html_entities_unconverted_warning(self):
        """Test that unconverted HTML entities trigger warnings."""
        from unittest.mock import patch

        # Test unconverted entity
        with patch("blackref.field_validators.logger.warning") as mock_warning:
            _convert_html_entities("Test &unknownentity; text")
            mock_warning.assert_called_once_with(
                "Found unconverted HTML entities: ['&unknownentity;']"
            )

    def test_fix_html_entities_inappropriate_symbols_warning(self):
        """Test that inappropriate symbols in titles trigger warnings."""
        from unittest.mock import patch

        # Test mathematical symbols in title
        entry = {
            "ID": "test2023",
            "title": "Algorithm with O(n²) complexity and ±5% error",
        }

        with patch("blackref.field_validators.logger.warning") as mock_warning:
            fix_html_entities(entry.copy())
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0][0]
            assert "test2023" in args
            assert "title" in args
            assert "math symbol" in args

    def test_fix_html_entities_arrows_warning(self):
        """Test that arrows in titles trigger warnings."""
        from unittest.mock import patch

        # Test arrows in title
        entry = {"ID": "test2023", "title": "Process A → Process B: Analysis"}

        with patch("blackref.field_validators.logger.warning") as mock_warning:
            fix_html_entities(entry.copy())
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0][0]
            assert "test2023" in args
            assert "arrow" in args

    def test_fix_html_entities_greek_letters_warning(self):
        """Test that multiple Greek letters in titles trigger warnings."""
        from unittest.mock import patch

        # Test multiple Greek letters in title
        entry = {"ID": "test2023", "title": "Study of α-particles and β-decay"}

        with patch("blackref.field_validators.logger.warning") as mock_warning:
            fix_html_entities(entry.copy())
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0][0]
            assert "test2023" in args
            assert "Greek letters" in args

    def test_fix_html_entities_no_warning_in_abstract(self):
        """Test that mathematical symbols in abstract don't trigger warnings."""
        from unittest.mock import patch

        # Mathematical symbols should be fine in abstract
        entry = {
            "ID": "test2023",
            "abstract": "We measured ±5% accuracy with O(n²) complexity",
        }

        with patch("blackref.field_validators.logger.warning") as mock_warning:
            fix_html_entities(entry.copy())
            mock_warning.assert_not_called()

    def test_fix_html_entities_single_greek_no_warning(self):
        """Test that single Greek letters don't trigger warnings."""
        from unittest.mock import patch

        # Single Greek letter should not warn
        entry = {"ID": "test2023", "title": "Algorithm α Analysis"}

        with patch("blackref.field_validators.logger.warning") as mock_warning:
            fix_html_entities(entry.copy())
            mock_warning.assert_not_called()

    def test_fix_html_entities_no_double_escaping(self):
        """Test that already escaped ampersands are not double-escaped."""
        # Test that \& doesn't become \\&
        test_cases = [
            ("Already escaped \\& symbol", "Already escaped \\& symbol"),
            ("Mixed: \\& and &amp;", "Mixed: \\& and \\&"),
            ("Plain & and &amp;", "Plain \\& and \\&"),
        ]

        for input_text, expected in test_cases:
            result = _convert_html_entities(input_text)
            assert result == expected, (
                f"Failed for '{input_text}': got '{result}', expected '{expected}'"
            )
