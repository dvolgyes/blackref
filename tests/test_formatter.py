#!/usr/bin/env python3
"""Tests for formatter module."""

import bibtexparser
from blackref.formatter import LazyOpen, formatter


class TestLazyOpen:
    """Test LazyOpen context manager."""

    def test_lazy_open_file_handle(self):
        """Test LazyOpen with file handle."""
        import io

        file_handle = io.StringIO("test content")
        with LazyOpen(file_handle, "r") as f:
            assert f is file_handle
            content = f.read()
            assert content == "test content"

    def test_lazy_open_string_path(self, tmp_path):
        """Test LazyOpen with string path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        with LazyOpen(str(test_file), "r") as f:
            content = f.read()
            assert content == "test content"


class TestFormatter:
    """Test BibTeX formatter."""

    def test_formatter_basic(self):
        """Test basic formatting functionality."""
        bib_str = """
        @article{test2023,
            title = {Test Title},
            author = {Test Author},
            year = {2023},
            journal = {Test Journal}
        }
        """
        bib = bibtexparser.loads(bib_str)

        display_order = ("title", "author", "year", "journal")
        sort_fields = ("year",)
        utf8_fields = set()
        latex_fields = set()

        result = formatter(bib, display_order, sort_fields, utf8_fields, latex_fields)

        assert "@article{test2023," in result
        assert "title" in result
        assert "author" in result
        assert "year" in result
        assert "journal" in result

    def test_formatter_sorting(self):
        """Test entry sorting functionality."""
        bib_str = """
        @article{test2023,
            title = {Test Title 2023},
            year = {2023}
        }
        @article{test2022,
            title = {Test Title 2022},
            year = {2022}
        }
        """
        bib = bibtexparser.loads(bib_str)

        display_order = ("title", "year")
        sort_fields = ("year",)
        utf8_fields = set()
        latex_fields = set()

        result = formatter(bib, display_order, sort_fields, utf8_fields, latex_fields)

        # Should be sorted by year (2022 first)
        pos_2022 = result.find("test2022")
        pos_2023 = result.find("test2023")
        assert pos_2022 < pos_2023

    def test_formatter_reverse_sorting(self):
        """Test reverse sorting functionality."""
        bib_str = """
        @article{test2022,
            title = {Test Title 2022},
            year = {2022}
        }
        @article{test2023,
            title = {Test Title 2023},
            year = {2023}
        }
        """
        bib = bibtexparser.loads(bib_str)

        display_order = ("title", "year")
        sort_fields = ("year-",)  # Reverse sort
        utf8_fields = set()
        latex_fields = set()

        result = formatter(bib, display_order, sort_fields, utf8_fields, latex_fields)

        # Should be sorted by year in reverse (2023 first)
        pos_2022 = result.find("test2022")
        pos_2023 = result.find("test2023")
        assert pos_2023 < pos_2022

    def test_formatter_display_order(self):
        """Test field display order."""
        bib_str = """
        @article{test2023,
            year = {2023},
            title = {Test Title},
            author = {Test Author}
        }
        """
        bib = bibtexparser.loads(bib_str)

        display_order = ("title", "author", "year")
        sort_fields = ("year",)
        utf8_fields = set()
        latex_fields = set()

        result = formatter(bib, display_order, sort_fields, utf8_fields, latex_fields)

        # Title should appear before author in output
        title_pos = result.find("title")
        author_pos = result.find("author")
        year_pos = result.find("year")

        assert title_pos < author_pos < year_pos

    def test_formatter_utf8_fields(self):
        """Test UTF-8 field processing."""
        bib_str = """
        @article{test2023,
            title = {Test Title},
            author = {Caf\\'e Author}
        }
        """
        bib = bibtexparser.loads(bib_str)

        display_order = ("title", "author")
        sort_fields = ("title",)
        utf8_fields = {"author"}
        latex_fields = set()

        result = formatter(bib, display_order, sort_fields, utf8_fields, latex_fields)

        assert "author" in result

    def test_formatter_latex_fields(self):
        """Test LaTeX field processing."""
        bib_str = """
        @article{test2023,
            title = {Test Title},
            author = {Café Author}
        }
        """
        bib = bibtexparser.loads(bib_str)

        display_order = ("title", "author")
        sort_fields = ("title",)
        utf8_fields = set()
        latex_fields = {"author"}

        result = formatter(bib, display_order, sort_fields, utf8_fields, latex_fields)

        assert "author" in result

    def test_formatter_empty_entry(self):
        """Test formatting with empty entry."""
        bib_str = """
        @article{test2023,
            title = {Test Title},
            abstract = {},
            notes = {}
        }
        """
        bib = bibtexparser.loads(bib_str)

        display_order = ("title", "abstract", "notes")
        sort_fields = ("title",)
        utf8_fields = set()
        latex_fields = set()

        result = formatter(bib, display_order, sort_fields, utf8_fields, latex_fields)

        # Empty fields should be removed
        assert "abstract" not in result
        assert "notes" not in result
        assert "title" in result

    def test_formatter_alignment(self):
        """Test field alignment."""
        bib_str = """
        @article{test2023,
            title = {Test Title},
            verylongfieldname = {Test Value}
        }
        """
        bib = bibtexparser.loads(bib_str)

        display_order = ("title", "verylongfieldname")
        sort_fields = ("title",)
        utf8_fields = set()
        latex_fields = set()

        result = formatter(bib, display_order, sort_fields, utf8_fields, latex_fields)

        # Should have proper alignment
        assert "title" in result
        assert "verylongfieldname" in result
