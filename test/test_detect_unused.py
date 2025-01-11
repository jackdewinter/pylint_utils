"""
Module to provide test cases that test the verfication that pylint suppress messages
are still required.
"""

import os
import subprocess
import tempfile
import unittest
from test.patch_builtin_open import PatchBuiltinOpen
from test.proxypylintutils import ProxyPyLintUtils


def write_temporary_configuration(pylint_config_to_disable):
    """
    Write the configuration as a temporary file that is kept around.
    """
    configuration_text = f"[pylint]\ndisable = {pylint_config_to_disable}\n"
    try:
        with tempfile.NamedTemporaryFile("wt", delete=False) as outfile:
            outfile.write(configuration_text)
            return outfile.name
    except IOError as this_exception:
        raise AssertionError(
            f"Test configuration file was not written ({this_exception})."
        ) from this_exception


def test_scan_for_unused_original_not_clean():
    """
    Test to make sure that scanning a file that is not originally clean will result
    in an error right away.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    file_to_scan = "test/resources/balanced_file.py"
    supplied_arguments = [
        "--scan",
        file_to_scan,
    ]

    expected_return_code = 1
    expected_output = """Verifying {file} scans cleanly without modifications.
  Baseline PyLint scan found unsuppressed warnings: missing-module-docstring
  Fix all errors before scanning again.

No unused PyLint suppressions found.
""".replace(
        "{file}", file_to_scan
    )
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_with_multiple_unsuppressed_in_original():
    """
    Test to make sure that scanning a file that is not originally clean on multiple
    counts will result in an error right away.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    file_to_scan = "test/resources/yet_another_bad_file.py"
    supplied_arguments = [
        "--scan",
        file_to_scan,
    ]

    expected_return_code = 1
    expected_output = """Verifying {file} scans cleanly without modifications.
  Baseline PyLint scan found unsuppressed warnings: missing-function-docstring, missing-module-docstring, too-many-arguments, trailing-newlines
  Fix all errors before scanning again.

No unused PyLint suppressions found.
""".replace(
        "{file}", file_to_scan
    )
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_with_multiple_unsuppressed_in_original_with_config():
    """
    Test to make sure that scanning a file that is not originally clean on multiple
    counts will result in an error right away.
    """

    # Arrange
    warning_to_suppress = "missing-function-docstring, missing-module-docstring, too-many-arguments, trailing-newlines"
    configuration_file = None
    try:
        configuration_file = write_temporary_configuration(warning_to_suppress)
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/yet_another_bad_file.py"
        supplied_arguments = [
            "--config",
            configuration_file,
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 2
        expected_output = """Verifying {file} scans cleanly without modifications.

1 unused PyLint suppressions found.
{file}:5: Unused suppression: too-many-branches
""".replace(
            "{file}", file_to_scan
        )
        expected_error = ""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )
    finally:
        if configuration_file and os.path.exists(configuration_file):
            os.remove(configuration_file)


def test_scan_with_multiple_unsuppressed_in_original_with_bad_end_with_config():
    """
    Test to make sure that scanning a file that is not originally clean on multiple
    counts will result in an error right away.
    """

    # Arrange
    warning_to_suppress = (
        "missing-function-docstring, missing-module-docstring, "
        + "too-many-arguments, missing-final-newline"
    )
    configuration_file = None
    try:
        configuration_file = write_temporary_configuration(warning_to_suppress)
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/yet_another_bad_file_with_bad_end.py"
        supplied_arguments = [
            "--config",
            configuration_file,
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 2
        expected_output = """Verifying {file} scans cleanly without modifications.

1 unused PyLint suppressions found.
{file}:5: Unused suppression: too-many-branches
""".replace(
            "{file}", file_to_scan
        )
        expected_error = ""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )
    finally:
        if configuration_file and os.path.exists(configuration_file):
            os.remove(configuration_file)


