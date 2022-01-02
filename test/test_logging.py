"""
Module to provide tests related to the logging.
"""

import os
import tempfile
from test.proxypylintutils import ProxyPyLintUtils


def test_with_dash_dash_log_level_debug(caplog):
    """
    Test to make sure we get the right effect if the `--log-level` flag
    is set for debug.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = [
        "--log-level",
        "DEBUG",
        "scan",
    ]

    expected_return_code = 1
    expected_output = ""
    expected_error = "Provided path 'scan' does not exist."

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )

    # Info messages
    assert "Number of files found: " in caplog.text
    assert "Determining files to scan for path 'scan'." in caplog.text

    # Debug messages
    assert "Provided path 'scan' does not exist." in caplog.text


def test_with_dash_dash_log_level_info(caplog):
    """
    Test to make sure we get the right effect if the `--log-level` flag
    is set for info.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = [
        "--log-level",
        "INFO",
        "scan",
    ]

    expected_return_code = 1
    expected_output = ""
    expected_error = "Provided path 'scan' does not exist."

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )

    # Info messages
    assert "Number of files found: " in caplog.text
    assert "Determining files to scan for path 'scan'." in caplog.text

    # Debug messages
    assert "Provided path 'scan' does not exist." not in caplog.text


def test_with_dash_dash_log_level_invalid(caplog):
    """
    Test to make sure we get the right effect if the `--log-level` flag
    is set for an invalid log level.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = [
        "--log-level",
        "invalid",
        "scan",
        "test/resources/rules/md047/end_with_blank_line.md",
    ]

    expected_return_code = 2
    expected_output = ""
    expected_error = """usage: main.py [-h] [--verbose] [--version]
               [--log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
               [--log-file LOG_FILE] [--config CONFIG_FILE] [-s]
               [-r REPORT_FILE] [--list-files] [--recurse]
               [--ignore-path IGNORE_PATH]
               path [path ...]
main.py: error: argument --log-level: invalid __log_level_type value: 'invalid'
"""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )

    # Info messages
    assert "Number of scanned files found: " not in caplog.text
    assert (
        "Determining files to scan for path "
        + "'test/resources/rules/md047/end_with_blank_line.md'."
        not in caplog.text
    )

    # Debug messages
    assert (
        "Provided path 'test/resources/rules/md047/end_with_blank_line.md' "
        + "is a valid Markdown file. Adding."
        not in caplog.text
    )


def test_with_dash_dash_log_level_info_with_file():
    """
    Test to make sure we get the right effect if the `--log-level` flag
    is set for info with the results going to a file.
    """

    # Arrange
    temp_file = None
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        log_file_name = temp_file.name

    try:
        scanner = ProxyPyLintUtils()
        supplied_arguments = [
            "--log-level",
            "INFO",
            "--log-file",
            log_file_name,
            "scan",
        ]

        expected_return_code = 1
        expected_output = ""
        expected_error = "Provided path 'scan' does not exist."

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )

        with open(log_file_name, encoding="utf-8") as file:
            file_data = file.read().replace("\n", "")

        # Info messages
        assert "Number of files found: " in file_data, f">{file_data}<"
        assert "Determining files to scan for path 'scan'." in file_data

        # Debug messages
        assert (
            "Provided path 'test/resources/rules/md047/end_with_blank_line.md' "
            + "is a valid file. Adding."
            not in file_data
        )
    finally:
        if os.path.exists(log_file_name):
            os.remove(log_file_name)
