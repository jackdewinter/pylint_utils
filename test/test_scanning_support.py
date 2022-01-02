"""
Module to provide tests related to scanning for files to analyze.
"""
from test.proxypylintutils import ProxyPyLintUtils


def test_dash_dash_list_files_and_test_path():
    """
    Test to make sure we find all the files in the test directory if asked.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["--list-files", "test"]

    expected_return_code = 0
    expected_output = """test/__init__.py
test/proxypylintutils.py
test/pytest_execute.py
test/test_logging.py
test/test_main.py
test/test_one.py
test/test_scanning_support.py
test/utils.py"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_dash_dash_list_files_and_test_path_and_recurse():
    """
    Test to make sure we find all the files in the test directory and any
    lower directories if asked.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["--list-files", "--recurse", "test"]

    expected_return_code = 0
    expected_output = """test/__init__.py
test/proxypylintutils.py
test/pytest_execute.py
test/resources/bad_file.py
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
test/resources/yet_another_bad_file.py
test/test_logging.py
test/test_main.py
test/test_one.py
test/test_scanning_support.py
test/utils.py"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_dash_dash_list_files_and_resources_path():
    """
    Test to make sure we find all the files in the test/resources directory,
    and only that directory, if asked.
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


def test_dash_dash_list_files_and_resources_path_with_star():
    """
    Test to make sure we find all the files in the test/resources directory,
    if asked.  This form ignores any non-matching files without reporting
    any errors.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["--list-files", "test/resources/*"]

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


def test_dash_dash_list_files_and_resources_path_with_b_star():
    """
    Test to make sure we find all the files in the test/resources directory
    matching the glob pattern `b*`.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["--list-files", "test/resources/b*"]

    expected_return_code = 0
    expected_output = """test/resources/bad_file.py
test/resources/bad_suppression.py
test/resources/balanced_file.py
test/resources/balanced_file_disable_next.py
test/resources/balanced_file_double_disable.py
test/resources/balanced_file_no_suppression.py
test/resources/balanced_file_with_too_many_lines.py
"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_dash_dash_list_files_and_resources_path_with_r_star():
    """
    Test to make sure we find all the files in the test/resources directory
    matching the glob pattern `r*`.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["--list-files", "test/resources/r*"]

    expected_return_code = 1
    expected_output = ""
    expected_error = "No matching files found."

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_dash_dash_list_files_and_resources_path_with_z_star():
    """
    Test to make sure we find all the files in the test/resources directory
    matching the glob pattern `z*`.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["--list-files", "test/resources/z*"]

    expected_return_code = 1
    expected_output = ""
    expected_error = "Provided glob path 'test/resources/z*' did not match any files."

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_dash_dash_list_files_and_direct_good_path():
    """
    Test to make sure we find the bad_file.py file in the test/resources directory.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["--list-files", "test/resources/bad_file.py"]

    expected_return_code = 0
    expected_output = "test/resources/bad_file.py"
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_dash_dash_list_files_and_direct_bad_path_and_good_path():
    """
    Test to make sure we do not find the bad_file.py file in the test/resources
    directory, as we also ask for the `test/resources/readme.md` file which is not
    a valid file.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = [
        "--list-files",
        "test/resources/bad_file.py",
        "test/resources/readme.md",
    ]

    expected_return_code = 1
    expected_output = ""
    expected_error = (
        "Provided file path 'test/resources/readme.md' is not a valid file."
    )

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_dash_dash_list_files_and_invalid_path():
    """
    Test to make sure we do not find the bad path in the test/resources
    directory.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = [
        "--log-level",
        "DEBUG",
        "--list-files",
        "test/resources/not-a-valid-file-name.md",
    ]

    expected_return_code = 1
    expected_output = ""
    expected_error = (
        "Provided path 'test/resources/not-a-valid-file-name.md' does not exist."
    )

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_dash_dash_list_files_and_test_path_with_non_existant_ignore_path():
    """
    Test to make sure we find the files in the test directory, except for an
    ignored path that is not present.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = [
        "--list-files",
        "--recurse",
        "--ignore-path",
        "not-a-path",
        "test",
    ]

    expected_return_code = 0
    expected_output = """test/__init__.py
test/proxypylintutils.py
test/pytest_execute.py
test/resources/bad_file.py
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
test/resources/yet_another_bad_file.py
test/test_logging.py
test/test_main.py
test/test_one.py
test/test_scanning_support.py
test/utils.py"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_dash_dash_list_files_and_test_path_with_existant_and_specific_ignore_path():
    """
    Test to make sure we find the files in the test directory, except for an
    ignored path that matches a full path.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = [
        "--list-files",
        "--recurse",
        "--ignore-path",
        "test/utils.py",
        "test",
    ]

    expected_return_code = 0
    expected_output = """test/__init__.py
test/proxypylintutils.py
test/pytest_execute.py
test/resources/bad_file.py
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
test/resources/yet_another_bad_file.py
test/test_logging.py
test/test_main.py
test/test_one.py
test/test_scanning_support.py"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_dash_dash_list_files_and_test_path_with_existant_directory_path():
    """
    Test to make sure we find the files in the test directory, except for an
    ignored path that is a valid directory.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = [
        "--list-files",
        "--recurse",
        "--ignore-path",
        "test/resources",
        "test",
    ]

    expected_return_code = 0
    expected_output = """test/__init__.py
test/proxypylintutils.py
test/pytest_execute.py
test/test_logging.py
test/test_main.py
test/test_one.py
test/test_scanning_support.py
test/utils.py"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_dash_dash_list_files_and_test_path_with_existant_directory_path_and_specific_path():
    """
    Test to make sure we find the files in the test directory, except for an
    ignored path that is a valid directory and another that is a specific path.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = [
        "--list-files",
        "--recurse",
        "--ignore-path",
        "test/resources",
        "--ignore-path",
        "test/resources/bad_file.py",
        "test",
    ]

    expected_return_code = 0
    expected_output = """test/__init__.py
test/proxypylintutils.py
test/pytest_execute.py
test/test_logging.py
test/test_main.py
test/test_one.py
test/test_scanning_support.py
test/utils.py"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
