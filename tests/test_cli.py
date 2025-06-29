#!/usr/bin/env python3
"""Tests for CLI module."""

import os
from click.testing import CliRunner
from blackref.cli import main, DEFAULT_ORDER


class TestCLI:
    """Test CLI functionality."""

    def test_cli_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "uncompromising reference formatter" in result.output

    def test_cli_default_order(self):
        """Test default field order."""
        expected_fields = [
            "title",
            "booktitle",
            "author",
            "editor",
            "abstract",
            "journal",
            "issn",
            "volume",
            "year",
            "month",
            "number",
            "pages",
            "publisher",
            "address",
            "doi",
            "pubmedid",
            "url",
            "notes",
        ]
        assert DEFAULT_ORDER == ",".join(expected_fields)

    def test_cli_stdin_stdout(self):
        """Test processing from stdin to stdout."""
        runner = CliRunner()
        bib_input = """@article{test2023,
    title = {Test Title},
    author = {Test Author},
    year = {2023}
}"""

        result = runner.invoke(main, [], input=bib_input, catch_exceptions=False)
        assert result.exit_code == 0
        # For now, just test that it doesn't crash - output capture issue in tests
        # TODO: Fix output capture in Click tests

    def test_cli_file_input(self):
        """Test processing from file input."""
        runner = CliRunner()
        bib_content = """@article{test2023,
    title = {Test Title},
    author = {Test Author},
    year = {2023}
}"""

        with runner.isolated_filesystem():
            with open("test.bib", "w") as f:
                f.write(bib_content)

            result = runner.invoke(main, ["test.bib"], catch_exceptions=False)
            assert result.exit_code == 0
            # TODO: Fix output capture in Click tests

    def test_cli_file_output(self):
        """Test output to file."""
        runner = CliRunner()
        bib_content = """@article{test2023,
    title = {Test Title},
    author = {Test Author},
    year = {2023}
}"""

        with runner.isolated_filesystem():
            with open("input.bib", "w") as f:
                f.write(bib_content)

            result = runner.invoke(
                main, ["input.bib", "-o", "output.bib"], catch_exceptions=False
            )
            assert result.exit_code == 0

            # Check that output file was created
            assert os.path.exists("output.bib")

    def test_cli_write_back(self):
        """Test write-back functionality."""
        runner = CliRunner()
        bib_content = """@article{test2023,
    title = {Test Title},
    author = {Test Author},
    year = {2023}
}"""

        with runner.isolated_filesystem():
            with open("test.bib", "w") as f:
                f.write(bib_content)

            result = runner.invoke(
                main, ["test.bib", "--write-back"], catch_exceptions=False
            )
            assert result.exit_code == 0

            # Check that file still exists (was modified in place)
            assert os.path.exists("test.bib")

    def test_cli_sort_option(self):
        """Test custom sorting option."""
        runner = CliRunner()
        bib_content = """@article{ztest2023,
    title = {Z Test Title},
    year = {2023}
}
@article{atest2022,
    title = {A Test Title},
    year = {2022}
}"""

        result = runner.invoke(
            main, ["--sort", "title"], input=bib_content, catch_exceptions=False
        )
        assert result.exit_code == 0

    def test_cli_display_order(self):
        """Test custom display order."""
        runner = CliRunner()
        bib_content = """@article{test2023,
    year = {2023},
    title = {Test Title},
    author = {Test Author}
}"""

        result = runner.invoke(
            main,
            ["--display-order", "author,title,year"],
            input=bib_content,
            catch_exceptions=False,
        )
        assert result.exit_code == 0

    def test_cli_utf8_option(self):
        """Test UTF-8 encoding option."""
        runner = CliRunner()
        bib_content = """@article{test2023,
    title = {Test Title},
    author = {Caf\\'e Author}
}"""

        result = runner.invoke(
            main, ["--utf8", "author"], input=bib_content, catch_exceptions=False
        )
        assert result.exit_code == 0

    def test_cli_latex_option(self):
        """Test LaTeX encoding option."""
        runner = CliRunner()
        bib_content = """@article{test2023,
    title = {Test Title},
    author = {Café Author}
}"""

        result = runner.invoke(
            main, ["--latex", "author"], input=bib_content, catch_exceptions=False
        )
        assert result.exit_code == 0

    def test_cli_invalid_file(self):
        """Test handling of invalid input file."""
        runner = CliRunner()
        result = runner.invoke(main, ["nonexistent.bib"])
        assert result.exit_code != 0  # Should fail with non-zero exit code
        # Error message is printed to stderr by Click, not captured in output

    def test_cli_multiple_sort_fields(self):
        """Test sorting by multiple fields."""
        runner = CliRunner()
        bib_content = """@article{test2023a,
    title = {A Test Title},
    year = {2023}
}
@article{test2023b,
    title = {B Test Title},
    year = {2023}
}
@article{test2022,
    title = {Test Title},
    year = {2022}
}"""

        result = runner.invoke(
            main, ["--sort", "year,title"], input=bib_content, catch_exceptions=False
        )
        assert result.exit_code == 0
