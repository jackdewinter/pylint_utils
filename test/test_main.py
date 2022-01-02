"""
Module to provide tests related to the basic parts of the scanner.
"""
import os
import runpy
import tempfile
from test.proxypylintutils import ProxyPyLintUtils
from test.utils import assert_if_strings_different


def test_dash_dash_version():
    """
    Test to make sure we get the correct response if 'version' is supplied.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["--version"]

    version_meta = runpy.run_path("./pylint_utils/version.py")
    semantic_version = version_meta["__version__"]

    expected_return_code = 0
    expected_output = """{version}
""".replace(
        "{version}", semantic_version
    )
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_with_no_parameters():
    """
    Test to make sure we get the simple information if no parameters are supplied.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = []

    expected_return_code = 2
    expected_output = ""
    expected_error = """usage: main.py [-h] [--verbose] [--version]
               [--log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
               [--log-file LOG_FILE] [--config CONFIG_FILE] [-s]
               [-r REPORT_FILE] [--list-files] [--recurse]
               [--ignore-path IGNORE_PATH]
               path [path ...]
main.py: error: the following arguments are required: path
    """

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_with_no_parameters_through_module():
    """
    Test to make sure we get the simple information if no parameters are supplied,
    but through the module interface.
    """

    # Arrange
    scanner = ProxyPyLintUtils(use_module=True)
    supplied_arguments = []

    expected_return_code = 2
    expected_output = ""
    expected_error = """usage: __main.py__ [-h] [--verbose] [--version]
                   [--log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
                   [--log-file LOG_FILE] [--config CONFIG_FILE] [-s]
                   [-r REPORT_FILE] [--list-files] [--recurse]
                   [--ignore-path IGNORE_PATH]
                   path [path ...]
__main.py__: error: the following arguments are required: path
    """

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_with_no_parameters_through_main():
    """
    Test to make sure we get the simple information if no parameters are supplied,
    but through the main interface.
    """

    # Arrange
    scanner = ProxyPyLintUtils(use_main=True)
    supplied_arguments = []

    expected_return_code = 2
    expected_output = ""
    expected_error = """usage: main.py [-h] [--verbose] [--version]
               [--log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
               [--log-file LOG_FILE] [--config CONFIG_FILE] [-s]
               [-r REPORT_FILE] [--list-files] [--recurse]
               [--ignore-path IGNORE_PATH]
               path [path ...]
main.py: error: the following arguments are required: path
    """

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_dash_dash_list_files():
    """
    Test to make sure we can do a simple listing of files
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["--list-files", "test/resources"]

    expected_return_code = 0
    expected_output = """test/resources/bad_file.py
test/resources/bad_suppression.py
test/resources/balanced_file.py
test/resources/balanced_file_disable_next.py
test/resources/balanced_file_double_disable.py
test/resources/balanced_file_no_suppression.py
test/resources/balanced_file_with_too_many_lines.py
test/resources/unbalanced_file_double_disable.py
test/resources/unbalanced_file_double_enable.py
test/resources/unbalanced_file_enable_without_disable.py
test/resources/unbalanced_file_no_disable.py
test/resources/unbalanced_file_no_enable.py
test/resources/yet_another_bad_file.py"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_balanced_file():
    """
    Test to make sure that if we scan a file that is properly suppressed, no issues.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["test/resources/balanced_file.py"]

    expected_return_code = 0
    expected_output = ""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_balanced_file_no_suppressions():
    """
    Test to make sure that if we scan that has pylint issues but has not been scanned
    yet by pylint, there are no issues as none have been reported yet.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["test/resources/balanced_file_no_suppression.py"]

    expected_return_code = 0
    expected_output = ""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_balanced_file_with_too_many_lines():
    """
    Test to make sure that scanning a file that is balanced except for the
    `too_many_lines` suppression is okay.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["test/resources/balanced_file_with_too_many_lines.py"]

    expected_return_code = 0
    expected_output = ""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_unbalanced_file_no_disable_but_enable():
    """
    Test to make sure that scanning a file that has an enable suppression but
    not a disable suppression is reported as an issue.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    file_path_to_scan = "test/resources/unbalanced_file_no_disable.py"
    supplied_arguments = [file_path_to_scan]

    expected_return_code = 1
    expected_output = """{path}(11): Pylint error 'too-many-arguments' was not disabled, so enable is ignored.

Scanned python files contained 1 PyLint suppression error(s).
""".replace(
        "{path}", file_path_to_scan
    )
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_unbalanced_file_double_disable():
    """
    Test to make sure that scanning a file that has multiple disable suppression
    is reported as an issue.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["test/resources/unbalanced_file_double_disable.py"]

    expected_return_code = 1
    expected_output = """test/resources/unbalanced_file_double_disable.py(12): Pylint error 'too-many-arguments' was already disabled.
