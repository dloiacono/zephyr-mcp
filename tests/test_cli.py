"""Tests for zephyr_mcp CLI entry point."""

import logging
from unittest.mock import MagicMock, patch

from zephyr_mcp import main


class TestMain:
    @patch("zephyr_mcp._cli")
    def test_main_calls_cli(self, mock_cli):
        mock_cli.standalone_mode = False
        main()
        mock_cli.assert_called_once()


class TestCliCallback:
    """Test the _cli callback function by importing and calling it with mocked dependencies."""

    def _invoke(self, transport="stdio", port=8000, host="0.0.0.0", read_only=False, verbose=0):
        """Call the CLI callback with mocked server creation."""
        mock_server = MagicMock()
        with (
            patch("zephyr_mcp.server.create_server", return_value=mock_server) as mock_create,
            patch("logging.basicConfig") as mock_log_config,
        ):
            from zephyr_mcp import _cli

            _cli.callback(
                transport=transport,
                port=port,
                host=host,
                read_only=read_only,
                verbose=verbose,
            )
        return mock_server, mock_create, mock_log_config

    def test_stdio_transport(self):
        mock_server, mock_create, _ = self._invoke(transport="stdio")
        mock_create.assert_called_once_with(read_only=False)
        mock_server.run.assert_called_once_with(transport="stdio")

    def test_sse_transport(self):
        mock_server, mock_create, _ = self._invoke(transport="sse", port=9000, host="127.0.0.1")
        mock_create.assert_called_once_with(read_only=False)
        mock_server.run.assert_called_once_with(transport="sse", host="127.0.0.1", port=9000)

    def test_read_only_flag(self):
        _, mock_create, _ = self._invoke(read_only=True)
        mock_create.assert_called_once_with(read_only=True)

    def test_verbose_info(self):
        _, _, mock_log = self._invoke(verbose=1)
        assert mock_log.call_args[1]["level"] == logging.INFO

    def test_verbose_debug(self):
        _, _, mock_log = self._invoke(verbose=2)
        assert mock_log.call_args[1]["level"] == logging.DEBUG

    def test_verbose_3_is_debug(self):
        _, _, mock_log = self._invoke(verbose=3)
        assert mock_log.call_args[1]["level"] == logging.DEBUG

    def test_default_verbose_is_warning(self):
        _, _, mock_log = self._invoke(verbose=0)
        assert mock_log.call_args[1]["level"] == logging.WARNING