def test_scan_for_unused_original_not_clean_with_verbose():
    """
    Test to make sure that scanning a file that is not originally clean will result
    in an error right away.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    file_to_scan = "test/resources/balanced_file.py"
    supplied_arguments = [
        "--verbose",
        "--scan",
        file_to_scan,
    ]

    expected_return_code = 1
    expected_output = """Scanning file: {file}
  File contains 0 scan errors.
Verifying {file} scans cleanly without modifications.
  Baseline PyLint scan found unsuppressed warnings: missing-module-docstring
  Fix all errors before scanning again.

No unused PyLint suppressions found.
""".replace(
        "{file}", file_to_scan
    )
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_for_unused_original_not_clean_with_config():
    """
    Test to make sure that scanning a file that is not originally clean, but
    clean with applied configuration, will result in a clean parsing.
    """

    # Arrange
    configuration_file = None
    warning_to_suppress = "missing-module-docstring"
    try:
        configuration_file = write_temporary_configuration(warning_to_suppress)
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/balanced_file.py"
        supplied_arguments = [
            "--config",
            configuration_file,
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 0
        expected_output = """Verifying {file} scans cleanly without modifications.

No unused PyLint suppressions found.
""".replace(
            "{file}", file_to_scan
        )
        expected_error = ""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )
    finally:
        if configuration_file and os.path.exists(configuration_file):
            os.remove(configuration_file)


def test_scan_for_unused_original_not_clean_with_bad_config():
    """
    Test to make sure that scanning a file that is not originally clean,
    with a bad configuration file, will result in a clean parsing.
    """

    # Arrange
    configuration_file = "test/resources/README.md"
    scanner = ProxyPyLintUtils()
    file_to_scan = "test/resources/balanced_file.py"
    supplied_arguments = [
        "--config",
        configuration_file,
        "--scan",
        file_to_scan,
    ]

    expected_return_code = 1
    expected_output = ""
    expected_stdout_parts = [
        f"""Verifying {file_to_scan} scans cleanly without modifications.
  Baseline PyLint scan found reported error output:""",
        """Fix all errors before scanning again.

No unused PyLint suppressions found.
""",
    ]
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output,
        expected_error,
        expected_return_code,
        output_parts=expected_stdout_parts,
    )


def test_scan_for_unused_original_clean():
    """
    Test to make sure that scanning a file that is clean will result in nothing being found.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    file_to_scan = "test/resources/balanced_file_clean.py"
    supplied_arguments = [
        "--scan",
        file_to_scan,
    ]

    expected_return_code = 0
    expected_output = """Verifying {file} scans cleanly without modifications.

No unused PyLint suppressions found.
""".replace(
        "{file}", file_to_scan
    )
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_for_unused_original_clean_with_verbose():
    """
    Test to make sure that scanning a file that is clean will result in nothing being found.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    file_to_scan = "test/resources/balanced_file_clean.py"
    supplied_arguments = [
        "--verbose",
        "--scan",
        file_to_scan,
    ]

    expected_return_code = 0
    expected_output = """ Scanning file: test/resources/balanced_file_clean.py
  File contains 0 scan errors.
Verifying {file} scans cleanly without modifications.
  Verifying suppression 'too-many-arguments' from file test/resources/balanced_file_clean.py, line 6

No unused PyLint suppressions found.
""".replace(
        "{file}", file_to_scan
    )
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_for_unused_original_clean_with_display():
    """
    Test to make sure that scanning a file that is clean will result in nothing being found.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    file_to_scan = "test/resources/balanced_file_clean.py"
    supplied_arguments = [
        "--x-display",
        "--scan",
        file_to_scan,
    ]

    expected_return_code = 0
    expected_output = """Verifying {file} scans cleanly without modifications.
  .\bv

No unused PyLint suppressions found.
""".replace(
        "{file}", file_to_scan
    )
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_for_unused_original_clean_with_extra_suppression_first():
    """
    Test to make sure that scanning a file that is pylint clean with an extra
    suppression noted first in the suppress line will report and extra suppression.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    file_to_scan = "test/resources/balanced_file_clean_with_extra_first.py"
    supplied_arguments = [
        "--scan",
        file_to_scan,
    ]

    expected_return_code = 2
    expected_output = """Verifying {file} scans cleanly without modifications.