test/resources/unbalanced_file_double_disable.py(15): Pylint error 'too-many-arguments' was disabled, but not re-enabled.

Scanned python files contained 2 PyLint suppression error(s).
"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_unbalanced_file_no_enable_but_disable():
    """
    Test to make sure that scanning a file that has a disable suppression but
    not an enable suppression is reported as an issue.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["test/resources/unbalanced_file_no_enable.py"]

    expected_return_code = 1
    expected_output = """test/resources/unbalanced_file_no_enable.py(13): Pylint error 'too-many-arguments' was disabled, but not re-enabled.

Scanned python files contained 1 PyLint suppression error(s).
"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_unbalanced_file_double_enable():
    """
    Test to make sure that scanning a file that has a double enable suppression
    is reported as an issue.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["test/resources/unbalanced_file_double_enable.py"]

    expected_return_code = 1
    expected_output = """test/resources/unbalanced_file_double_enable.py(16): Pylint error 'too-many-arguments' was not disabled, so enable is ignored.

Scanned python files contained 1 PyLint suppression error(s).
"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_unbalanced_file_enable_without_disable():
    """
    Test to make sure that scanning a file that has an enable suppression for something
    that was not disabled is reported as an issue.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["test/resources/unbalanced_file_enable_without_disable.py"]

    expected_return_code = 1
    expected_output = """test/resources/unbalanced_file_enable_without_disable.py(1): Pylint error 'too-many-arguments' was not disabled, so enable is ignored.

Scanned python files contained 1 PyLint suppression error(s).
"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_unbalanced_file_enable_without_disable_and_verbose():
    """
    Test to make sure that scanning a file that has an enable suppression for something
    that was not disabled is reported as an issue, with verbose enabled.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = [
        "--verbose",
        "test/resources/unbalanced_file_enable_without_disable.py",
    ]

    expected_return_code = 1
    expected_output = """Scanning file: test/resources/unbalanced_file_enable_without_disable.py
test/resources/unbalanced_file_enable_without_disable.py(1): Pylint error 'too-many-arguments' was not disabled, so enable is ignored.
  File contains 1 scan errors.

Scanned python files contained 1 PyLint suppression error(s).
"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_balanced_file_disable_next():
    """
    Test to make sure that scanning a file that has an enable suppression for something
    that was not disabled is reported as an issue.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["test/resources/balanced_file_disable_next.py"]

    expected_return_code = 0
    expected_output = """test/resources/balanced_file_disable_next.py(1): Pylint suppression string 'disable-next=' is not supported.
"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_bad_suppression():
    """
    Test to make sure that scanning a file that has a bad suppression directive
    is reported as an issue.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["test/resources/bad_suppression.py"]

    expected_return_code = 1
    expected_output = """test/resources/bad_suppression.py(1): Pylint suppression 'enable-next=too-many-arguments' is not understood.

Scanned python files contained 1 PyLint suppression error(s)."""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_double_suppressions():
    """
    Test to make sure that multiple suppressions of the same block can be specified
    together on one line (disable) or on separate lines (enable).
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["test/resources/balanced_file_double_disable.py"]

    expected_return_code = 0
    expected_output = ""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_balanced_file_and_report():
    """
    Test to make sure that we can generate a report if we have a balanced file.
    """

    # Arrange
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            report_file_name = temp_file.name

        scanner = ProxyPyLintUtils()
        supplied_arguments = [
            "--report",
            report_file_name,
            "test/resources/balanced_file.py",
        ]

        expected_return_code = 0
        expected_output = ""
        expected_error = ""

        expected_report = """{
    "disables-by-file": {
        "test/resources/balanced_file.py": {
            "too-many-arguments": 1
        }
    },
    "disables-by-name": {
        "too-many-arguments": 1
    }
}"""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )

        with open(report_file_name, encoding="utf-8") as file:
            file_data = file.read()

        assert_if_strings_different(expected_report, file_data)
    finally:
        if os.path.exists(report_file_name):
            os.remove(report_file_name)


def test_scan_balanced_file_and_report_with_write_failure():
    """
    Test to make sure that if we try and write a report file out and it fails,
    that we notify the user.
    """

    # Arrange
    with tempfile.TemporaryDirectory() as temp_directory:
        report_file_name = temp_directory

        scanner = ProxyPyLintUtils()
        supplied_arguments = [
            "--report",
            report_file_name,
            "test/resources/balanced_file.py",
        ]

        expected_return_code = 1
        expected_output = ""
        expected_error = """Unable to write to report file '{file}':
  Error: [Errno 13] Permission denied: '{file}'
""".replace(
            "{file}", report_file_name
        )

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )
