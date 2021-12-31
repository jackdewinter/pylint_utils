"""
Module to provide tests related to the basic parts of the scanner.
"""
import runpy
from test.proxypylintutils import ProxyPyLintUtils


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