1 unused PyLint suppressions found.
{file}:6: Unused suppression: too-many-branches
""".replace(
        "{file}", file_to_scan
    )
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_for_unused_original_clean_with_extra_suppression_first_with_verbose():
    """
    Test to make sure that scanning a file that is pylint clean with an extra
    suppression noted first in the suppress line will report and extra suppression.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    file_to_scan = "test/resources/balanced_file_clean_with_extra_first.py"
    supplied_arguments = [
        "--verbose",
        "--scan",
        file_to_scan,
    ]

    expected_return_code = 2
    expected_output = """Scanning file: {file}
  File contains 0 scan errors.
Verifying {file} scans cleanly without modifications.
  Verifying suppression 'too-many-branches' from file test/resources/balanced_file_clean_with_extra_first.py, line 6
  Verifying suppression 'too-many-arguments' from file test/resources/balanced_file_clean_with_extra_first.py, line 6

1 unused PyLint suppressions found.
{file}:6: Unused suppression: too-many-branches
""".replace(
        "{file}", file_to_scan
    )
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_for_unused_original_clean_with_extra_suppression_last():
    """
    Test to make sure that scanning a file that is pylint clean with an extra
    suppression noted last in the suppress line will report and extra suppression.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    file_to_scan = "test/resources/balanced_file_clean_with_extra_last.py"
    supplied_arguments = [
        "--scan",
        file_to_scan,
    ]

    expected_return_code = 2
    expected_output = """Verifying {file} scans cleanly without modifications.

1 unused PyLint suppressions found.
{file}:6: Unused suppression: too-many-branches
""".replace(
        "{file}", file_to_scan
    )
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_for_unused_original_clean_with_extra_suppression_last_with_verbose():
    """
    Test to make sure that scanning a file that is pylint clean with an extra
    suppression noted last in the suppress line will report and extra suppression.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    file_to_scan = "test/resources/balanced_file_clean_with_extra_last.py"
    supplied_arguments = [
        "--verbose",
        "--scan",
        file_to_scan,
    ]

    expected_return_code = 2
    expected_output = """Scanning file: {file}
  File contains 0 scan errors.
Verifying {file} scans cleanly without modifications.
  Verifying suppression 'too-many-arguments' from file test/resources/balanced_file_clean_with_extra_last.py, line 6
  Verifying suppression 'too-many-branches' from file test/resources/balanced_file_clean_with_extra_last.py, line 6

1 unused PyLint suppressions found.
{file}:6: Unused suppression: too-many-branches
""".replace(
        "{file}", file_to_scan
    )
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_for_unused_clean():
    """
    Test to make sure that scanning a file that is has not pylint suppressions.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    file_to_scan = "test/resources/clean_file.py"
    supplied_arguments = [
        "--scan",
        file_to_scan,
    ]

    expected_return_code = 0
    expected_output = """No unused PyLint suppressions found.""".replace(
        "{file}", file_to_scan
    )
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_for_unused_clean_with_verbose():
    """
    Test to make sure that scanning a file that is has not pylint suppressions.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    file_to_scan = "test/resources/clean_file.py"
    supplied_arguments = [
        "--verbose",
        "--scan",
        file_to_scan,
    ]

    expected_return_code = 0
    expected_output = """Scanning file: {file}
  File contains 0 scan errors.
File {file} does not contain any PyLint suppressions.

No unused PyLint suppressions found.""".replace(
        "{file}", file_to_scan
    )
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_for_unused_with_bad_scan_file_open():
    """
    Test to make sure that scanning a file that fails when the new scan file
    is opened is captured properly.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    file_to_scan = "test/resources/balanced_file_clean.py"
    supplied_arguments = [
        "--verbose",
        "--scan",
        file_to_scan,
    ]

    test_file_to_scan_path = (
        f"{os.path.dirname(file_to_scan)}/__{os.path.basename(file_to_scan)}"
    )
    mock_exception_message = "bob"

    expected_return_code = 1
    expected_output = """Scanning file: {file}
  File contains 0 scan errors.
