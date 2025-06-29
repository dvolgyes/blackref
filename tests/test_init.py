#!/usr/bin/env python3
"""Tests for __init__ module."""

import blackref


class TestInit:
    """Test module initialization."""

    def test_version_attribute(self):
        """Test that version attribute exists."""
        assert hasattr(blackref, "__version__")
        assert isinstance(blackref.__version__, str)

    def test_author_attribute(self):
        """Test that author attribute exists."""
        assert hasattr(blackref, "__author__")
        assert blackref.__author__ == "David Völgyes"

    def test_email_attribute(self):
        """Test that email attribute exists."""
        assert hasattr(blackref, "__email__")
        assert blackref.__email__ == "david.volgyes@ieee.org"

    def test_license_attribute(self):
        """Test that license attribute exists."""
        assert hasattr(blackref, "__license__")
        assert blackref.__license__ == "AGPLv3"

    def test_summary_attribute(self):
        """Test that summary attribute exists."""
        assert hasattr(blackref, "__summary__")
        assert "BibTeX" in blackref.__summary__

    def test_description_attribute(self):
        """Test that description attribute exists."""
        assert hasattr(blackref, "__description__")
        assert blackref.__description__ == blackref.__summary__

    def test_main_function_import(self):
        """Test that main function is imported."""
        assert hasattr(blackref, "main")
        assert callable(blackref.main)

    def test_all_exports(self):
        """Test that __all__ contains expected exports."""
        expected_exports = [
            "__version__",
            "__author__",
            "__email__",
            "__license__",
            "__summary__",
            "__description__",
            "main",
        ]
        assert hasattr(blackref, "__all__")
        for export in expected_exports:
            assert export in blackref.__all__