Verifying {file} scans cleanly without modifications.
  Verifying suppression 'too-many-arguments' from file {file}, line 6
    Modified file scan of {file} failed during creation: {error}

No unused PyLint suppressions found.
""".replace(
        "{file}", file_to_scan
    ).replace(
        "{error}", mock_exception_message
    )
    expected_error = ""

    # Act
    try:
        pbo = PatchBuiltinOpen()
        pbo.register_exception(
            test_file_to_scan_path, "wt", exception_message=mock_exception_message
        )
        pbo.start()

        execute_results = scanner.invoke_main(arguments=supplied_arguments)
    finally:
        pbo.stop()

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scan_for_unused_with_bad_scan_file_open_and_display():
    """
    Test to make sure that scanning a file that fails when the new scan file
    is opened is captured properly, with the display mode turned on.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    file_to_scan = "test/resources/balanced_file_clean.py"
    supplied_arguments = [
        "--x-display",
        "--scan",
        file_to_scan,
    ]

    test_file_to_scan_path = (
        f"{os.path.dirname(file_to_scan)}/__{os.path.basename(file_to_scan)}"
    )
    mock_exception_message = "bob"

    expected_return_code = 1
    expected_output = """Verifying {file} scans cleanly without modifications.
  .\b    Modified file scan of {file} failed during creation: bob


No unused PyLint suppressions found.
""".replace(
        "{file}", file_to_scan
    ).replace(
        "{error}", mock_exception_message
    )
    expected_error = ""

    # Act
    try:
        pbo = PatchBuiltinOpen()
        pbo.register_exception(
            test_file_to_scan_path, "wt", exception_message=mock_exception_message
        )
        pbo.start()

        execute_results = scanner.invoke_main(arguments=supplied_arguments)
    finally:
        pbo.stop()

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


class PatchSubprocessPopen:
    """
    Patch for a subprocess call to mock out the response.
    """

    def __init__(self):
        self.mock_patcher = None
        self.patched_open = None

    def start(self):
        """
        Start the patching of the "open" function.
        """
        self.mock_patcher = unittest.mock.patch("subprocess.Popen")
        self.patched_open = self.mock_patcher.start()
        self.patched_open.side_effect = self.my_popen

    def stop(self):
        """
        Stop the patching of the "open" function.
        """
        self.mock_patcher.stop()
        self.mock_patcher = None

    # pylint: disable=consider-using-with
    def my_popen(self, *args, **kwargs):
        """
        Mock out the opening of another process.
        """

        popen_commands = args[0]
        rt_index = popen_commands.index("-r")
        file_name = popen_commands[rt_index + 2]
        if os.path.basename(file_name).startswith("__"):
            raise IOError("goober")
        try:
            self.mock_patcher.stop()

            return subprocess.Popen(
                *args,
                **kwargs,
            )
        finally:
            self.patched_open = self.mock_patcher.start()
            self.patched_open.side_effect = self.my_popen

    # pylint: enable=consider-using-with


def test_scan_for_unused_with_bad_scan_subprocess_popen_and_display():
    """
    Test to make sure that...
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    file_to_scan = "test/resources/balanced_file_clean.py"
    supplied_arguments = [
        "--scan",
        file_to_scan,
    ]

    mock_exception_message = "bob"

    expected_return_code = 1
    expected_output = """Verifying {file} scans cleanly without modifications.
Pylint returned exception:goober
    Modified file scan of test/resources/balanced_file_clean.py failed: Fatal Error

No unused PyLint suppressions found.
""".replace(
        "{file}", file_to_scan
    ).replace(
        "{error}", mock_exception_message
    )
    expected_error = ""

    # Act
    try:
        pbo = PatchSubprocessPopen()
        pbo.start()

        execute_results = scanner.invoke_main(arguments=supplied_arguments)

    finally:
        pbo.stop()

    # Assert
    # assert mock_subproc_popen.called

    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
